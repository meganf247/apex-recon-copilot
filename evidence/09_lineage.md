
```sql
SELECT source_table_full_name, target_table_full_name, count(*) AS lineage_events, max(event_time) AS last_seen
FROM system.access.table_lineage
WHERE (target_table_full_name LIKE 'apex_recon.%' OR source_table_full_name LIKE 'apex_recon.%')
  AND source_table_full_name IS NOT NULL AND target_table_full_name IS NOT NULL
GROUP BY 1, 2 ORDER BY 2, 1
```
| source_table_full_name | target_table_full_name | lineage_events | last_seen |
|---|---|---|---|
| apex_recon.gold.dispute_drafts | apex_recon.gold.case_workbench | 2 | 2026-10-05T17:21:26.291Z |
| apex_recon.gold.dispute_queue | apex_recon.gold.case_workbench | 2 | 2026-10-05T17:21:26.291Z |
| apex_recon.gold.dispute_queue | apex_recon.gold.dispute_drafts | 2 | 2026-10-05T17:21:20.926Z |
| apex_recon.gold.recon_deal_month | apex_recon.gold.dispute_queue | 3 | 2026-10-05T15:38:50.432Z |
| apex_recon.ml.discrepancy_features | apex_recon.gold.dispute_queue | 3 | 2026-10-05T15:38:50.432Z |
| apex_recon.ml.discrepancy_predictions | apex_recon.gold.dispute_queue | 3 | 2026-10-05T15:38:50.432Z |
| apex_recon.silver.dim_publishers | apex_recon.gold.publisher_recon_month | 5 | 2026-10-06T16:47:38.648Z |
| apex_recon.silver.publisher_daily_reports | apex_recon.gold.publisher_recon_month | 5 | 2026-10-06T16:47:38.648Z |
| apex_recon.silver.ssp_hourly | apex_recon.gold.publisher_recon_month | 5 | 2026-10-06T16:47:38.648Z |
| apex_recon.silver.dsp_daily_reports | apex_recon.gold.recon_deal_daily | 5 | 2026-10-06T16:47:38.612Z |
| apex_recon.silver.ssp_hourly | apex_recon.gold.recon_deal_daily | 5 | 2026-10-06T16:47:38.612Z |
| apex_recon.gold.recon_deal_daily | apex_recon.gold.recon_deal_month | 6 | 2026-10-06T16:47:42.087Z |
| apex_recon.silver.dim_deals | apex_recon.gold.recon_deal_month | 6 | 2026-10-06T16:47:42.087Z |
| apex_recon.silver.dim_dsps | apex_recon.gold.recon_deal_month | 6 | 2026-10-06T16:47:42.087Z |
| apex_recon.silver.dim_publishers | apex_recon.gold.recon_deal_month | 6 | 2026-10-06T16:47:42.087Z |
| apex_recon.gold.recon_deal_month | apex_recon.gold.recon_partner_month | 5 | 2026-10-06T16:47:42.756Z |
| apex_recon.gold.recon_deal_daily | apex_recon.ml.discrepancy_features | 5 | 2026-10-06T16:47:43.680Z |
| apex_recon.gold.recon_deal_month | apex_recon.ml.discrepancy_features | 5 | 2026-10-06T16:47:43.680Z |
| apex_recon.silver.ssp_hourly | apex_recon.ml.discrepancy_features | 5 | 2026-10-06T16:47:43.680Z |
| apex_recon.gold.case_workbench | apex_recon.ops.dispute_case_status | 15 | 2026-10-05T17:31:40.186Z |
| apex_recon.ops.lakebase_credit_approvals | apex_recon.ops.dispute_case_status | 15 | 2026-10-05T17:31:40.186Z |
| apex_recon.ops.lakebase_dispute_cases | apex_recon.ops.dispute_case_status | 15 | 2026-10-05T17:31:40.186Z |
| apex_recon.bronze.dispute_resolutions | apex_recon.silver.dispute_history | 6 | 2026-10-06T16:47:21.331Z |
| apex_recon.bronze.dsp_reports_format_a | apex_recon.silver.dsp_daily_reports | 4 | 2026-10-06T16:47:24.700Z |
| apex_recon.bronze.dsp_reports_format_b | apex_recon.silver.dsp_daily_reports | 4 | 2026-10-06T16:47:24.700Z |
| apex_recon.bronze.dsp_reports_format_c | apex_recon.silver.dsp_daily_reports | 4 | 2026-10-06T16:47:24.700Z |
| apex_recon.silver.dim_deals | apex_recon.silver.dsp_daily_reports | 4 | 2026-10-06T16:47:24.700Z |
| apex_recon.silver.dim_dsps | apex_recon.silver.dsp_daily_reports | 4 | 2026-10-06T16:47:24.700Z |
| apex_recon.silver.fx_rates | apex_recon.silver.dsp_daily_reports | 4 | 2026-10-06T16:47:24.700Z |
| apex_recon.bronze.dsp_reports_format_a | apex_recon.silver.dsp_reports_quarantine | 5 | 2026-10-06T16:47:24.736Z |
| apex_recon.bronze.dsp_reports_format_b | apex_recon.silver.dsp_reports_quarantine | 5 | 2026-10-06T16:47:24.736Z |
| apex_recon.bronze.dsp_reports_format_c | apex_recon.silver.dsp_reports_quarantine | 5 | 2026-10-06T16:47:24.736Z |
| apex_recon.silver.dim_deals | apex_recon.silver.dsp_reports_quarantine | 5 | 2026-10-06T16:47:24.736Z |
| apex_recon.silver.dim_dsps | apex_recon.silver.dsp_reports_quarantine | 5 | 2026-10-06T16:47:24.736Z |
| apex_recon.silver.fx_rates | apex_recon.silver.dsp_reports_quarantine | 5 | 2026-10-06T16:47:24.736Z |
| apex_recon.bronze.publisher_adserver_reports | apex_recon.silver.publisher_daily_reports | 4 | 2026-10-06T16:47:27.640Z |
| apex_recon.bronze.ssp_auction_logs | apex_recon.silver.ssp_hourly | 2 | 2026-10-06T16:47:34.673Z |
