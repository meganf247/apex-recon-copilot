-- Lakebase is registered in Unity Catalog as apex_recon_ops (project apex-recon-lb, branch production,
-- database databricks_postgres). Rows the app writes to Postgres are queryable from SQL and Genie immediately.
SELECT catalog_name, catalog_owner, comment FROM system.information_schema.catalogs WHERE catalog_name = 'apex_recon_ops';

SELECT case_id, status, resolution, confirmed_root_cause, recovered_usd, owner, updated_at
FROM apex_recon_ops.recon.dispute_cases ORDER BY updated_at DESC;

SELECT event_id, case_id, event_type, actor, created_at FROM apex_recon_ops.recon.case_events ORDER BY event_id;

SELECT case_id, amount_usd, approved_by, reason, approved_at FROM apex_recon_ops.recon.credit_approvals;

-- The live view Genie uses: workbench queue joined to Lakebase case state
SELECT status, count(*) AS cases, round(sum(revenue_at_risk_usd)) AS revenue_at_risk_usd,
       round(sum(recovered_usd)) AS recovered_usd, round(sum(credited_usd)) AS credited_usd
FROM apex_recon.ops.dispute_case_status GROUP BY status ORDER BY status;

-- The synced serving table the app reads (Lakebase serving.case_workbench), via the same catalog
SELECT count(*) AS cases_in_lakebase_serving_queue FROM apex_recon_ops.serving.case_workbench;
