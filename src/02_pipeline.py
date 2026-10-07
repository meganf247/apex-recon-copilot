# Apex Exchange reconciliation pipeline: bronze -> silver -> gold.
#
#   bronze.ssp_logs ────► silver.ssp_daily ──┐
#                                            ├─► gold.recon_deal_month ──► gold.recon_partner_month
#   bronze.dsp_reports ─► silver.dsp_daily ──┘   joins: SSP ⋈ DSP, + silver.deals, + silver.dsps
#
# silver.deals and silver.dsps are reference tables written by the generator.
import dlt
from pyspark.sql import Window
from pyspark.sql import functions as F

CATALOG = spark.conf.get("apex.catalog", "apex_recon")
RAW = f"/Volumes/{CATALOG}/landing/raw"
LARGE_DAILY_GAP_PCT = 7.5


def autoload(path, fmt, schema, **opts):
    reader = spark.readStream.format("cloudFiles").option("cloudFiles.format", fmt).schema(schema)
    for k, v in opts.items():
        reader = reader.option(k, v)
    return reader.load(path).withColumn("_source_file", F.col("_metadata.file_path"))


def gap_pct(apex, partner):
    return F.round(F.when(F.col(apex) > 0, 100 * (F.col(apex) - F.col(partner)) / F.col(apex)), 2)


# ---------- bronze: files as delivered ----------

@dlt.table(name=f"{CATALOG}.bronze.ssp_logs",
           comment="Apex auction logs as delivered: impressions and revenue per deal per UTC hour.")
def ssp_logs():
    return autoload(f"{RAW}/ssp_logs/", "json",
                    "event_hour_utc STRING, deal_id STRING, dsp_id STRING, impressions BIGINT, gross_revenue_usd DOUBLE")


@dlt.table(name=f"{CATALOG}.bronze.dsp_reports",
           comment="DSP billing reports as delivered (all columns as text, so bad values reach the silver quality rules).")
def dsp_reports():
    return (autoload(f"{RAW}/dsp_reports/", "csv", "report_date STRING, deal_id STRING, impressions STRING, spend_usd STRING",
                     header="true")
            .withColumn("dsp_id", F.regexp_extract("_source_file", r"dsp_reports/(DSP\d+)/", 1)))


# ---------- silver: clean, typed, one row per deal per day ----------

@dlt.table(name=f"{CATALOG}.silver.ssp_daily", comment="Apex's count per deal per day (UTC).")
def ssp_daily():
    return (spark.read.table(f"{CATALOG}.bronze.ssp_logs")
            .groupBy("deal_id", "dsp_id", F.to_date("event_hour_utc").alias("report_date"))
            .agg(F.sum("impressions").alias("ssp_impressions"), F.sum("gross_revenue_usd").alias("ssp_revenue_usd")))


@dlt.table(name=f"{CATALOG}.silver.dsp_daily",
           comment="Each DSP's count per deal per day. Rows with no deal ID, a bad date, negative impressions or "
                   "an exact duplicate are dropped; the pipeline records how many each rule caught.")
@dlt.expect_or_drop("has_deal_id", "deal_id IS NOT NULL")
@dlt.expect_or_drop("valid_date", "report_date IS NOT NULL")
@dlt.expect_or_drop("non_negative_impressions", "dsp_impressions >= 0")
@dlt.expect_or_drop("not_duplicate", "copy_number = 1")
def dsp_daily():
    rows = spark.read.table(f"{CATALOG}.bronze.dsp_reports").select(
        "dsp_id", "deal_id",
        F.expr("try_to_timestamp(report_date, 'yyyy-MM-dd')").cast("date").alias("report_date"),
        F.expr("try_cast(impressions AS BIGINT)").alias("dsp_impressions"),
        F.expr("try_cast(spend_usd AS DOUBLE)").alias("dsp_revenue_usd"),
        "_source_file")
    copies = Window.partitionBy("_source_file", "deal_id", "report_date", "dsp_impressions", "dsp_revenue_usd").orderBy(F.lit(1))
    return rows.withColumn("copy_number", F.row_number().over(copies))


# ---------- gold: the reconciliation ----------

@dlt.table(name=f"{CATALOG}.gold.recon_deal_month",
           comment="Monthly reconciliation per CTV deal (the unit of a dispute). Positive gap = DSP reported less than Apex. "
                   "needs_review = monthly gap over the DSP's contract threshold, or >=30% of days with a daily gap over 7.5%.")
def recon_deal_month():
    ssp = spark.read.table(f"{CATALOG}.silver.ssp_daily")
    dsp = spark.read.table(f"{CATALOG}.silver.dsp_daily").select("deal_id", "report_date", "dsp_impressions", "dsp_revenue_usd")
    daily = (ssp.join(dsp, ["deal_id", "report_date"], "left")                                    # join 1
             .withColumn("missing_in_dsp_report", F.col("dsp_impressions").isNull())
             .withColumn("daily_gap_pct", gap_pct("ssp_impressions", "dsp_impressions")))
    month = (daily.groupBy("deal_id", F.date_format("report_date", "yyyy-MM").alias("billing_month"))
             .agg(F.sum("ssp_impressions").alias("ssp_impressions"),
                  F.coalesce(F.sum("dsp_impressions"), F.lit(0)).alias("dsp_impressions"),
                  F.round(F.sum("ssp_revenue_usd"), 2).alias("ssp_revenue_usd"),
                  F.round(F.coalesce(F.sum("dsp_revenue_usd"), F.lit(0.0)), 2).alias("dsp_revenue_usd"),
                  F.count("*").alias("days_delivered"),
                  F.sum(F.col("missing_in_dsp_report").cast("int")).alias("days_missing_in_dsp_report"),
                  F.sum((F.abs("daily_gap_pct") > LARGE_DAILY_GAP_PCT).cast("int")).alias("days_with_large_gap")))
    deals = spark.read.table(f"{CATALOG}.silver.deals")
    dsps = spark.read.table(f"{CATALOG}.silver.dsps")
    return (month.join(deals, "deal_id")                                                             # join 2
            .join(dsps, "dsp_id")                                                                     # join 3
            .withColumn("impression_gap_pct", gap_pct("ssp_impressions", "dsp_impressions"))
            .withColumn("revenue_gap_usd", F.round(F.col("ssp_revenue_usd") - F.col("dsp_revenue_usd"), 2))
            .withColumn("revenue_gap_pct", gap_pct("ssp_revenue_usd", "dsp_revenue_usd"))
            .withColumn("revenue_at_risk_usd", F.greatest("revenue_gap_usd", F.lit(0.0)))
            .withColumn("large_gap_day_share", F.round(F.col("days_with_large_gap") / F.col("days_delivered"), 3))
            .withColumn("over_threshold", F.abs("revenue_gap_pct") > F.col("discrepancy_threshold_pct"))
            .withColumn("needs_review", F.col("over_threshold") | (F.col("large_gap_day_share") >= 0.3)))


@dlt.table(name=f"{CATALOG}.gold.recon_partner_month",
           comment="Monthly reconciliation per DSP: totals, gap, deals needing review and revenue at risk.")
def recon_partner_month():
    return (spark.read.table(f"{CATALOG}.gold.recon_deal_month")
            .groupBy("dsp_id", "dsp_name", "partner_team", "billing_month", "discrepancy_threshold_pct")
            .agg(F.count("*").alias("active_deals"),
                 F.sum(F.col("needs_review").cast("int")).alias("deals_needing_review"),
                 F.round(F.sum("ssp_revenue_usd"), 2).alias("ssp_revenue_usd"),
                 F.round(F.sum("dsp_revenue_usd"), 2).alias("dsp_revenue_usd"),
                 F.round(F.sum("revenue_at_risk_usd"), 2).alias("revenue_at_risk_usd"))
            .withColumn("revenue_gap_pct", gap_pct("ssp_revenue_usd", "dsp_revenue_usd"))
            .withColumn("over_threshold", F.abs("revenue_gap_pct") > F.col("discrepancy_threshold_pct")))
