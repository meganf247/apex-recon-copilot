-- Unity Catalog access for the Reconciliation Workbench app's service principal.
GRANT USE CATALOG ON CATALOG apex_recon TO `{{APP_SP}}`;
GRANT USE SCHEMA, SELECT ON SCHEMA apex_recon.gold TO `{{APP_SP}}`;
GRANT USE SCHEMA, SELECT ON SCHEMA apex_recon.ops TO `{{APP_SP}}`;
MERGE INTO apex_recon.ops.recon_access t
USING (SELECT '{{APP_SP}}' AS principal, '*' AS partner_team, TRUE AS can_see_revenue) s ON t.principal = s.principal
WHEN MATCHED THEN UPDATE SET * WHEN NOT MATCHED THEN INSERT *;
