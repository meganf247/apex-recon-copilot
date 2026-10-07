
```sql
WITH current_tables AS (
  SELECT concat(table_catalog, '.', table_schema, '.', table_name) AS t FROM apex_recon.information_schema.tables
)
SELECT source_table_full_name, target_table_full_name, count(*) AS lineage_events, max(event_time) AS last_seen
FROM system.access.table_lineage
WHERE source_table_full_name IN (SELECT t FROM current_tables) AND target_table_full_name IN (SELECT t FROM current_tables)
GROUP BY 1, 2 ORDER BY 2, 1
```
| source_table_full_name | target_table_full_name | lineage_events | last_seen |
|---|---|---|---|
| apex_recon.gold.dispute_drafts | apex_recon.gold.case_workbench | 4 | 2026-10-07T15:15:45.534Z |
| apex_recon.gold.dispute_queue | apex_recon.gold.case_workbench | 4 | 2026-10-07T15:15:45.534Z |
| apex_recon.gold.dispute_queue | apex_recon.gold.dispute_drafts | 4 | 2026-10-07T15:15:34.217Z |
| apex_recon.gold.recon_deal_month | apex_recon.gold.dispute_queue | 5 | 2026-10-07T15:13:13.140Z |
| apex_recon.ml.discrepancy_predictions | apex_recon.gold.dispute_queue | 5 | 2026-10-07T15:13:13.140Z |
| apex_recon.ml.root_cause_features | apex_recon.gold.dispute_queue | 1 | 2026-10-07T15:13:13.140Z |
| apex_recon.silver.deals | apex_recon.gold.recon_deal_month | 2 | 2026-10-07T15:28:06.745Z |
| apex_recon.silver.dsp_daily | apex_recon.gold.recon_deal_month | 2 | 2026-10-07T15:28:06.745Z |
| apex_recon.silver.dsps | apex_recon.gold.recon_deal_month | 2 | 2026-10-07T15:28:06.745Z |
| apex_recon.silver.ssp_daily | apex_recon.gold.recon_deal_month | 2 | 2026-10-07T15:28:06.745Z |
| apex_recon.gold.recon_deal_month | apex_recon.gold.recon_partner_month | 9 | 2026-10-07T15:28:07.407Z |
| apex_recon.gold.recon_deal_month | apex_recon.ml.root_cause_features | 1 | 2026-10-07T15:12:34.949Z |
| apex_recon.silver.dsp_daily | apex_recon.ml.root_cause_features | 1 | 2026-10-07T15:12:34.949Z |
| apex_recon.silver.ssp_daily | apex_recon.ml.root_cause_features | 1 | 2026-10-07T15:12:34.949Z |
| apex_recon.gold.case_workbench | apex_recon.ops.dispute_case_status | 25 | 2026-10-07T15:22:43.500Z |
| apex_recon.bronze.dsp_reports | apex_recon.silver.dsp_daily | 2 | 2026-10-07T15:27:55.618Z |
| apex_recon.bronze.ssp_logs | apex_recon.silver.ssp_daily | 2 | 2026-10-07T15:28:03.248Z |
