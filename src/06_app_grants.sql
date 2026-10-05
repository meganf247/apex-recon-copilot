-- Unity Catalog access for the Reconciliation Workbench app's service principal.
GRANT USE CATALOG ON CATALOG apex_recon TO `9e942a9d-a89a-4549-bcda-db62c646ab87`;
GRANT USE SCHEMA, SELECT ON SCHEMA apex_recon.gold TO `9e942a9d-a89a-4549-bcda-db62c646ab87`;
GRANT USE SCHEMA, SELECT ON SCHEMA apex_recon.ops TO `9e942a9d-a89a-4549-bcda-db62c646ab87`;
MERGE INTO apex_recon.ops.recon_access t
USING (SELECT '9e942a9d-a89a-4549-bcda-db62c646ab87' AS principal, '*' AS partner_team, TRUE AS can_see_revenue) s ON t.principal = s.principal
WHEN MATCHED THEN UPDATE SET * WHEN NOT MATCHED THEN INSERT *;
