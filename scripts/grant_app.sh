#!/usr/bin/env bash
# Grant the Reconciliation Workbench app's service principal its Unity Catalog and Lakebase access.
# Usage: scripts/grant_app.sh [profile]
set -euo pipefail
PROFILE=${1:-megan-fevm2}
ENDPOINT=projects/apex-recon-lb/branches/production/endpoints/primary
PGHOST=ep-cold-cell-d2f24olw.database.us-east-1.cloud.databricks.com
cd "$(dirname "$0")/.."
SP=$(databricks apps get apex-recon-workbench -p "$PROFILE" -o json | python3 -c "import json,sys; print(json.load(sys.stdin)['service_principal_client_id'])")
echo "app service principal: $SP"
sed "s/{{APP_SP}}/$SP/g" src/06_app_grants.sql > /tmp/app_grants.sql
python3 scripts/run_sql.py /tmp/app_grants.sql --profile "$PROFILE"
databricks postgres create-role projects/apex-recon-lb/branches/production -p "$PROFILE" -o json \
  --json "{\"spec\": {\"identity_type\": \"SERVICE_PRINCIPAL\", \"postgres_role\": \"$SP\"}}" >/dev/null 2>&1 || echo "(role exists)"
TOKEN=$(databricks postgres generate-database-credential "$ENDPOINT" -p "$PROFILE" -o json | python3 -c "import json,sys; print(json.load(sys.stdin)['token'])")
sed "s/{{APP_SP}}/$SP/g" src/06_app_grants_lakebase.sql | \
  PGPASSWORD=$TOKEN psql "host=$PGHOST dbname=databricks_postgres user=$(databricks current-user me -p "$PROFILE" -o json | python3 -c "import json,sys; print(json.load(sys.stdin)['userName'])") sslmode=require" -v ON_ERROR_STOP=1
