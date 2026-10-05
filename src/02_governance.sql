-- Unity Catalog governance for partner revenue data.
--   * Finance and Data Engineering see every partner; partner managers see only DSPs their team owns (row filter).
--   * Dollar amounts are Finance-confidential: masked for anyone outside apex_finance (column mask).
--   * Governed tags classify the sensitive columns; comments document every gold table for analysts and Genie.

CREATE TABLE IF NOT EXISTS apex_recon.ops.partner_team_access (
  group_name   STRING COMMENT 'Workspace group of partner managers',
  partner_team STRING COMMENT 'Partner team that owns a set of DSP relationships (matches dim_dsps.partner_team)'
) COMMENT 'Which partner-manager group may see which DSP partner team. Drives the partner row filter.';

INSERT OVERWRITE apex_recon.ops.partner_team_access VALUES
  ('apex_partner_atlantic', 'Atlantic'),
  ('apex_partner_pacific',  'Pacific'),
  ('apex_partner_central',  'Central'),
  ('apex_partner_emea',     'EMEA');

CREATE OR REPLACE FUNCTION apex_recon.ops.partner_team_filter(team STRING)
RETURNS BOOLEAN
COMMENT 'Row filter: apex_finance and apex_data_engineering see all partners; partner managers only see DSPs owned by their team.'
RETURN is_account_group_member('apex_finance')
    OR is_account_group_member('apex_data_engineering')
    OR EXISTS (SELECT 1 FROM apex_recon.ops.partner_team_access a
               WHERE a.partner_team = team AND is_account_group_member(a.group_name));

CREATE OR REPLACE FUNCTION apex_recon.ops.finance_only_usd(amount DOUBLE)
RETURNS DOUBLE
COMMENT 'Column mask: dollar amounts are visible to apex_finance only; everyone else sees NULL.'
RETURN CASE WHEN is_account_group_member('apex_finance') THEN amount ELSE NULL END;

-- Work queue (plain Delta table written by 04_score_and_draft): row filter + revenue masks.
ALTER TABLE apex_recon.gold.dispute_queue SET ROW FILTER apex_recon.ops.partner_team_filter ON (partner_team);
ALTER TABLE apex_recon.gold.dispute_queue ALTER COLUMN ssp_revenue_usd     SET MASK apex_recon.ops.finance_only_usd;
ALTER TABLE apex_recon.gold.dispute_queue ALTER COLUMN dsp_revenue_usd     SET MASK apex_recon.ops.finance_only_usd;
ALTER TABLE apex_recon.gold.dispute_queue ALTER COLUMN revenue_gap_usd     SET MASK apex_recon.ops.finance_only_usd;
ALTER TABLE apex_recon.gold.dispute_queue ALTER COLUMN revenue_at_risk_usd SET MASK apex_recon.ops.finance_only_usd;

-- Classification tags
ALTER TABLE apex_recon.gold.dispute_queue SET TAGS ('domain' = 'billing', 'data_owner' = 'revenue_accounting');
ALTER TABLE apex_recon.gold.dispute_queue ALTER COLUMN ssp_revenue_usd     SET TAGS ('data_classification' = 'financial_confidential');
ALTER TABLE apex_recon.gold.dispute_queue ALTER COLUMN dsp_revenue_usd     SET TAGS ('data_classification' = 'financial_confidential');
ALTER TABLE apex_recon.gold.dispute_queue ALTER COLUMN revenue_gap_usd     SET TAGS ('data_classification' = 'financial_confidential');
ALTER TABLE apex_recon.gold.dispute_queue ALTER COLUMN revenue_at_risk_usd SET TAGS ('data_classification' = 'financial_confidential');
ALTER TABLE apex_recon.gold.dispute_drafts SET TAGS ('domain' = 'billing', 'contains' = 'genai_generated_text');
ALTER TABLE apex_recon.ml.ground_truth_root_causes SET TAGS ('usage' = 'evaluation_only');

-- Access for the teams
GRANT USE CATALOG ON CATALOG apex_recon TO `apex_finance`;
GRANT USE CATALOG ON CATALOG apex_recon TO `apex_data_engineering`;
GRANT USE SCHEMA, SELECT ON SCHEMA apex_recon.gold TO `apex_finance`;
GRANT USE SCHEMA, SELECT ON SCHEMA apex_recon.gold TO `apex_data_engineering`;
GRANT ALL PRIVILEGES ON SCHEMA apex_recon.bronze TO `apex_data_engineering`;
GRANT ALL PRIVILEGES ON SCHEMA apex_recon.silver TO `apex_data_engineering`;
