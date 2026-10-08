
```sql
SELECT table_schema, table_name, filter_name, target_columns
FROM apex_recon.information_schema.row_filters ORDER BY 1, 2
```
| table_schema | table_name | filter_name | target_columns |
|---|---|---|---|
| gold | dispute_queue | apex_recon.ops.partner_access_filter | partner_team |

```sql
SELECT table_schema, table_name, column_name, mask_name
FROM apex_recon.information_schema.column_masks ORDER BY 1, 2, 3
```
| table_schema | table_name | column_name | mask_name |
|---|---|---|---|
| gold | dispute_queue | dsp_revenue_usd | apex_recon.ops.finance_only_usd |
| gold | dispute_queue | revenue_at_risk_usd | apex_recon.ops.finance_only_usd |
| gold | dispute_queue | revenue_gap_usd | apex_recon.ops.finance_only_usd |
| gold | dispute_queue | ssp_revenue_usd | apex_recon.ops.finance_only_usd |

```sql
SELECT schema_name, table_name, tag_name, tag_value
FROM apex_recon.information_schema.table_tags ORDER BY 1, 2, 3
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
SELECT principal, partner_team, can_see_revenue FROM apex_recon.ops.recon_access ORDER BY 1
```
| principal | partner_team | can_see_revenue |
|---|---|---|
| 285dda25-5ce5-4119-9ee0-d2bab16a3e3f | * | true |
| megan.fogal@databricks.com | * | true |
| pm.atlantic@apexexchange.example | Atlantic | false |
| pm.emea@apexexchange.example | EMEA | false |

```sql
SELECT status, count(*) AS cases, round(sum(revenue_at_risk_usd)) AS revenue_at_risk_usd
FROM apex_recon.ops.dispute_case_status GROUP BY status ORDER BY status
```
| status | cases | revenue_at_risk_usd |
|---|---|---|
| OPEN | 714 | 1.7763495E7 |
| RESOLVED | 1 | 349977.0 |
