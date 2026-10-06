
```sql
SELECT catalog_name, catalog_owner, comment FROM system.information_schema.catalogs WHERE catalog_name = 'apex_recon_ops'
```
| catalog_name | catalog_owner | comment |
|---|---|---|
| apex_recon_ops | megan.fogal@databricks.com |  |

```sql
SELECT case_id, status, resolution, confirmed_root_cause, recovered_usd, owner, updated_at
FROM apex_recon_ops.recon.dispute_cases ORDER BY updated_at DESC
```
| case_id | status | resolution | confirmed_root_cause | recovered_usd | owner | updated_at |
|---|---|---|---|---|---|---|
| CASE-2026-09-D00734 | RESOLVED | CREDIT_ISSUED | IVT_FILTERING | 0.00 | billing.analyst@apexexchange.example | 2026-10-06T17:00:22.029Z |

```sql
SELECT event_id, case_id, event_type, actor, created_at FROM apex_recon_ops.recon.case_events ORDER BY event_id
```
| event_id | case_id | event_type | actor | created_at |
|---|---|---|---|---|
| 1 | CASE-2026-09-D00734 | CREATED | billing.analyst@apexexchange.example | 2026-10-06T17:00:06.077Z |
| 2 | CASE-2026-09-D00734 | EMAIL_SENT | billing.analyst@apexexchange.example | 2026-10-06T17:00:13.437Z |
| 3 | CASE-2026-09-D00734 | STATUS_CHANGED | billing.analyst@apexexchange.example | 2026-10-06T17:00:22.029Z |

```sql
SELECT case_id, amount_usd, approved_by, reason, approved_at FROM apex_recon_ops.recon.credit_approvals
```
| case_id | amount_usd | approved_by | reason | approved_at |
|---|---|---|---|---|
| CASE-2026-09-D00734 | 215005.82 | billing.analyst@apexexchange.example | IVT_FILTERING | 2026-10-06T17:00:22.029Z |

```sql
SELECT status, count(*) AS cases, round(sum(revenue_at_risk_usd)) AS revenue_at_risk_usd,
       round(sum(recovered_usd)) AS recovered_usd, round(sum(credited_usd)) AS credited_usd
FROM apex_recon.ops.dispute_case_status GROUP BY status ORDER BY status
```
| status | cases | revenue_at_risk_usd | recovered_usd | credited_usd |
|---|---|---|---|---|
| OPEN | 954 | 2.7186795E7 | 0.0 | 0.0 |
| RESOLVED | 1 | 215006.0 | 0.0 | 215006.0 |

```sql
SELECT count(*) AS cases_in_lakebase_serving_queue FROM apex_recon_ops.serving.case_workbench
```
| cases_in_lakebase_serving_queue |
|---|
| 955 |
