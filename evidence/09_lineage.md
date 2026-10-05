
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
| apex_recon.silver.dim_publishers | apex_recon.gold.publisher_recon_month | 3 | 2026-10-05T17:16:42.057Z |
| apex_recon.silver.publisher_daily_reports | apex_recon.gold.publisher_recon_month | 3 | 2026-10-05T17:16:42.057Z |
| apex_recon.silver.ssp_hourly | apex_recon.gold.publisher_recon_month | 3 | 2026-10-05T17:16:42.057Z |
| apex_recon.silver.dsp_daily_reports | apex_recon.gold.recon_deal_daily | 3 | 2026-10-05T17:16:42.904Z |
| apex_recon.silver.ssp_hourly | apex_recon.gold.recon_deal_daily | 3 | 2026-10-05T17:16:42.904Z |
| apex_recon.gold.recon_deal_daily | apex_recon.gold.recon_deal_month | 4 | 2026-10-05T17:16:46.125Z |
| apex_recon.silver.dim_deals | apex_recon.gold.recon_deal_month | 4 | 2026-10-05T17:16:46.125Z |
| apex_recon.silver.dim_dsps | apex_recon.gold.recon_deal_month | 4 | 2026-10-05T17:16:46.125Z |
| apex_recon.silver.dim_publishers | apex_recon.gold.recon_deal_month | 4 | 2026-10-05T17:16:46.125Z |
| apex_recon.gold.recon_deal_month | apex_recon.gold.recon_partner_month | 4 | 2026-10-05T17:16:49.369Z |
| apex_recon.gold.recon_deal_daily | apex_recon.ml.discrepancy_features | 4 | 2026-10-05T17:16:53.658Z |
| apex_recon.gold.recon_deal_month | apex_recon.ml.discrepancy_features | 4 | 2026-10-05T17:16:53.658Z |
| apex_recon.silver.ssp_hourly | apex_recon.ml.discrepancy_features | 4 | 2026-10-05T17:16:53.658Z |
| apex_recon.gold.case_workbench | apex_recon.ops.dispute_case_status | 7 | 2026-10-05T16:33:23.552Z |
| apex_recon.ops.lakebase_credit_approvals | apex_recon.ops.dispute_case_status | 7 | 2026-10-05T16:33:23.552Z |
| apex_recon.ops.lakebase_dispute_cases | apex_recon.ops.dispute_case_status | 7 | 2026-10-05T16:33:23.552Z |
| apex_recon.bronze.dispute_resolutions | apex_recon.silver.dispute_history | 4 | 2026-10-05T17:16:25.277Z |
| apex_recon.bronze.dsp_reports_format_a | apex_recon.silver.dsp_daily_reports | 2 | 2026-10-05T17:16:24.067Z |
| apex_recon.bronze.dsp_reports_format_b | apex_recon.silver.dsp_daily_reports | 2 | 2026-10-05T17:16:24.067Z |
| apex_recon.bronze.dsp_reports_format_c | apex_recon.silver.dsp_daily_reports | 2 | 2026-10-05T17:16:24.067Z |
| apex_recon.silver.dim_deals | apex_recon.silver.dsp_daily_reports | 2 | 2026-10-05T17:16:24.067Z |
| apex_recon.silver.dim_dsps | apex_recon.silver.dsp_daily_reports | 2 | 2026-10-05T17:16:24.067Z |
| apex_recon.silver.fx_rates | apex_recon.silver.dsp_daily_reports | 2 | 2026-10-05T17:16:24.067Z |
| apex_recon.bronze.dsp_reports_format_a | apex_recon.silver.dsp_reports_quarantine | 3 | 2026-10-05T17:16:24.175Z |
| apex_recon.bronze.dsp_reports_format_b | apex_recon.silver.dsp_reports_quarantine | 3 | 2026-10-05T17:16:24.175Z |
| apex_recon.bronze.dsp_reports_format_c | apex_recon.silver.dsp_reports_quarantine | 3 | 2026-10-05T17:16:24.175Z |
| apex_recon.silver.dim_deals | apex_recon.silver.dsp_reports_quarantine | 3 | 2026-10-05T17:16:24.175Z |
| apex_recon.silver.dim_dsps | apex_recon.silver.dsp_reports_quarantine | 3 | 2026-10-05T17:16:24.175Z |
| apex_recon.silver.fx_rates | apex_recon.silver.dsp_reports_quarantine | 3 | 2026-10-05T17:16:24.175Z |
| apex_recon.bronze.publisher_adserver_reports | apex_recon.silver.publisher_daily_reports | 2 | 2026-10-05T17:16:26.222Z |
