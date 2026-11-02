#!/usr/bin/env bash
# (Re)create the Lakebase synced table that serves gold.case_workbench to the app as serving.case_workbench.
# Run once after the first job run, and again whenever the columns of gold.case_workbench change
# (a snapshot synced table keeps the schema it was created with). Then rerun scripts/grant_app.sh.
# Usage: scripts/create_synced_table.sh [profile]
set -euo pipefail
PROFILE=${1:-megan-fevm2}
NAME=apex_recon.serving.case_workbench
if databricks postgres get-synced-table "synced_tables/$NAME" -p "$PROFILE" >/dev/null 2>&1; then
  echo "deleting existing synced table $NAME"
  databricks postgres delete-synced-table "synced_tables/$NAME" -p "$PROFILE"
  while databricks postgres get-synced-table "synced_tables/$NAME" -p "$PROFILE" >/dev/null 2>&1; do sleep 5; done
fi
databricks postgres create-synced-table "$NAME" -p "$PROFILE" --json '{"spec": {
  "source_table_full_name": "apex_recon.gold.case_workbench", "primary_key_columns": ["case_id"],
  "scheduling_policy": "SNAPSHOT", "branch": "projects/apex-recon-lb/branches/production",
  "postgres_database": "databricks_postgres", "create_database_objects_if_missing": true}}'
echo "created $NAME; waiting for the first snapshot"
until databricks postgres get-synced-table "synced_tables/$NAME" -p "$PROFILE" -o json |
      python3 -c "import json,sys; s=json.load(sys.stdin)['status']; print(s.get('detailed_state')); sys.exit(0 if 'ONLINE' in str(s.get('detailed_state')) else 1)"; do
  sleep 15
done
