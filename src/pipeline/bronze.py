# Bronze: land every source as-delivered with Auto Loader. Partner files keep their native formats;
# everything is read as strings here so malformed values survive to be judged by silver expectations.
import dlt
from pyspark.sql import functions as F
from pyspark.sql import types as T

CATALOG = spark.conf.get("apex.catalog", "apex_recon")
RAW = f"/Volumes/{CATALOG}/landing/raw"


def strings(*cols):
    return T.StructType([T.StructField(c, T.StringType()) for c in cols])


def autoload(path, fmt, schema, **opts):
    reader = spark.readStream.format("cloudFiles").option("cloudFiles.format", fmt).schema(schema)
    for k, v in opts.items():
        reader = reader.option(k, v)
    return (reader.load(path)
            .withColumn("_source_file", F.col("_metadata.file_path"))
            .withColumn("_file_modified_at", F.col("_metadata.file_modification_time"))
            .withColumn("_ingested_at", F.current_timestamp()))


SSP_SCHEMA = T.StructType([
    T.StructField("event_hour_utc", T.StringType()),
    T.StructField("deal_id", T.StringType()),
    T.StructField("dsp_id", T.StringType()),
    T.StructField("seat_id", T.StringType()),
    T.StructField("publisher_id", T.StringType()),
    T.StructField("impressions", T.LongType()),
    T.StructField("gross_revenue_usd", T.DoubleType()),
    T.StructField("log_source", T.StringType()),
])


@dlt.table(name=f"{CATALOG}.bronze.ssp_auction_logs",
           comment="Apex Exchange auction-service logs: one row per deal per UTC hour (system of record). Source: ssp_logs/*.json.gz")
def ssp_auction_logs():
    return autoload(f"{RAW}/ssp_logs/", "json", SSP_SCHEMA)


# Each DSP delivers billing reports in one of three layouts. Route files by DSP using the partner reference list.
_formats = {}
for r in spark.read.option("header", True).csv(f"{RAW}/reference/dsps.csv").collect():
    _formats.setdefault(r.report_format, []).append(r.dsp_id)

DSP_LAYOUTS = {
    "a": ("A", strings("report_date", "deal_id", "impressions", "spend_usd"),
          "Layout A: report_date (yyyy-MM-dd), deal_id, impressions, spend_usd"),
    "b": ("B", strings("report_date", "deal_id", "impressions", "media_cost", "currency"),
          "Layout B: Date (MM/dd/yyyy), Deal ID, Imps, Media Cost, Currency (USD/EUR/GBP)"),
    "c": ("C", strings("report_day", "seat_id", "deal_code", "impressions_served", "gross_spend"),
          "Layout C: day (yyyyMMdd), seat_id, DSP-side deal_code, impressions_served, gross_spend (USD)"),
}


def dsp_bronze(suffix, fmt, schema, desc):
    ids = ",".join(sorted(_formats.get(fmt, [])))

    @dlt.table(name=f"{CATALOG}.bronze.dsp_reports_format_{suffix}",
               comment=f"DSP billing reports as delivered. {desc}. Raw strings; parsed in silver.")
    def _t():
        return (autoload(f"{RAW}/dsp_reports/{{{ids}}}/", "csv", schema, header="true")
                .withColumn("dsp_id", F.regexp_extract("_source_file", r"dsp_reports/(DSP\d+)/", 1)))


for suffix, (fmt, schema, desc) in DSP_LAYOUTS.items():
    dsp_bronze(suffix, fmt, schema, desc)


@dlt.table(name=f"{CATALOG}.bronze.publisher_adserver_reports",
           comment="Publisher ad server exports (FreeWheel / Google Ad Manager / SpringServe style), one file per publisher per month.")
def publisher_adserver_reports():
    schema = strings("report_date", "ad_unit", "deal_id", "adserver_impressions", "estimated_revenue_usd")
    return (autoload(f"{RAW}/publisher_reports/", "csv", schema, header="true")
            .withColumn("publisher_id", F.regexp_extract("_source_file", r"publisher_reports/(P\d+)/", 1)))


@dlt.table(name=f"{CATALOG}.bronze.dispute_resolutions",
           comment="Historical (Jan-Jun 2026) dispute cases as resolved by Billing Ops analysts. Source of ML training labels.")
def dispute_resolutions():
    schema = strings("case_id", "dsp_id", "deal_id", "billing_month", "ssp_impressions", "dsp_impressions",
                     "ssp_revenue_usd", "dsp_revenue_usd", "revenue_gap_usd", "revenue_gap_pct", "resolved_root_cause",
                     "resolution_outcome", "recovered_usd", "days_to_resolve", "resolved_by")
    return autoload(f"{RAW}/history/", "csv", schema, header="true")
