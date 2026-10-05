# Gold: the reconciliation itself. SSP (system of record) vs DSP (who pays Apex) vs publisher (whom Apex pays),
# at deal-day, deal-month and partner-month grain, plus the ML feature set that explains each discrepancy.
import dlt
from pyspark.sql import Window
from pyspark.sql import functions as F

CATALOG = spark.conf.get("apex.catalog", "apex_recon")
S, G, M = f"{CATALOG}.silver", f"{CATALOG}.gold", f"{CATALOG}.ml"
LARGE_DAILY_GAP_PCT = 7.5


def pct_gap(ssp, other):
    return F.round(F.when(F.col(ssp) > 0, 100 * (F.col(ssp) - F.col(other)) / F.col(ssp)), 3)


@dlt.table(name=f"{G}.recon_deal_daily",
           comment="SSP vs DSP impressions and revenue per deal per day. Positive gap = DSP reports less than Apex. "
                   "dsp_row_missing = Apex delivered but the DSP report has no row for that day.")
def recon_deal_daily():
    ssp = (spark.read.table(f"{S}.ssp_hourly")
           .groupBy("deal_id", "dsp_id", F.col("event_date_utc").alias("recon_date"))
           .agg(F.sum("impressions").alias("ssp_impressions"), F.sum("gross_revenue_usd").alias("ssp_revenue_usd")))
    dsp = (spark.read.table(f"{S}.dsp_daily_reports")
           .groupBy("deal_id", "dsp_id", F.col("report_date").alias("recon_date"))
           .agg(F.sum("impressions").alias("dsp_impressions"), F.sum("amount_usd").alias("dsp_revenue_usd")))
    return (ssp.join(dsp, ["deal_id", "dsp_id", "recon_date"], "full")
            .withColumn("billing_month", F.date_format("recon_date", "yyyy-MM"))
            .withColumn("dsp_row_missing", F.col("dsp_impressions").isNull() & (F.col("ssp_impressions") > 0))
            .fillna(0, ["ssp_impressions", "ssp_revenue_usd", "dsp_impressions", "dsp_revenue_usd"])
            .withColumn("impression_gap", F.col("ssp_impressions") - F.col("dsp_impressions"))
            .withColumn("impression_gap_pct", pct_gap("ssp_impressions", "dsp_impressions"))
            .withColumn("revenue_gap_usd", F.round(F.col("ssp_revenue_usd") - F.col("dsp_revenue_usd"), 2))
            .withColumn("revenue_gap_pct", pct_gap("ssp_revenue_usd", "dsp_revenue_usd")))


@dlt.table(name=f"{G}.recon_deal_month",
           comment="Monthly billing reconciliation per CTV deal (the unit of a dispute). needs_review = monthly gap over the "
                   "DSP contract threshold, or >=30% of days with a daily gap over 7.5%. revenue_at_risk_usd = revenue Apex "
                   "delivered that the DSP has not reported.")
def recon_deal_month():
    daily = spark.read.table(f"{G}.recon_deal_daily")
    deals = spark.read.table(f"{S}.dim_deals")
    pubs = spark.read.table(f"{S}.dim_publishers").select("publisher_id", "publisher_name", "publisher_type",
                                                           "ad_server", "ssai_vendor", "ivt_risk_score")
    dsps = spark.read.table(f"{S}.dim_dsps").select("dsp_id", "dsp_name", "partner_team", "reporting_currency",
                                                     "discrepancy_threshold_pct", "billing_count_basis", "payment_terms_days")
    m = (daily.groupBy("deal_id", "dsp_id", "billing_month")
         .agg(F.sum("ssp_impressions").alias("ssp_impressions"), F.sum("dsp_impressions").alias("dsp_impressions"),
              F.round(F.sum("ssp_revenue_usd"), 2).alias("ssp_revenue_usd"),
              F.round(F.sum("dsp_revenue_usd"), 2).alias("dsp_revenue_usd"),
              F.sum(F.when(F.col("ssp_impressions") > 0, 1).otherwise(0)).alias("days_delivered"),
              F.sum(F.col("dsp_row_missing").cast("int")).alias("days_missing_in_dsp_report"),
              F.sum(F.when(~F.col("dsp_row_missing") & (F.abs("impression_gap_pct") > LARGE_DAILY_GAP_PCT), 1)
                    .otherwise(0)).alias("days_with_large_gap")))
    return (m.join(dsps, "dsp_id", "left").join(deals.drop("dsp_id"), "deal_id", "left").join(pubs, "publisher_id", "left")
            .withColumn("impression_gap_pct", pct_gap("ssp_impressions", "dsp_impressions"))
            .withColumn("revenue_gap_usd", F.round(F.col("ssp_revenue_usd") - F.col("dsp_revenue_usd"), 2))
            .withColumn("revenue_gap_pct", pct_gap("ssp_revenue_usd", "dsp_revenue_usd"))
            .withColumn("revenue_at_risk_usd", F.greatest(F.col("revenue_gap_usd"), F.lit(0.0)))
            .withColumn("large_gap_day_share", F.round(F.col("days_with_large_gap") / F.col("days_delivered"), 3))
            .withColumn("over_threshold", F.abs("revenue_gap_pct") > F.col("discrepancy_threshold_pct"))
            .withColumn("needs_review", F.col("over_threshold") | (F.col("large_gap_day_share") >= 0.3)))


@dlt.table(name=f"{G}.recon_partner_month",
           comment="Monthly reconciliation per DSP: totals, gap, deals needing review and revenue at risk. Feeds the close overview.")
def recon_partner_month():
    dm = spark.read.table(f"{G}.recon_deal_month")
    return (dm.groupBy("dsp_id", "dsp_name", "partner_team", "billing_month", "discrepancy_threshold_pct", "payment_terms_days")
            .agg(F.countDistinct("deal_id").alias("active_deals"),
                 F.sum(F.col("needs_review").cast("int")).alias("deals_needing_review"),
                 F.sum("ssp_impressions").alias("ssp_impressions"), F.sum("dsp_impressions").alias("dsp_impressions"),
                 F.round(F.sum("ssp_revenue_usd"), 2).alias("ssp_revenue_usd"),
                 F.round(F.sum("dsp_revenue_usd"), 2).alias("dsp_revenue_usd"),
                 F.round(F.sum("revenue_at_risk_usd"), 2).alias("revenue_at_risk_usd"))
            .withColumn("revenue_gap_usd", F.round(F.col("ssp_revenue_usd") - F.col("dsp_revenue_usd"), 2))
            .withColumn("revenue_gap_pct", pct_gap("ssp_revenue_usd", "dsp_revenue_usd"))
            .withColumn("over_threshold", F.abs("revenue_gap_pct") > F.col("discrepancy_threshold_pct")))


@dlt.table(name=f"{G}.publisher_recon_month",
           comment="Sell-side check: payout Apex owes each CTV publisher (SSP revenue x rev share) vs the publisher's own ad server estimate.")
def publisher_recon_month():
    pubs = spark.read.table(f"{S}.dim_publishers").select("publisher_id", "publisher_name", "publisher_type", "ad_server",
                                                           "publisher_rev_share_pct",
                                                           F.col("discrepancy_threshold_pct").alias("publisher_threshold_pct"))
    ssp = (spark.read.table(f"{S}.ssp_hourly")
           .groupBy("publisher_id", F.date_format("event_date_utc", "yyyy-MM").alias("billing_month"))
           .agg(F.sum("impressions").alias("ssp_impressions"), F.sum("gross_revenue_usd").alias("ssp_revenue_usd")))
    pub = (spark.read.table(f"{S}.publisher_daily_reports")
           .groupBy("publisher_id", F.date_format("report_date", "yyyy-MM").alias("billing_month"))
           .agg(F.sum("adserver_impressions").alias("publisher_impressions"),
                F.round(F.sum("estimated_revenue_usd"), 2).alias("publisher_estimated_payout_usd")))
    return (ssp.join(pub, ["publisher_id", "billing_month"], "full").join(pubs, "publisher_id", "left")
            .withColumn("apex_payout_due_usd", F.round(F.col("ssp_revenue_usd") * F.col("publisher_rev_share_pct") / 100, 2))
            .withColumn("apex_take_usd", F.round(F.col("ssp_revenue_usd") - F.col("apex_payout_due_usd"), 2))
            .withColumn("impression_gap_pct", pct_gap("ssp_impressions", "publisher_impressions"))
            .withColumn("payout_gap_pct", pct_gap("apex_payout_due_usd", "publisher_estimated_payout_usd")))


# ---------- ML features: one row per deal-month ----------

TZ_SHIFTS = list(range(-9, 4))  # hours applied to SSP timestamps to test whether a partner reports in another timezone


@dlt.table(name=f"{M}.discrepancy_features",
           comment="Root-cause features per deal-month: gap shape across days, best-fit timezone shift, sibling offsets, "
                   "revenue-vs-impression divergence, missing days, and deal/publisher context. No labels.")
def discrepancy_features():
    daily = spark.read.table(f"{G}.recon_deal_daily").where(~F.col("dsp_row_missing") & (F.col("ssp_impressions") > 0))
    dm = spark.read.table(f"{G}.recon_deal_month")
    w = Window.partitionBy("deal_id", "billing_month").orderBy("recon_date")

    shape = (daily.withColumn("prev_gap", F.lag("impression_gap_pct").over(w))
             .groupBy("deal_id", "billing_month")
             .agg(F.round(F.stddev("impression_gap_pct"), 3).alias("daily_gap_std"),
                  F.round(F.expr("percentile_approx(impression_gap_pct, 0.5)"), 3).alias("daily_gap_median"),
                  F.round(F.min("impression_gap_pct"), 3).alias("daily_gap_min"),
                  F.round(F.max("impression_gap_pct"), 3).alias("daily_gap_max"),
                  F.round(F.corr("impression_gap_pct", "prev_gap"), 3).alias("daily_gap_lag1_autocorr"),
                  F.round(F.corr("impression_gap_pct", "ssp_impressions"), 3).alias("gap_volume_corr"),
                  F.round(F.avg(F.when(F.col("impression_gap_pct") < -2, 1.0).otherwise(0.0)), 3).alias("share_days_dsp_over")))

    # Timezone test: re-bucket SSP hours with each candidate shift and see how much the daily gap shrinks.
    hourly = spark.read.table(f"{S}.ssp_hourly").select("deal_id", "event_hour_utc", "impressions")
    shifts = spark.createDataFrame([(s,) for s in TZ_SHIFTS], "shift_hours INT")
    dsp_day = daily.select("deal_id", "recon_date", "billing_month", "dsp_impressions")
    shifted = (hourly.crossJoin(F.broadcast(shifts))
               .withColumn("recon_date", F.to_date(F.expr("event_hour_utc + make_interval(0,0,0,0,shift_hours,0,0)")))
               .groupBy("deal_id", "shift_hours", "recon_date").agg(F.sum("impressions").alias("ssp_shifted"))
               .join(dsp_day, ["deal_id", "recon_date"])
               .groupBy("deal_id", "billing_month", "shift_hours")
               .agg(F.avg(F.abs(100 * (F.col("ssp_shifted") - F.col("dsp_impressions")) / F.col("ssp_shifted"))).alias("mad")))
    best = Window.partitionBy("deal_id", "billing_month").orderBy("mad")
    tz = (shifted.withColumn("rk", F.row_number().over(best))
          .groupBy("deal_id", "billing_month")
          .agg(F.max(F.when(F.col("shift_hours") == 0, F.col("mad"))).alias("mad_no_shift"),
               F.max(F.when(F.col("rk") == 1, F.col("mad"))).alias("mad_best_shift"),
               F.max(F.when(F.col("rk") == 1, F.col("shift_hours"))).alias("best_shift_hours"))
          .withColumn("tz_shift_gain", F.round(F.col("mad_no_shift") - F.col("mad_best_shift"), 3))
          .select("deal_id", "billing_month", "best_shift_hours", "tz_shift_gain"))

    # Sibling offset: another deal of the same DSP in the same month whose surplus mirrors this deal's shortfall.
    g = dm.select("deal_id", "dsp_id", "billing_month", (F.col("ssp_impressions") - F.col("dsp_impressions")).alias("gap"))
    o = g.select(F.col("deal_id").alias("o_deal"), "dsp_id", "billing_month", F.col("gap").alias("o_gap"))
    sib = (g.join(o, ["dsp_id", "billing_month"]).where((F.col("deal_id") != F.col("o_deal")) & (F.col("gap") * F.col("o_gap") < 0))
           .withColumn("match", F.least(F.abs("gap"), F.abs("o_gap")) / F.greatest(F.abs("gap"), F.abs("o_gap")))
           .groupBy("deal_id", "billing_month").agg(F.round(F.max("match"), 3).alias("sibling_offset_match")))

    return (dm.select("deal_id", "dsp_id", "billing_month", "ssp_impressions", "ssp_revenue_usd", "impression_gap_pct",
                      "revenue_gap_pct", "revenue_gap_usd", "days_delivered", "days_missing_in_dsp_report",
                      "large_gap_day_share", "needs_review", "discrepancy_threshold_pct", "reporting_currency",
                      "content_genre", "is_live", "device_type", "deal_type", "publisher_type", "ssai_vendor",
                      "ivt_risk_score")
            .withColumn("rev_minus_imp_gap_pct", F.round(F.col("revenue_gap_pct") - F.col("impression_gap_pct"), 3))
            .withColumn("missing_day_share", F.round(F.col("days_missing_in_dsp_report") / F.col("days_delivered"), 3))
            .withColumn("is_non_usd", F.col("reporting_currency") != "USD")
            .join(shape, ["deal_id", "billing_month"], "left")
            .join(tz, ["deal_id", "billing_month"], "left")
            .join(sib, ["deal_id", "billing_month"], "left")
            .fillna({"sibling_offset_match": 0.0, "tz_shift_gain": 0.0, "best_shift_hours": 0}))
