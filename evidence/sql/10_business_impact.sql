-- Business impact inputs for the deck: Q3 open-case exposure by predicted root cause, with the recovery rate
-- Billing Ops actually achieved on each cause in the Jan-Jun resolved history.
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
ORDER BY q3_revenue_at_risk_usd DESC;

SELECT round(sum(revenue_at_risk_usd)) AS q3_revenue_at_risk_usd, count(*) AS q3_cases,
       count(DISTINCT dsp_id) AS dsps_involved
FROM apex_recon.gold.dispute_queue;

SELECT round(sum(ssp_revenue_usd)) AS q3_gross_revenue_usd, round(sum(revenue_at_risk_usd)) AS q3_revenue_at_risk_all_deals_usd,
       round(100 * sum(revenue_at_risk_usd) / sum(ssp_revenue_usd), 2) AS at_risk_pct_of_gross
FROM apex_recon.gold.recon_deal_month WHERE billing_month >= '2026-07';

-- Analyst effort: historical time to resolve and cases per month
SELECT round(avg(days_to_resolve), 1) AS avg_days_to_resolve, percentile_approx(days_to_resolve, 0.9) AS p90_days,
       round(count(*) / 6.0) AS cases_per_month
FROM apex_recon.ml.dispute_history;

-- Pilot scoping: share of Q3 revenue at risk held by the top 5 DSPs
SELECT round(100 * sum(CASE WHEN rk <= 5 THEN usd END) / sum(usd), 1) AS top5_share_pct
FROM (SELECT dsp_id, sum(revenue_at_risk_usd) AS usd, row_number() OVER (ORDER BY sum(revenue_at_risk_usd) DESC) AS rk
      FROM apex_recon.gold.dispute_queue GROUP BY dsp_id);
