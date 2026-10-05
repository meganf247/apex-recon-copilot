-- Lakebase (Postgres) role and grants for the app service principal: read the synced queue, write case state.
CREATE EXTENSION IF NOT EXISTS databricks_auth;
SELECT databricks_create_role('9e942a9d-a89a-4549-bcda-db62c646ab87', 'SERVICE_PRINCIPAL');
GRANT CONNECT ON DATABASE apex_ops TO "9e942a9d-a89a-4549-bcda-db62c646ab87";
GRANT USAGE ON SCHEMA recon, serving TO "9e942a9d-a89a-4549-bcda-db62c646ab87";
GRANT SELECT ON ALL TABLES IN SCHEMA serving TO "9e942a9d-a89a-4549-bcda-db62c646ab87";
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA recon TO "9e942a9d-a89a-4549-bcda-db62c646ab87";
GRANT USAGE ON ALL SEQUENCES IN SCHEMA recon TO "9e942a9d-a89a-4549-bcda-db62c646ab87";
