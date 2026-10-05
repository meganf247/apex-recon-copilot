
```sql
SELECT current_user() AS principal, a.partner_team AS entitlement, a.can_see_revenue
FROM apex_recon.ops.recon_access a WHERE a.principal = current_user()
```
| principal | entitlement | can_see_revenue |
|---|---|---|
| megan.fogal@databricks.com | * | true |

```sql
SELECT partner_team, count(*) AS cases, round(sum(revenue_at_risk_usd), 0) AS revenue_at_risk_usd
FROM apex_recon.gold.dispute_queue GROUP BY partner_team ORDER BY partner_team
```
| partner_team | cases | revenue_at_risk_usd |
|---|---|---|
| Atlantic | 154 | 4034675.0 |
| Central | 194 | 5198282.0 |
| EMEA | 166 | 3686639.0 |
| Pacific | 441 | 1.4482205E7 |

```sql
UPDATE apex_recon.ops.recon_access SET partner_team = 'Atlantic', can_see_revenue = FALSE WHERE principal = current_user()
```
| num_affected_rows |
|---|
| 1 |

```sql
SELECT current_user() AS principal, a.partner_team AS entitlement, a.can_see_revenue
FROM apex_recon.ops.recon_access a WHERE a.principal = current_user()
```
| principal | entitlement | can_see_revenue |
|---|---|---|
| megan.fogal@databricks.com | Atlantic | false |

```sql
SELECT partner_team, count(*) AS cases, round(sum(revenue_at_risk_usd), 0) AS revenue_at_risk_usd
FROM apex_recon.gold.dispute_queue GROUP BY partner_team ORDER BY partner_team
```
| partner_team | cases | revenue_at_risk_usd |
|---|---|---|
| Atlantic | 154 |  |

```sql
SELECT case_id, dsp_name, partner_team, impression_gap_pct, revenue_gap_usd, revenue_at_risk_usd, predicted_root_cause
FROM apex_recon.gold.dispute_queue ORDER BY impression_gap_pct DESC LIMIT 5
```
| case_id | dsp_name | partner_team | impression_gap_pct | revenue_gap_usd | revenue_at_risk_usd | predicted_root_cause |
|---|---|---|---|---|---|---|
| CASE-2026-07-D00162 | Kestrel Demand | Atlantic | 52.639 |  |  | DEAL_ID_MISMAPPING |
| CASE-2026-07-D00302 | Kestrel Demand | Atlantic | 48.569 |  |  | DEAL_ID_MISMAPPING |
| CASE-2026-08-D00003 | Kestrel Demand | Atlantic | 42.897 |  |  | DEAL_ID_MISMAPPING |
| CASE-2026-09-D00117 | Cascade Reach | Atlantic | 36.276 |  |  | DEAL_ID_MISMAPPING |
| CASE-2026-07-D00497 | Kestrel Demand | Atlantic | 30.358 |  |  | DEAL_ID_MISMAPPING |

```sql
UPDATE apex_recon.ops.recon_access SET partner_team = '*', can_see_revenue = TRUE WHERE principal = current_user()
```
| num_affected_rows |
|---|
| 1 |

```sql
SELECT partner_team, count(*) AS cases, round(sum(revenue_at_risk_usd), 0) AS revenue_at_risk_usd
FROM apex_recon.gold.dispute_queue GROUP BY partner_team ORDER BY partner_team
```
| partner_team | cases | revenue_at_risk_usd |
|---|---|---|
| Atlantic | 154 | 4034675.0 |
| Central | 194 | 5198282.0 |
| EMEA | 166 | 3686639.0 |
| Pacific | 441 | 1.4482205E7 |

```sql
SELECT table_name, filter_name, target_columns FROM apex_recon.information_schema.row_filters WHERE table_name = 'dispute_queue'
```
| table_name | filter_name | target_columns |
|---|---|---|
| dispute_queue | apex_recon.ops.partner_access_filter | partner_team |

```sql
SELECT table_name, column_name, mask_name FROM apex_recon.information_schema.column_masks WHERE table_name = 'dispute_queue' ORDER BY column_name
```
| table_name | column_name | mask_name |
|---|---|---|
| dispute_queue | dsp_revenue_usd | apex_recon.ops.finance_only_usd |
| dispute_queue | revenue_at_risk_usd | apex_recon.ops.finance_only_usd |
| dispute_queue | revenue_gap_usd | apex_recon.ops.finance_only_usd |
| dispute_queue | ssp_revenue_usd | apex_recon.ops.finance_only_usd |

```sql
SELECT schema_name, table_name, tag_name, tag_value FROM apex_recon.information_schema.table_tags ORDER BY schema_name, table_name, tag_name
```
| schema_name | table_name | tag_name | tag_value |
|---|---|---|---|
| gold | case_workbench | domain | finance |
| gold | dispute_drafts | contains | genai_generated_text |
| gold | dispute_drafts | domain | finance |
| gold | dispute_queue | domain | finance |
| gold | recon_deal_month | domain | finance |
| gold | recon_partner_month | domain | finance |
| ml | ground_truth_root_causes | usage | evaluation_only |

```sql
SELECT table_name, column_name, tag_name, tag_value FROM apex_recon.information_schema.column_tags ORDER BY table_name, column_name
```
| table_name | column_name | tag_name | tag_value |
|---|---|---|---|
| dispute_queue | dsp_revenue_usd | sensitivity | internal |
| dispute_queue | revenue_at_risk_usd | sensitivity | internal |
| dispute_queue | revenue_gap_usd | sensitivity | internal |
| dispute_queue | ssp_revenue_usd | sensitivity | internal |

```sql
SELECT DISTINCT source_table_full_name, target_table_full_name
FROM system.access.table_lineage
WHERE target_table_full_name LIKE 'apex_recon.%' AND source_table_full_name LIKE 'apex_recon.%'
ORDER BY target_table_full_name, source_table_full_name
```
| source_table_full_name | target_table_full_name |
|---|---|
| apex_recon.gold.dispute_drafts | apex_recon.gold.case_workbench |
| apex_recon.gold.dispute_queue | apex_recon.gold.case_workbench |
| apex_recon.gold.dispute_queue | apex_recon.gold.dispute_drafts |
| apex_recon.gold.recon_deal_month | apex_recon.gold.dispute_queue |
| apex_recon.ml.discrepancy_features | apex_recon.gold.dispute_queue |
| apex_recon.ml.discrepancy_predictions | apex_recon.gold.dispute_queue |
| apex_recon.silver.dim_publishers | apex_recon.gold.publisher_recon_month |
| apex_recon.silver.publisher_daily_reports | apex_recon.gold.publisher_recon_month |
| apex_recon.silver.ssp_hourly | apex_recon.gold.publisher_recon_month |
| apex_recon.silver.dsp_daily_reports | apex_recon.gold.recon_deal_daily |
| apex_recon.silver.ssp_hourly | apex_recon.gold.recon_deal_daily |
| apex_recon.gold.recon_deal_daily | apex_recon.gold.recon_deal_month |
| apex_recon.silver.dim_deals | apex_recon.gold.recon_deal_month |
| apex_recon.silver.dim_dsps | apex_recon.gold.recon_deal_month |
| apex_recon.silver.dim_publishers | apex_recon.gold.recon_deal_month |
| apex_recon.gold.recon_deal_month | apex_recon.gold.recon_partner_month |
| apex_recon.gold.recon_deal_daily | apex_recon.ml.discrepancy_features |
| apex_recon.gold.recon_deal_month | apex_recon.ml.discrepancy_features |
| apex_recon.silver.ssp_hourly | apex_recon.ml.discrepancy_features |
| apex_recon.gold.case_workbench | apex_recon.ops.dispute_case_status |
| apex_recon.ops.lakebase_credit_approvals | apex_recon.ops.dispute_case_status |
| apex_recon.ops.lakebase_dispute_cases | apex_recon.ops.dispute_case_status |
| apex_recon.bronze.dispute_resolutions | apex_recon.silver.dispute_history |
| apex_recon.bronze.dsp_reports_format_a | apex_recon.silver.dsp_daily_reports |
| apex_recon.bronze.dsp_reports_format_b | apex_recon.silver.dsp_daily_reports |
| apex_recon.bronze.dsp_reports_format_c | apex_recon.silver.dsp_daily_reports |
| apex_recon.silver.dim_deals | apex_recon.silver.dsp_daily_reports |
| apex_recon.silver.dim_dsps | apex_recon.silver.dsp_daily_reports |
| apex_recon.silver.fx_rates | apex_recon.silver.dsp_daily_reports |
| apex_recon.bronze.dsp_reports_format_a | apex_recon.silver.dsp_reports_quarantine |
| apex_recon.bronze.dsp_reports_format_b | apex_recon.silver.dsp_reports_quarantine |
| apex_recon.bronze.dsp_reports_format_c | apex_recon.silver.dsp_reports_quarantine |
| apex_recon.silver.dim_deals | apex_recon.silver.dsp_reports_quarantine |
| apex_recon.silver.dim_dsps | apex_recon.silver.dsp_reports_quarantine |
| apex_recon.silver.fx_rates | apex_recon.silver.dsp_reports_quarantine |
| apex_recon.bronze.publisher_adserver_reports | apex_recon.silver.publisher_daily_reports |
