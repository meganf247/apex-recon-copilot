# Apex Exchange reconciliation pipeline: bronze -> silver -> gold.
#
#   bronze.ssp_logs ────► silver.ssp_daily ──┐
#                                            ├─► gold.recon_deal_month ──► gold.recon_partner_month
#   bronze.dsp_reports ─► silver.dsp_daily ──┘   joins: SSP ⋈ DSP, + silver.deals, + silver.dsps
#
# silver.deals and silver.dsps are reference tables written by the generator.
# Both gold tables carry the same row filter and revenue masks as the work queue (functions in src/00_setup_uc.sql),
# so a partner manager can't read around the governed queue through the reconciliation tables or Genie.
import dlt
from pyspark.sql import Window
from pyspark.sql import functions as F

CATALOG = spark.conf.get("apex.catalog", "apex_recon")
RAW = f"/Volumes/{CATALOG}/landing/raw"
LARGE_DAILY_GAP_PCT = 7.5
ROW_FILTER = f"ROW FILTER {CATALOG}.ops.partner_access_filter ON (partner_team)"
USD = f"DOUBLE MASK {CATALOG}.ops.finance_only_usd"


def columns(schema):
    return [c.strip().split(" ")[0] for c in schema.split(",")]


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

DEAL_MONTH_SCHEMA = f"""dsp_id STRING, deal_id STRING, billing_month STRING, ssp_impressions BIGINT, dsp_impressions BIGINT,
  ssp_revenue_usd {USD}, dsp_revenue_usd {USD}, days_delivered BIGINT, days_missing_in_dsp_report BIGINT,
  days_with_large_gap BIGINT, publisher_name STRING, deal_name STRING, deal_type STRING, content_genre STRING,
  is_live BOOLEAN, ivt_risk_score DOUBLE, apex_take_rate_pct DOUBLE, publisher_paid_on STRING, dsp_name STRING,
  partner_team STRING, discrepancy_threshold_pct DOUBLE, billing_count_basis STRING, payment_terms_days BIGINT,
  impression_gap_pct DOUBLE, revenue_gap_usd {USD}, revenue_gap_pct DOUBLE, large_gap_day_share DOUBLE,
  over_threshold BOOLEAN, needs_review BOOLEAN, billing_shortfall_usd {USD}, revenue_at_risk_usd {USD},
  apex_net_revenue_usd {USD}, apex_exposure_usd {USD}"""


@dlt.table(name=f"{CATALOG}.gold.recon_deal_month",
           comment="Monthly reconciliation per CTV deal (the unit of a dispute). Positive gap = DSP reported less than Apex. "
                   "needs_review = monthly gap over the DSP's contract threshold, or >=30% of days with a daily gap over 7.5%. "
                   "billing_shortfall_usd = positive gap on every deal; revenue_at_risk_usd = shortfall on deals that need "
                   "review (0 otherwise); apex_exposure_usd = the part of revenue at risk that hits Apex's own P&L: all of it "
                   "if the publisher is paid on Apex's count, only Apex's take rate if the publisher is paid on cleared revenue.",
           schema=DEAL_MONTH_SCHEMA, row_filter=ROW_FILTER)
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
            .withColumn("large_gap_day_share", F.round(F.col("days_with_large_gap") / F.col("days_delivered"), 3))
            .withColumn("over_threshold", F.abs("revenue_gap_pct") > F.col("discrepancy_threshold_pct"))
            .withColumn("needs_review", F.col("over_threshold") | (F.col("large_gap_day_share") >= 0.3))
            .withColumn("billing_shortfall_usd", F.greatest("revenue_gap_usd", F.lit(0.0)))
            .withColumn("revenue_at_risk_usd", F.when(F.col("needs_review"), F.col("billing_shortfall_usd")).otherwise(0.0))
            .withColumn("apex_net_revenue_usd", F.round(F.col("ssp_revenue_usd") * F.col("apex_take_rate_pct") / 100, 2))
            .withColumn("apex_exposure_usd", F.round(F.col("revenue_at_risk_usd") * F.when(
                F.col("publisher_paid_on") == "APEX_COUNT", 1.0).otherwise(F.col("apex_take_rate_pct") / 100), 2))
            .select(*columns(DEAL_MONTH_SCHEMA)))


PARTNER_MONTH_SCHEMA = f"""dsp_id STRING, dsp_name STRING, partner_team STRING, billing_month STRING,
  discrepancy_threshold_pct DOUBLE, active_deals BIGINT, deals_needing_review BIGINT, ssp_revenue_usd {USD},
  dsp_revenue_usd {USD}, billing_shortfall_usd {USD}, revenue_at_risk_usd {USD}, apex_net_revenue_usd {USD},
  apex_exposure_usd {USD}, revenue_gap_pct DOUBLE, over_threshold BOOLEAN"""


@dlt.table(name=f"{CATALOG}.gold.recon_partner_month",
           comment="Monthly reconciliation per DSP: totals, gap, deals needing review, billing shortfall (all deals), "
                   "revenue at risk (deals needing review) and Apex's own exposure.",
           schema=PARTNER_MONTH_SCHEMA, row_filter=ROW_FILTER)
def recon_partner_month():
    return (spark.read.table(f"{CATALOG}.gold.recon_deal_month")
            .groupBy("dsp_id", "dsp_name", "partner_team", "billing_month", "discrepancy_threshold_pct")
            .agg(F.count("*").alias("active_deals"),
                 F.sum(F.col("needs_review").cast("int")).alias("deals_needing_review"),
                 F.round(F.sum("ssp_revenue_usd"), 2).alias("ssp_revenue_usd"),
                 F.round(F.sum("dsp_revenue_usd"), 2).alias("dsp_revenue_usd"),
                 F.round(F.sum("billing_shortfall_usd"), 2).alias("billing_shortfall_usd"),
                 F.round(F.sum("revenue_at_risk_usd"), 2).alias("revenue_at_risk_usd"),
                 F.round(F.sum("apex_net_revenue_usd"), 2).alias("apex_net_revenue_usd"),
                 F.round(F.sum("apex_exposure_usd"), 2).alias("apex_exposure_usd"))
            .withColumn("revenue_gap_pct", gap_pct("ssp_revenue_usd", "dsp_revenue_usd"))
            .withColumn("over_threshold", F.abs("revenue_gap_pct") > F.col("discrepancy_threshold_pct"))
            .select(*columns(PARTNER_MONTH_SCHEMA)))
