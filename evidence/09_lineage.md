
```sql
SELECT source_table_full_name, target_table_full_name, count(*) AS lineage_events, max(event_time) AS last_seen
FROM system.access.table_lineage
WHERE (target_table_full_name LIKE 'apex_recon.%' OR source_table_full_name LIKE 'apex_recon.%')
  AND source_table_full_name IS NOT NULL AND target_table_full_name IS NOT NULL
GROUP BY 1, 2 ORDER BY 2, 1
```
| source_table_full_name | target_table_full_name | lineage_events | last_seen |
|---|---|---|---|
| apex_recon.gold.dispute_drafts | apex_recon.gold.case_workbench | 1 | 2026-10-05T15:41:23.280Z |
| apex_recon.gold.dispute_queue | apex_recon.gold.case_workbench | 1 | 2026-10-05T15:41:23.280Z |
| apex_recon.gold.dispute_queue | apex_recon.gold.dispute_drafts | 1 | 2026-10-05T15:41:17.287Z |
| apex_recon.gold.recon_deal_month | apex_recon.gold.dispute_queue | 3 | 2026-10-05T15:38:50.432Z |
| apex_recon.ml.discrepancy_features | apex_recon.gold.dispute_queue | 3 | 2026-10-05T15:38:50.432Z |
| apex_recon.ml.discrepancy_predictions | apex_recon.gold.dispute_queue | 3 | 2026-10-05T15:38:50.432Z |
| apex_recon.silver.dim_publishers | apex_recon.gold.publisher_recon_month | 2 | 2026-10-05T15:32:51.846Z |
| apex_recon.silver.publisher_daily_reports | apex_recon.gold.publisher_recon_month | 2 | 2026-10-05T15:32:51.846Z |
| apex_recon.silver.ssp_hourly | apex_recon.gold.publisher_recon_month | 2 | 2026-10-05T15:32:51.846Z |
| apex_recon.silver.dsp_daily_reports | apex_recon.gold.recon_deal_daily | 2 | 2026-10-05T15:32:51.933Z |
| apex_recon.silver.ssp_hourly | apex_recon.gold.recon_deal_daily | 2 | 2026-10-05T15:32:51.933Z |
| apex_recon.gold.recon_deal_daily | apex_recon.gold.recon_deal_month | 2 | 2026-10-05T15:32:55.686Z |
| apex_recon.silver.dim_deals | apex_recon.gold.recon_deal_month | 2 | 2026-10-05T15:32:55.686Z |
| apex_recon.silver.dim_dsps | apex_recon.gold.recon_deal_month | 2 | 2026-10-05T15:32:55.686Z |
| apex_recon.silver.dim_publishers | apex_recon.gold.recon_deal_month | 2 | 2026-10-05T15:32:55.686Z |
| apex_recon.gold.recon_deal_month | apex_recon.gold.recon_partner_month | 2 | 2026-10-05T15:32:59.262Z |
| apex_recon.gold.recon_deal_daily | apex_recon.ml.discrepancy_features | 2 | 2026-10-05T15:33:04.450Z |
| apex_recon.gold.recon_deal_month | apex_recon.ml.discrepancy_features | 2 | 2026-10-05T15:33:04.450Z |
| apex_recon.silver.ssp_hourly | apex_recon.ml.discrepancy_features | 2 | 2026-10-05T15:33:04.450Z |
| apex_recon.gold.case_workbench | apex_recon.ops.dispute_case_status | 2 | 2026-10-05T16:03:07.299Z |
| apex_recon.ops.lakebase_credit_approvals | apex_recon.ops.dispute_case_status | 2 | 2026-10-05T16:03:07.299Z |
| apex_recon.ops.lakebase_dispute_cases | apex_recon.ops.dispute_case_status | 2 | 2026-10-05T16:03:07.299Z |
| apex_recon.bronze.dispute_resolutions | apex_recon.silver.dispute_history | 2 | 2026-10-05T15:32:32.952Z |
| apex_recon.bronze.dsp_reports_format_a | apex_recon.silver.dsp_daily_reports | 1 | 2026-10-05T15:32:31.479Z |
| apex_recon.bronze.dsp_reports_format_b | apex_recon.silver.dsp_daily_reports | 1 | 2026-10-05T15:32:31.479Z |
| apex_recon.bronze.dsp_reports_format_c | apex_recon.silver.dsp_daily_reports | 1 | 2026-10-05T15:32:31.479Z |
| apex_recon.silver.dim_deals | apex_recon.silver.dsp_daily_reports | 1 | 2026-10-05T15:32:31.479Z |
| apex_recon.silver.dim_dsps | apex_recon.silver.dsp_daily_reports | 1 | 2026-10-05T15:32:31.479Z |
| apex_recon.silver.fx_rates | apex_recon.silver.dsp_daily_reports | 1 | 2026-10-05T15:32:31.479Z |
| apex_recon.bronze.dsp_reports_format_a | apex_recon.silver.dsp_reports_quarantine | 2 | 2026-10-05T15:32:35.470Z |
| apex_recon.bronze.dsp_reports_format_b | apex_recon.silver.dsp_reports_quarantine | 2 | 2026-10-05T15:32:35.470Z |
| apex_recon.bronze.dsp_reports_format_c | apex_recon.silver.dsp_reports_quarantine | 2 | 2026-10-05T15:32:35.470Z |
| apex_recon.silver.dim_deals | apex_recon.silver.dsp_reports_quarantine | 2 | 2026-10-05T15:32:35.470Z |
| apex_recon.silver.dim_dsps | apex_recon.silver.dsp_reports_quarantine | 2 | 2026-10-05T15:32:35.470Z |
| apex_recon.silver.fx_rates | apex_recon.silver.dsp_reports_quarantine | 2 | 2026-10-05T15:32:35.470Z |
| apex_recon.bronze.publisher_adserver_reports | apex_recon.silver.publisher_daily_reports | 1 | 2026-10-05T15:32:32.669Z |
