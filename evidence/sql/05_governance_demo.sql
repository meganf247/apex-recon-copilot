-- Governance proof: the same query returns different rows and masked dollars depending on the principal's entitlement.
-- Step 1: signed-in user has Finance access ('*', can_see_revenue = TRUE).
SELECT current_user() AS principal, a.partner_team AS entitlement, a.can_see_revenue
FROM apex_recon.ops.recon_access a WHERE a.principal = current_user();

SELECT partner_team, count(*) AS cases, round(sum(revenue_at_risk_usd), 0) AS revenue_at_risk_usd
FROM apex_recon.gold.dispute_queue GROUP BY partner_team ORDER BY partner_team;

-- Step 2: re-scope the same user to an Atlantic partner manager without revenue visibility.
UPDATE apex_recon.ops.recon_access SET partner_team = 'Atlantic', can_see_revenue = FALSE WHERE principal = current_user();

SELECT current_user() AS principal, a.partner_team AS entitlement, a.can_see_revenue
FROM apex_recon.ops.recon_access a WHERE a.principal = current_user();

SELECT partner_team, count(*) AS cases, round(sum(revenue_at_risk_usd), 0) AS revenue_at_risk_usd
FROM apex_recon.gold.dispute_queue GROUP BY partner_team ORDER BY partner_team;

SELECT case_id, dsp_name, partner_team, impression_gap_pct, revenue_gap_usd, revenue_at_risk_usd, predicted_root_cause
FROM apex_recon.gold.dispute_queue ORDER BY impression_gap_pct DESC LIMIT 5;

-- The same policies hold on every other governed surface: the pipeline's gold tables and the live case-status view.
SELECT partner_team, count(*) AS dsp_months, round(sum(ssp_revenue_usd)) AS ssp_revenue_usd, round(sum(revenue_at_risk_usd)) AS revenue_at_risk_usd
FROM apex_recon.gold.recon_partner_month GROUP BY partner_team ORDER BY partner_team;

SELECT partner_team, count(*) AS deal_months, round(sum(apex_exposure_usd)) AS apex_exposure_usd
FROM apex_recon.gold.recon_deal_month GROUP BY partner_team ORDER BY partner_team;

SELECT partner_team, count(*) AS cases, round(sum(revenue_at_risk_usd)) AS revenue_at_risk_usd, round(sum(recovered_usd)) AS recovered_usd
FROM apex_recon.ops.dispute_case_status GROUP BY partner_team ORDER BY partner_team;

-- Step 3: restore Finance access.
UPDATE apex_recon.ops.recon_access SET partner_team = '*', can_see_revenue = TRUE WHERE principal = current_user();

SELECT partner_team, count(*) AS cases, round(sum(revenue_at_risk_usd), 0) AS revenue_at_risk_usd
FROM apex_recon.gold.dispute_queue GROUP BY partner_team ORDER BY partner_team;

-- Policies attached to the table, and tags
SELECT table_schema, table_name, filter_name, target_columns FROM apex_recon.information_schema.row_filters ORDER BY 1, 2;
SELECT table_schema, table_name, column_name, mask_name FROM apex_recon.information_schema.column_masks ORDER BY 1, 2, 3;

-- Ungoverned working tables (Lakebase sync source, model inputs, drafts) are readable only by Finance and the app
SHOW GRANTS ON TABLE apex_recon.gold.case_workbench;
SELECT schema_name, table_name, tag_name, tag_value FROM apex_recon.information_schema.table_tags ORDER BY schema_name, table_name, tag_name;
SELECT table_name, column_name, tag_name, tag_value FROM apex_recon.information_schema.column_tags ORDER BY table_name, column_name;

-- Lineage: upstream sources of the work queue, from UC system tables
SELECT DISTINCT source_table_full_name, target_table_full_name
FROM system.access.table_lineage
WHERE target_table_full_name LIKE 'apex_recon.%' AND source_table_full_name LIKE 'apex_recon.%'
ORDER BY target_table_full_name, source_table_full_name;
