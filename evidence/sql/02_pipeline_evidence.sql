-- Rows per table and rows dropped by expectations. Streaming (bronze) tables log row counts on RUNNING progress events, so take the max over all of them.
-- Lakeflow pipeline evidence: rows written per dataset and expectation results for the latest update.
SELECT origin.flow_name AS dataset,
       max(details:flow_progress.metrics.num_output_rows::BIGINT) AS output_rows,
       max(details:flow_progress.data_quality.dropped_records::BIGINT) AS dropped_by_expectations
FROM event_log('7e5bc896-605c-44f6-a2e3-039922e893a9')
WHERE event_type = 'flow_progress' AND origin.flow_name LIKE 'apex_recon.%'
  AND origin.update_id = (SELECT origin.update_id FROM event_log('7e5bc896-605c-44f6-a2e3-039922e893a9')
                          WHERE event_type = 'create_update' ORDER BY timestamp DESC LIMIT 1)
GROUP BY 1 ORDER BY 1;

SELECT origin.flow_name AS dataset, e.name AS expectation,
       sum(e.passed_records) AS passed_records, sum(e.failed_records) AS failed_records
FROM event_log('7e5bc896-605c-44f6-a2e3-039922e893a9'),
     LATERAL explode(from_json(details:flow_progress.data_quality.expectations,
                     'array<struct<name:string,dataset:string,passed_records:bigint,failed_records:bigint>>')) AS t(e)
WHERE event_type = 'flow_progress' AND details:flow_progress.data_quality.expectations IS NOT NULL
  AND origin.update_id = (SELECT origin.update_id FROM event_log('7e5bc896-605c-44f6-a2e3-039922e893a9')
                          WHERE event_type = 'create_update' ORDER BY timestamp DESC LIMIT 1)
GROUP BY 1, 2 ORDER BY 1, 2;

-- Silver: the four data-quality rules on DSP reports (counts of rows each rule removed are in the expectation table above)
SELECT count(*) AS bronze_dsp_rows FROM apex_recon.bronze.dsp_reports;
SELECT count(*) AS silver_dsp_rows, count(DISTINCT dsp_id) AS dsps, min(report_date) AS first_day, max(report_date) AS last_day
FROM apex_recon.silver.dsp_daily;

-- Gold reconciliation: September close by partner (top 10 by revenue at risk)
SELECT dsp_name, partner_team, active_deals, deals_needing_review, ssp_revenue_usd, dsp_revenue_usd,
       revenue_gap_pct, discrepancy_threshold_pct, over_threshold, billing_shortfall_usd, revenue_at_risk_usd, apex_exposure_usd
FROM apex_recon.gold.recon_partner_month WHERE billing_month = '2026-09'
ORDER BY revenue_at_risk_usd DESC LIMIT 10;

-- Month-level totals across the window
SELECT billing_month, count(*) AS deal_months, sum(CAST(needs_review AS INT)) AS needs_review,
       round(sum(ssp_revenue_usd), 0) AS ssp_revenue_usd, round(sum(dsp_revenue_usd), 0) AS dsp_revenue_usd,
       round(sum(billing_shortfall_usd), 0) AS billing_shortfall_usd, round(sum(revenue_at_risk_usd), 0) AS revenue_at_risk_usd,
       round(sum(apex_net_revenue_usd), 0) AS apex_net_revenue_usd, round(sum(apex_exposure_usd), 0) AS apex_exposure_usd
FROM apex_recon.gold.recon_deal_month GROUP BY 1 ORDER BY 1;
