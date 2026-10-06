-- Live dispute workflow status, read straight from Lakebase through its Unity Catalog database catalog
-- (apex_recon_ops = Lakebase project apex-recon-lb, branch production, database databricks_postgres).
-- Analysts' actions in the app show up here, and in Genie, the moment they're committed. No copy job.

CREATE OR REPLACE VIEW apex_recon.ops.dispute_case_status
COMMENT 'Current dispute workflow status per case, live from Lakebase (apex_recon_ops.recon.*), joined to the open-case queue. Cases with no workbench activity are OPEN.'
AS SELECT q.case_id, q.billing_month, q.dsp_id, q.dsp_name, q.partner_team, q.deal_id,
          coalesce(c.status, 'OPEN') AS status, c.resolution, c.owner, c.confirmed_root_cause, q.predicted_root_cause,
          q.revenue_at_risk_usd, coalesce(CAST(c.recovered_usd AS DOUBLE), 0) AS recovered_usd,
          coalesce(a.credited_usd, 0) AS credited_usd, c.updated_at AS last_activity_at
   FROM apex_recon.gold.case_workbench q
   LEFT JOIN apex_recon_ops.recon.dispute_cases c USING (case_id)
   LEFT JOIN (SELECT case_id, CAST(sum(amount_usd) AS DOUBLE) AS credited_usd
              FROM apex_recon_ops.recon.credit_approvals GROUP BY case_id) a USING (case_id);

DROP TABLE IF EXISTS apex_recon.ops.lakebase_dispute_cases;
DROP TABLE IF EXISTS apex_recon.ops.lakebase_case_events;
DROP TABLE IF EXISTS apex_recon.ops.lakebase_credit_approvals;
