
```sql
WITH hist AS (
  SELECT resolved_root_cause AS cause,
         sum(recovered_usd) / nullif(sum(greatest(revenue_gap_usd, 0)), 0) AS historical_recovery_rate,
         avg(days_to_resolve) AS avg_days_to_resolve, count(*) AS historical_cases
  FROM apex_recon.ml.dispute_history GROUP BY 1
)
SELECT q.predicted_root_cause, count(*) AS q3_cases, round(sum(q.revenue_at_risk_usd)) AS q3_revenue_at_risk_usd,
       round(sum(q.apex_exposure_usd)) AS q3_apex_exposure_usd,
       round(h.historical_recovery_rate, 3) AS historical_recovery_rate,
       round(sum(q.revenue_at_risk_usd) * coalesce(h.historical_recovery_rate, 0)) AS recoverable_usd,
       round(sum(q.apex_exposure_usd) * coalesce(h.historical_recovery_rate, 0)) AS recoverable_to_apex_pnl_usd,
       round(h.avg_days_to_resolve, 1) AS historical_avg_days_to_resolve
FROM apex_recon.gold.dispute_queue q LEFT JOIN hist h ON h.cause = q.predicted_root_cause
GROUP BY q.predicted_root_cause, h.historical_recovery_rate, h.avg_days_to_resolve
ORDER BY q3_revenue_at_risk_usd DESC
```
| predicted_root_cause | q3_cases | q3_revenue_at_risk_usd | q3_apex_exposure_usd | historical_recovery_rate | recoverable_usd | recoverable_to_apex_pnl_usd | historical_avg_days_to_resolve |
|---|---|---|---|---|---|---|---|
| IVT_FILTERING | 269 | 7945604.0 | 4053293.0 | 0.0 | 0.0 | 0.0 | 21.4 |
| GENUINE_BILLING_ERROR | 152 | 5246259.0 | 2384752.0 | 0.6 | 3147755.0 | 1430851.0 | 20.4 |
| LATE_OR_MISSING_DATA | 145 | 3485356.0 | 1695191.0 | 0.9 | 3136821.0 | 1525672.0 | 21.4 |
| WITHIN_TOLERANCE | 70 | 840009.0 | 515598.0 | 0.0 | 0.0 | 0.0 | 20.2 |
| TIMEZONE_SHIFT | 79 | 596244.0 | 275261.0 | 0.0 | 0.0 | 0.0 | 21.4 |

```sql
SELECT round(sum(ssp_revenue_usd)) AS q3_gross_ctv_spend_usd, round(sum(apex_net_revenue_usd)) AS q3_apex_net_revenue_usd,
       round(100 * sum(apex_net_revenue_usd) / sum(ssp_revenue_usd), 1) AS avg_take_rate_pct,
       round(sum(billing_shortfall_usd)) AS q3_billing_shortfall_usd,
       round(100 * sum(billing_shortfall_usd) / sum(ssp_revenue_usd), 2) AS shortfall_pct_of_gross,
       round(sum(revenue_at_risk_usd)) AS q3_revenue_at_risk_usd, sum(CAST(needs_review AS INT)) AS q3_cases,
       round(sum(apex_exposure_usd)) AS q3_apex_exposure_usd,
       round(100 * sum(apex_exposure_usd) / sum(apex_net_revenue_usd), 1) AS exposure_pct_of_apex_net_revenue
FROM apex_recon.gold.recon_deal_month WHERE billing_month >= '2026-07'
```
| q3_gross_ctv_spend_usd | q3_apex_net_revenue_usd | avg_take_rate_pct | q3_billing_shortfall_usd | shortfall_pct_of_gross | q3_revenue_at_risk_usd | q3_cases | q3_apex_exposure_usd | exposure_pct_of_apex_net_revenue |
|---|---|---|---|---|---|---|---|---|
| 4.32140868E8 | 6.1918136E7 | 14.3 | 2.4428097E7 | 5.65 | 1.8113472E7 | 715 | 8924095.0 | 14.4 |

```sql
SELECT publisher_paid_on, count(*) AS q3_cases, round(sum(revenue_at_risk_usd)) AS revenue_at_risk_usd,
       round(sum(apex_exposure_usd)) AS apex_exposure_usd, round(avg(apex_take_rate_pct), 1) AS avg_take_rate_pct
FROM apex_recon.gold.dispute_queue GROUP BY 1 ORDER BY 1
```
| publisher_paid_on | q3_cases | revenue_at_risk_usd | apex_exposure_usd | avg_take_rate_pct |
|---|---|---|---|---|
| APEX_COUNT | 279 | 7280177.0 | 7280177.0 | 13.5 |
| CLEARED | 436 | 1.0833295E7 | 1643918.0 | 15.6 |

```sql
SELECT count(*) AS q3_cases, count(DISTINCT dsp_id) AS dsps_involved FROM apex_recon.gold.dispute_queue
```
| q3_cases | dsps_involved |
|---|---|
| 715 | 39 |

```sql
SELECT round(avg(days_to_resolve), 1) AS avg_days_to_resolve, percentile_approx(days_to_resolve, 0.9) AS p90_days,
       round(count(*) / 6.0) AS cases_per_month
FROM apex_recon.ml.dispute_history
```
| avg_days_to_resolve | p90_days | cases_per_month |
|---|---|---|
| 20.9 | 33 | 269 |

```sql
SELECT round(100 * sum(CASE WHEN rk <= 5 THEN usd END) / sum(usd), 1) AS top5_share_pct
FROM (SELECT dsp_id, sum(revenue_at_risk_usd) AS usd, row_number() OVER (ORDER BY sum(revenue_at_risk_usd) DESC) AS rk
      FROM apex_recon.gold.dispute_queue GROUP BY dsp_id)
```
| top5_share_pct |
|---|
| 37.7 |
