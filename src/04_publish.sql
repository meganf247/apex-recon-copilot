-- Publish step (runs after the ML notebook):
--   1. Unity Catalog governance on the work queue
--   2. Live case-status view over Lakebase
--
-- 1 · Governance for partner revenue data.
--   * Row filter: Finance sees every partner; a partner manager sees only the DSPs their team owns.
--   * Column mask: dollar amounts are Finance-confidential; everyone else sees NULL.
--   * Both policies are driven by one access table keyed on the signed-in principal, so access changes are a
--     row update (auditable in table history) rather than a code change. The access table and the two policy
--     functions are created in src/00_setup_uc.sql, because the pipeline applies them too.
--   * Where each table is governed:
--       gold.recon_deal_month, gold.recon_partner_month  row filter + masks, declared in src/02_pipeline.py
--       gold.dispute_queue                               row filter + masks, applied below (rebuilt by the ML notebook)
--       gold.case_workbench, gold.dispute_drafts, ml.*   no filter: the Lakebase sync source, model inputs and
--                                                         drafts. SELECT is granted only to Finance and the app's
--                                                         service principal (src/app_grants.sql), never to partner managers.
--   * Tags classify the sensitive objects; comments document every table for analysts and Genie.

-- Billing Ops work queue: row filter + revenue masks.
ALTER TABLE apex_recon.gold.dispute_queue SET ROW FILTER apex_recon.ops.partner_access_filter ON (partner_team);
ALTER TABLE apex_recon.gold.dispute_queue ALTER COLUMN ssp_revenue_usd     SET MASK apex_recon.ops.finance_only_usd;
ALTER TABLE apex_recon.gold.dispute_queue ALTER COLUMN dsp_revenue_usd     SET MASK apex_recon.ops.finance_only_usd;
ALTER TABLE apex_recon.gold.dispute_queue ALTER COLUMN revenue_gap_usd     SET MASK apex_recon.ops.finance_only_usd;
ALTER TABLE apex_recon.gold.dispute_queue ALTER COLUMN revenue_at_risk_usd SET MASK apex_recon.ops.finance_only_usd;
ALTER TABLE apex_recon.gold.dispute_queue ALTER COLUMN apex_exposure_usd   SET MASK apex_recon.ops.finance_only_usd;

-- Classification tags (domain uses the workspace's governed tag policy values)
ALTER TABLE apex_recon.gold.dispute_queue          SET TAGS ('domain' = 'finance');
ALTER TABLE apex_recon.gold.case_workbench         SET TAGS ('domain' = 'finance');
ALTER TABLE apex_recon.gold.dispute_drafts         SET TAGS ('domain' = 'finance', 'contains' = 'genai_generated_text');
ALTER TABLE apex_recon.gold.recon_deal_month       SET TAGS ('domain' = 'finance');
ALTER TABLE apex_recon.gold.recon_partner_month    SET TAGS ('domain' = 'finance');
ALTER TABLE apex_recon.ml.ground_truth_root_causes SET TAGS ('usage' = 'evaluation_only');
ALTER TABLE apex_recon.gold.dispute_queue ALTER COLUMN ssp_revenue_usd     SET TAGS ('sensitivity' = 'internal');
ALTER TABLE apex_recon.gold.dispute_queue ALTER COLUMN dsp_revenue_usd     SET TAGS ('sensitivity' = 'internal');
ALTER TABLE apex_recon.gold.dispute_queue ALTER COLUMN revenue_gap_usd     SET TAGS ('sensitivity' = 'internal');
ALTER TABLE apex_recon.gold.dispute_queue ALTER COLUMN revenue_at_risk_usd SET TAGS ('sensitivity' = 'internal');
ALTER TABLE apex_recon.gold.dispute_queue ALTER COLUMN apex_exposure_usd   SET TAGS ('sensitivity' = 'internal');

-- 2 · Live dispute workflow status, read straight from Lakebase through its Unity Catalog database catalog
-- (apex_recon_ops = Lakebase project apex-recon-lb, branch production, database databricks_postgres).
-- Analysts' actions in the app show up here, and in Genie, the moment they're committed. No copy job.
-- Built on the governed gold.dispute_queue, so the row filter and revenue masks apply to whoever queries the view.

CREATE OR REPLACE VIEW apex_recon.ops.dispute_case_status
COMMENT 'Current dispute workflow status per case, live from Lakebase (apex_recon_ops.recon.*), joined to the open-case queue. Cases with no workbench activity are OPEN. Inherits the queue row filter and revenue masks.'
AS SELECT q.case_id, q.billing_month, q.dsp_id, q.dsp_name, q.partner_team, q.deal_id,
          coalesce(c.status, 'OPEN') AS status, c.resolution, c.owner, c.confirmed_root_cause, q.predicted_root_cause,
          q.revenue_at_risk_usd, q.apex_exposure_usd,
          CASE WHEN q.revenue_at_risk_usd IS NOT NULL THEN coalesce(CAST(c.recovered_usd AS DOUBLE), 0) END AS recovered_usd,
          CASE WHEN q.revenue_at_risk_usd IS NOT NULL THEN coalesce(a.credited_usd, 0) END AS credited_usd,
          c.updated_at AS last_activity_at
   FROM apex_recon.gold.dispute_queue q
   LEFT JOIN apex_recon_ops.recon.dispute_cases c USING (case_id)
   LEFT JOIN (SELECT case_id, CAST(sum(amount_usd) AS DOUBLE) AS credited_usd
              FROM apex_recon_ops.recon.credit_approvals GROUP BY case_id) a USING (case_id);

