
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
| apex_recon.gold.dispute_drafts | apex_recon.gold.case_workbench | 9 | 2026-11-02T15:56:14.811Z |
| apex_recon.gold.dispute_queue | apex_recon.gold.case_workbench | 9 | 2026-11-02T15:56:14.811Z |
| apex_recon.gold.dispute_queue | apex_recon.gold.dispute_drafts | 9 | 2026-11-02T15:56:04.901Z |
| apex_recon.gold.recon_deal_month | apex_recon.gold.dispute_queue | 10 | 2026-11-02T15:53:46.137Z |
| apex_recon.ml.discrepancy_predictions | apex_recon.gold.dispute_queue | 10 | 2026-11-02T15:53:46.137Z |
| apex_recon.ml.root_cause_features | apex_recon.gold.dispute_queue | 6 | 2026-11-02T15:53:46.137Z |
| apex_recon.silver.deals | apex_recon.gold.recon_deal_month | 9 | 2026-11-02T15:52:25.787Z |
| apex_recon.silver.dsp_daily | apex_recon.gold.recon_deal_month | 5 | 2026-11-02T15:52:25.787Z |
| apex_recon.silver.dsps | apex_recon.gold.recon_deal_month | 9 | 2026-11-02T15:52:25.787Z |
| apex_recon.silver.ssp_daily | apex_recon.gold.recon_deal_month | 5 | 2026-11-02T15:52:25.787Z |
| apex_recon.gold.recon_deal_month | apex_recon.gold.recon_partner_month | 15 | 2026-11-02T15:52:30.657Z |
| apex_recon.gold.recon_deal_month | apex_recon.ml.root_cause_features | 6 | 2026-11-02T15:53:02.888Z |
| apex_recon.silver.dsp_daily | apex_recon.ml.root_cause_features | 6 | 2026-11-02T15:53:02.888Z |
| apex_recon.silver.ssp_daily | apex_recon.ml.root_cause_features | 6 | 2026-11-02T15:53:02.888Z |
| apex_recon.gold.case_workbench | apex_recon.ops.dispute_case_status | 29 | 2026-10-08T18:15:40.947Z |
| apex_recon.gold.dispute_queue | apex_recon.ops.dispute_case_status | 2 | 2026-11-02T15:56:38.171Z |
| apex_recon.gold.case_workbench | apex_recon.serving.case_workbench | 1 | 2026-11-02T15:57:15.048Z |
| apex_recon.bronze.dsp_reports | apex_recon.silver.dsp_daily | 6 | 2026-11-02T15:52:16.342Z |
| apex_recon.bronze.ssp_logs | apex_recon.silver.ssp_daily | 6 | 2026-11-02T15:52:21.692Z |
