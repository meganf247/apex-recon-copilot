
```sql
WITH hist AS (
  SELECT resolved_root_cause AS cause,
         sum(recovered_usd) / nullif(sum(greatest(revenue_gap_usd, 0)), 0) AS historical_recovery_rate,
         avg(days_to_resolve) AS avg_days_to_resolve, count(*) AS historical_cases
  FROM apex_recon.silver.dispute_history GROUP BY 1
)
SELECT q.predicted_root_cause, count(*) AS q3_cases, round(sum(q.revenue_at_risk_usd)) AS q3_revenue_at_risk_usd,
       round(h.historical_recovery_rate, 3) AS historical_recovery_rate,
       round(sum(q.revenue_at_risk_usd) * coalesce(h.historical_recovery_rate, 0)) AS recoverable_usd,
       round(h.avg_days_to_resolve, 1) AS historical_avg_days_to_resolve
FROM apex_recon.gold.dispute_queue q LEFT JOIN hist h ON h.cause = q.predicted_root_cause
GROUP BY q.predicted_root_cause, h.historical_recovery_rate, h.avg_days_to_resolve
ORDER BY q3_revenue_at_risk_usd DESC
```
| predicted_root_cause | q3_cases | q3_revenue_at_risk_usd | historical_recovery_rate | recoverable_usd | historical_avg_days_to_resolve |
|---|---|---|---|---|---|
| SSAI_BEACON_LOSS | 187 | 5032434.0 | 0.4 | 2012974.0 | 20.3 |
| IVT_FILTERING | 191 | 4627116.0 | 0.0 | 0.0 | 21.0 |
| DEAL_ID_MISMAPPING | 111 | 3841454.0 | 0.95 | 3649382.0 | 21.2 |
| GENUINE_BILLING_ERROR | 108 | 3477331.0 | 0.6 | 2086399.0 | 20.6 |
| LATE_OR_MISSING_DATA | 117 | 3225242.0 | 0.9 | 2902718.0 | 20.9 |
| FX_MISMATCH | 62 | 1322601.0 | 0.9 | 1190341.0 | 20.5 |
| TIMEZONE_SHIFT | 132 | 928902.0 | 0.0 | 0.0 | 20.4 |
| WITHIN_TOLERANCE | 13 | 190290.0 | 0.0 | 0.0 | 21.2 |

```sql
SELECT round(sum(revenue_at_risk_usd)) AS q3_revenue_at_risk_usd, count(*) AS q3_cases,
       count(DISTINCT dsp_id) AS dsps_involved
FROM apex_recon.gold.dispute_queue
```
| q3_revenue_at_risk_usd | q3_cases | dsps_involved |
|---|---|---|
| 2.264537E7 | 921 | 39 |

```sql
SELECT round(sum(ssp_revenue_usd)) AS q3_gross_revenue_usd, round(sum(revenue_at_risk_usd)) AS q3_revenue_at_risk_all_deals_usd,
       round(100 * sum(revenue_at_risk_usd) / sum(ssp_revenue_usd), 2) AS at_risk_pct_of_gross
FROM apex_recon.gold.recon_deal_month WHERE billing_month >= '2026-07'
```
| q3_gross_revenue_usd | q3_revenue_at_risk_all_deals_usd | at_risk_pct_of_gross |
|---|---|---|
| 4.28479438E8 | 2.7927301E7 | 6.52 |

```sql
SELECT round(avg(days_to_resolve), 1) AS avg_days_to_resolve, percentile_approx(days_to_resolve, 0.9) AS p90_days,
       round(count(*) / 6.0) AS cases_per_month
FROM apex_recon.silver.dispute_history
```
| avg_days_to_resolve | p90_days | cases_per_month |
|---|---|---|
| 20.7 | 34 | 359 |

```sql
SELECT round(100 * sum(CASE WHEN rk <= 5 THEN usd END) / sum(usd), 1) AS top5_share_pct
FROM (SELECT dsp_id, sum(revenue_at_risk_usd) AS usd, row_number() OVER (ORDER BY sum(revenue_at_risk_usd) DESC) AS rk
      FROM apex_recon.gold.dispute_queue GROUP BY dsp_id)
```
| top5_share_pct |
|---|
| 48.6 |
