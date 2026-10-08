-- What the publish step (src/04_publish.sql) applied, read back from Unity Catalog after the build run

-- Row filter on the dispute queue
SELECT table_schema, table_name, filter_name, target_columns
FROM apex_recon.information_schema.row_filters ORDER BY 1, 2;

-- Column masks (dollar amounts visible to Finance only)
SELECT table_schema, table_name, column_name, mask_name
FROM apex_recon.information_schema.column_masks ORDER BY 1, 2, 3;

-- Governed tags
SELECT schema_name, table_name, tag_name, tag_value
FROM apex_recon.information_schema.table_tags ORDER BY 1, 2, 3;

-- Access table that drives the filter and masks
SELECT principal, partner_team, can_see_revenue FROM apex_recon.ops.recon_access ORDER BY 1;

-- Live view over Lakebase exists and returns rows
SELECT status, count(*) AS cases, round(sum(revenue_at_risk_usd)) AS revenue_at_risk_usd
FROM apex_recon.ops.dispute_case_status GROUP BY status ORDER BY status;
