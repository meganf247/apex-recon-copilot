# Silver: one normalized shape per source. DSP reports from three layouts become a single table with
# canonical deal IDs, real dates and USD amounts; rows that fail data-quality rules are dropped from
# silver and kept, with the reason, in a quarantine table for Billing Ops to chase with the partner.
import dlt
from pyspark.sql import Window
from pyspark.sql import functions as F

CATALOG = spark.conf.get("apex.catalog", "apex_recon")
RAW = f"/Volumes/{CATALOG}/landing/raw"
B, S = f"{CATALOG}.bronze", f"{CATALOG}.silver"


def ref_csv(name):
    return spark.read.option("header", True).option("inferSchema", True).csv(f"{RAW}/reference/{name}.csv")


# ---------- reference dimensions ----------

@dlt.table(name=f"{S}.dim_dsps", comment="Demand-side platforms buying Apex CTV inventory, with partner team ownership.")
def dim_dsps():
    return ref_csv("dsps").join(ref_csv("dsp_contracts"), "dsp_id")


@dlt.table(name=f"{S}.dim_publishers", comment="CTV publishers (streaming services, FAST channels, device platforms) and their contract terms.")
def dim_publishers():
    return ref_csv("publishers").join(ref_csv("publisher_contracts"), "publisher_id")


@dlt.table(name=f"{S}.dim_deals", comment="Programmatic CTV deals (PG / PMP / open) with content genre, live flag and device type.")
def dim_deals():
    return (ref_csv("deals")
            .withColumn("flight_start", F.to_date("flight_start"))
            .withColumn("flight_end", F.to_date("flight_end")))


@dlt.table(name=f"{S}.fx_rates", comment="Daily FX reference rates (USD per unit of EUR / GBP).")
def fx_rates():
    return ref_csv("fx_rates").withColumn("rate_date", F.to_date("rate_date"))


# ---------- SSP system of record ----------

@dlt.table(name=f"{S}.ssp_hourly", comment="Apex auction logs, typed: impressions and gross revenue per deal per UTC hour.")
@dlt.expect_or_drop("valid_impressions", "impressions >= 0")
@dlt.expect_or_drop("has_deal", "deal_id IS NOT NULL")
def ssp_hourly():
    return (spark.readStream.table(f"{B}.ssp_auction_logs")
            .withColumn("event_hour_utc", F.to_timestamp("event_hour_utc"))
            .withColumn("event_date_utc", F.to_date("event_hour_utc"))
            .select("event_hour_utc", "event_date_utc", "deal_id", "dsp_id", "seat_id", "publisher_id",
                    "impressions", "gross_revenue_usd", "_source_file"))


# ---------- DSP billing reports: three layouts -> one ----------

def _try_date(col, fmt):
    return F.expr(f"try_to_timestamp({col}, '{fmt}')").cast("date")


def _try_num(col, typ):
    return F.expr(f"try_cast({col} AS {typ})")


DSP_RULES = {
    "valid_report_date": "report_date IS NOT NULL",
    "known_deal": "deal_id IS NOT NULL",
    "non_negative_impressions": "impressions >= 0",
    "valid_amount": "amount_native IS NOT NULL",
    "seat_matches_partner": "seat_ok",
    "not_duplicate": "NOT is_duplicate",
}


@dlt.view(name="dsp_reports_normalized", comment="All DSP layouts mapped to one schema, before data-quality rules.")
def dsp_reports_normalized():
    deals = spark.read.table(f"{S}.dim_deals").select("deal_id", "dsp_deal_code")
    seats = spark.read.table(f"{S}.dim_dsps").select("dsp_id", F.col("seat_id").alias("partner_seat_id"))
    a = (spark.read.table(f"{B}.dsp_reports_format_a")
         .select("dsp_id", _try_date("report_date", "yyyy-MM-dd").alias("report_date"), "deal_id",
                 _try_num("impressions", "BIGINT").alias("impressions"),
                 _try_num("spend_usd", "DOUBLE").alias("amount_native"),
                 F.lit("USD").alias("currency"), F.lit(True).alias("seat_ok"), F.lit("A").alias("source_format"),
                 "_source_file"))
    b = (spark.read.table(f"{B}.dsp_reports_format_b")
         .select("dsp_id", _try_date("report_date", "MM/dd/yyyy").alias("report_date"), "deal_id",
                 _try_num("impressions", "BIGINT").alias("impressions"),
                 _try_num("media_cost", "DOUBLE").alias("amount_native"),
                 "currency", F.lit(True).alias("seat_ok"), F.lit("B").alias("source_format"), "_source_file"))
    c = (spark.read.table(f"{B}.dsp_reports_format_c")
         .join(deals, F.col("deal_code") == F.col("dsp_deal_code"), "left")
         .join(seats, "dsp_id", "left")
         .select("dsp_id", _try_date("report_day", "yyyyMMdd").alias("report_date"), "deal_id",
                 _try_num("impressions_served", "BIGINT").alias("impressions"),
                 _try_num("gross_spend", "DOUBLE").alias("amount_native"),
                 F.lit("USD").alias("currency"), (F.col("seat_id") == F.col("partner_seat_id")).alias("seat_ok"),
                 F.lit("C").alias("source_format"), "_source_file"))
    rows = a.unionByName(b).unionByName(c).withColumn("seat_ok", F.coalesce("seat_ok", F.lit(False)))
    dup_key = ["_source_file", "report_date", "deal_id", "impressions", "amount_native"]
    rows = rows.withColumn("is_duplicate", F.row_number().over(Window.partitionBy(*dup_key).orderBy(F.lit(1))) > 1)
    fx = spark.read.table(f"{S}.fx_rates").select(F.col("rate_date").alias("report_date"), "currency", "usd_per_unit")
    return (rows.join(fx, ["report_date", "currency"], "left")
            .withColumn("amount_usd", F.round(F.col("amount_native") * F.coalesce("usd_per_unit", F.lit(1.0)), 4)))


@dlt.table(name=f"{S}.dsp_daily_reports",
           comment="DSP-reported impressions and spend per deal per reported day, normalized to canonical deal_id and USD. "
                   "Report dates are as labelled by the partner (contractually UTC).")
@dlt.expect_all_or_drop(DSP_RULES)
def dsp_daily_reports():
    return dlt.read("dsp_reports_normalized").drop("usd_per_unit")


@dlt.table(name=f"{S}.dsp_reports_quarantine",
           comment="DSP report rows rejected by data-quality rules, with every failed rule listed, for partner follow-up.")
def dsp_reports_quarantine():
    df = dlt.read("dsp_reports_normalized")
    failed = F.array_compact(F.array(*[F.when(~F.coalesce(F.expr(cond), F.lit(False)), F.lit(name))
                                       for name, cond in DSP_RULES.items()]))
    return df.withColumn("failed_rules", failed).where(F.size("failed_rules") > 0).drop("usd_per_unit")


# ---------- publisher ad server exports ----------

@dlt.table(name=f"{S}.publisher_daily_reports",
           comment="Publisher ad server impressions and estimated payout per deal per publisher-local day.")
@dlt.expect_or_drop("valid_report_date", "report_date IS NOT NULL")
@dlt.expect_or_drop("non_negative_impressions", "adserver_impressions >= 0")
def publisher_daily_reports():
    return (spark.read.table(f"{B}.publisher_adserver_reports")
            .select("publisher_id", "deal_id", "ad_unit",
                    _try_date("report_date", "yyyy-MM-dd").alias("report_date"),
                    _try_num("adserver_impressions", "BIGINT").alias("adserver_impressions"),
                    _try_num("estimated_revenue_usd", "DOUBLE").alias("estimated_revenue_usd"),
                    "_source_file"))


@dlt.table(name=f"{S}.dispute_history", comment="Resolved Jan-Jun dispute cases, typed. resolved_root_cause is the ML label.")
@dlt.expect_or_drop("has_label", "resolved_root_cause IS NOT NULL")
def dispute_history():
    nums = ["ssp_impressions", "dsp_impressions", "ssp_revenue_usd", "dsp_revenue_usd", "revenue_gap_usd",
            "revenue_gap_pct", "recovered_usd"]
    df = spark.read.table(f"{B}.dispute_resolutions")
    for c in nums:
        df = df.withColumn(c, _try_num(c, "DOUBLE"))
    return df.withColumn("days_to_resolve", _try_num("days_to_resolve", "INT")).drop("_file_modified_at", "_ingested_at")
