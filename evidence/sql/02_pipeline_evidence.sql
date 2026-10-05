-- Lakeflow pipeline evidence: rows written per dataset and expectation results for the latest update.
SELECT origin.flow_name AS dataset,
       max(details:flow_progress.metrics.num_output_rows::BIGINT) AS output_rows,
       max(details:flow_progress.data_quality.dropped_records::BIGINT) AS dropped_by_expectations
FROM event_log('5d44a671-5813-463d-903e-33ca04bb3376')
WHERE event_type = 'flow_progress' AND details:flow_progress.status = 'COMPLETED'
  AND origin.update_id = (SELECT origin.update_id FROM event_log('5d44a671-5813-463d-903e-33ca04bb3376')
                          WHERE event_type = 'create_update' ORDER BY timestamp DESC LIMIT 1)
GROUP BY 1 ORDER BY 1;

SELECT origin.flow_name AS dataset, e.name AS expectation,
       sum(e.passed_records) AS passed_records, sum(e.failed_records) AS failed_records
FROM event_log('5d44a671-5813-463d-903e-33ca04bb3376'),
     LATERAL explode(from_json(details:flow_progress.data_quality.expectations,
                     'array<struct<name:string,dataset:string,passed_records:bigint,failed_records:bigint>>')) AS t(e)
WHERE event_type = 'flow_progress' AND details:flow_progress.data_quality.expectations IS NOT NULL
  AND origin.update_id = (SELECT origin.update_id FROM event_log('5d44a671-5813-463d-903e-33ca04bb3376')
                          WHERE event_type = 'create_update' ORDER BY timestamp DESC LIMIT 1)
GROUP BY 1, 2 ORDER BY 1, 2;

-- Quarantine: every rejected DSP report row is kept with the rules it failed.
SELECT r AS failed_rule, count(*) AS rows
FROM apex_recon.silver.dsp_reports_quarantine LATERAL VIEW explode(failed_rules) x AS r
GROUP BY r ORDER BY rows DESC;

SELECT dsp_id, source_format, report_date, deal_id, impressions, amount_native, failed_rules, _source_file
FROM apex_recon.silver.dsp_reports_quarantine ORDER BY dsp_id, _source_file LIMIT 10;

-- Three partner layouts normalized into one silver table
SELECT source_format, currency, count(*) AS rows, count(DISTINCT dsp_id) AS dsps,
       round(sum(amount_native), 2) AS amount_native, round(sum(amount_usd), 2) AS amount_usd
FROM apex_recon.silver.dsp_daily_reports GROUP BY 1, 2 ORDER BY 1, 2;

-- Gold reconciliation: September close by partner (top 10 by revenue at risk)
SELECT dsp_name, partner_team, active_deals, deals_needing_review, ssp_revenue_usd, dsp_revenue_usd,
       revenue_gap_pct, discrepancy_threshold_pct, over_threshold, revenue_at_risk_usd
FROM apex_recon.gold.recon_partner_month WHERE billing_month = '2026-09'
ORDER BY revenue_at_risk_usd DESC LIMIT 10;

-- Month-level totals across the window
SELECT billing_month, count(*) AS deal_months, sum(CAST(needs_review AS INT)) AS needs_review,
       round(sum(ssp_revenue_usd), 0) AS ssp_revenue_usd, round(sum(dsp_revenue_usd), 0) AS dsp_revenue_usd,
       round(sum(revenue_at_risk_usd), 0) AS revenue_at_risk_usd
FROM apex_recon.gold.recon_deal_month GROUP BY 1 ORDER BY 1;

-- Sell side: payout owed to publishers vs publisher ad server estimates (September)
SELECT publisher_type, count(*) AS publishers, round(sum(apex_payout_due_usd), 0) AS apex_payout_due_usd,
       round(sum(publisher_estimated_payout_usd), 0) AS publisher_estimated_payout_usd,
       round(sum(apex_take_usd), 0) AS apex_take_usd,
       round(100 * sum(apex_take_usd) / sum(ssp_revenue_usd), 2) AS take_rate_pct
FROM apex_recon.gold.publisher_recon_month WHERE billing_month = '2026-09' GROUP BY 1 ORDER BY 1;

-- ML feature signal by planted root cause (ground truth joined for evaluation only)
SELECT g.root_cause, count(*) AS deal_months, round(avg(f.tz_shift_gain), 2) AS avg_tz_shift_gain,
       round(avg(f.sibling_offset_match), 2) AS avg_sibling_offset, round(avg(f.missing_day_share), 3) AS avg_missing_day_share,
       round(avg(abs(f.rev_minus_imp_gap_pct)), 2) AS avg_abs_rev_minus_imp, round(avg(f.large_gap_day_share), 2) AS avg_large_gap_days
FROM apex_recon.ml.discrepancy_features f JOIN apex_recon.ml.ground_truth_root_causes g USING (deal_id, billing_month)
GROUP BY 1 ORDER BY 1;
