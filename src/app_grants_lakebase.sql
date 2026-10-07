-- Lakebase (Postgres) grants for the app service principal: read the synced queue, write case state.
-- The Postgres role itself is created with the Lakebase API in scripts/grant_app.sh.
GRANT CONNECT ON DATABASE databricks_postgres TO "{{APP_SP}}";
GRANT USAGE ON SCHEMA recon, serving TO "{{APP_SP}}";
GRANT SELECT ON ALL TABLES IN SCHEMA serving TO "{{APP_SP}}";
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA recon TO "{{APP_SP}}";
GRANT USAGE ON ALL SEQUENCES IN SCHEMA recon TO "{{APP_SP}}";
