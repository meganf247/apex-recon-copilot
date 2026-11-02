-- Business impact inputs for the deck.
-- Definitions: billing shortfall = positive gap on every deal; revenue at risk = the shortfall on deals that need
-- review (the dispute queue); Apex net exposure = the part of revenue at risk that hits Apex's own P&L (all of it when
-- the publisher is paid on Apex's count, only Apex's take rate when the publisher is paid on cleared revenue).

-- 1. Q3 queue by predicted root cause, with the recovery rate Billing Ops actually achieved on each cause in Jan-Jun.
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
ORDER BY q3_revenue_at_risk_usd DESC;

-- 2. Q3 headline: gross spend vs Apex's own revenue, and the three gap measures.
SELECT round(sum(ssp_revenue_usd)) AS q3_gross_ctv_spend_usd, round(sum(apex_net_revenue_usd)) AS q3_apex_net_revenue_usd,
       round(100 * sum(apex_net_revenue_usd) / sum(ssp_revenue_usd), 1) AS avg_take_rate_pct,
       round(sum(billing_shortfall_usd)) AS q3_billing_shortfall_usd,
       round(100 * sum(billing_shortfall_usd) / sum(ssp_revenue_usd), 2) AS shortfall_pct_of_gross,
       round(sum(revenue_at_risk_usd)) AS q3_revenue_at_risk_usd, sum(CAST(needs_review AS INT)) AS q3_cases,
       round(sum(apex_exposure_usd)) AS q3_apex_exposure_usd,
       round(100 * sum(apex_exposure_usd) / sum(apex_net_revenue_usd), 1) AS exposure_pct_of_apex_net_revenue
FROM apex_recon.gold.recon_deal_month WHERE billing_month >= '2026-07';

-- 3. Where Apex's exposure comes from: publisher payment terms.
SELECT publisher_paid_on, count(*) AS q3_cases, round(sum(revenue_at_risk_usd)) AS revenue_at_risk_usd,
       round(sum(apex_exposure_usd)) AS apex_exposure_usd, round(avg(apex_take_rate_pct), 1) AS avg_take_rate_pct
FROM apex_recon.gold.dispute_queue GROUP BY 1 ORDER BY 1;

-- 4. Queue size by DSP.
SELECT count(*) AS q3_cases, count(DISTINCT dsp_id) AS dsps_involved FROM apex_recon.gold.dispute_queue;

-- 5. Today's dispute process (Jan-Jun history).
SELECT round(avg(days_to_resolve), 1) AS avg_days_to_resolve, percentile_approx(days_to_resolve, 0.9) AS p90_days,
       round(count(*) / 6.0) AS cases_per_month
FROM apex_recon.ml.dispute_history;

-- 6. Concentration: share of Q3 revenue at risk with the top 5 DSPs.
SELECT round(100 * sum(CASE WHEN rk <= 5 THEN usd END) / sum(usd), 1) AS top5_share_pct
FROM (SELECT dsp_id, sum(revenue_at_risk_usd) AS usd, row_number() OVER (ORDER BY sum(revenue_at_risk_usd) DESC) AS rk
      FROM apex_recon.gold.dispute_queue GROUP BY dsp_id);
