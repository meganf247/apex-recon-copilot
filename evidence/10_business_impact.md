
```sql
WITH hist AS (
  SELECT resolved_root_cause AS cause,
         sum(recovered_usd) / nullif(sum(greatest(revenue_gap_usd, 0)), 0) AS historical_recovery_rate,
         avg(days_to_resolve) AS avg_days_to_resolve, count(*) AS historical_cases
  FROM apex_recon.ml.dispute_history GROUP BY 1
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
| IVT_FILTERING | 280 | 8179089.0 | 0.0 | 0.0 | 21.4 |
| GENUINE_BILLING_ERROR | 141 | 4907612.0 | 0.6 | 2944567.0 | 20.4 |
| LATE_OR_MISSING_DATA | 145 | 3539910.0 | 0.9 | 3185919.0 | 21.4 |
| WITHIN_TOLERANCE | 70 | 924973.0 | 0.0 | 0.0 | 20.2 |
| TIMEZONE_SHIFT | 79 | 561888.0 | 0.0 | 0.0 | 21.4 |

```sql
SELECT round(sum(revenue_at_risk_usd)) AS q3_revenue_at_risk_usd, count(*) AS q3_cases,
       count(DISTINCT dsp_id) AS dsps_involved
FROM apex_recon.gold.dispute_queue
```
| q3_revenue_at_risk_usd | q3_cases | dsps_involved |
|---|---|---|
| 1.8113472E7 | 715 | 39 |

```sql
SELECT round(sum(ssp_revenue_usd)) AS q3_gross_revenue_usd, round(sum(revenue_at_risk_usd)) AS q3_revenue_at_risk_all_deals_usd,
       round(100 * sum(revenue_at_risk_usd) / sum(ssp_revenue_usd), 2) AS at_risk_pct_of_gross
FROM apex_recon.gold.recon_deal_month WHERE billing_month >= '2026-07'
```
| q3_gross_revenue_usd | q3_revenue_at_risk_all_deals_usd | at_risk_pct_of_gross |
|---|---|---|
| 4.32140868E8 | 2.4428097E7 | 5.65 |

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
