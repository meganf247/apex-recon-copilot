# Runbook: build and run Apex Recon Copilot yourself

Step-by-step instructions to stand the whole build up in a Databricks workspace and run it end to end.
Allow about 1 hour; most of that is waiting on the build job (~20 min).

Commands are run from the repo root on your laptop. `<profile>` is your Databricks CLI profile name
(this build uses `megan-fevm2` for `https://fevm-megant-fevm.cloud.databricks.com`).

---

## 0. Prerequisites

| Need | Check |
|---|---|
| Databricks CLI (recent; needs `postgres` and `bundle` commands) | `databricks --version` |
| `psql` (Postgres client) | `psql --version` (macOS: `brew install libpq`) |
| Python 3.10+ (for the helper scripts) | `python3 --version` |
| `uv` (only for the local app test) | `uv --version` |
| Workspace with Unity Catalog, serverless compute, Lakebase and Foundation Model APIs | — |
| **CREATE CATALOG** on the metastore, *or* someone who can create the two catalogs in step 2 for you | — |

Log in:
```bash
databricks auth login --host https://<your-workspace>.cloud.databricks.com --profile <profile>
```

---

## 1. Values that are specific to a workspace

These IDs are hard-coded for the current workspace. If you deploy somewhere else, change them first (search the repo for the old value).

| Value | Current | Where it's used |
|---|---|---|
| Workspace host | `https://fevm-megant-fevm.cloud.databricks.com` | `databricks.yml` |
| CLI profile | `megan-fevm2` | default `--profile` in `scripts/*.py`, `scripts/grant_app.sh` |
| SQL warehouse ID | `93d767746e247a90` | `resources/jobs.yml`, `resources/app.yml`, `scripts/*.py`, `tests/app_smoke_test.py` |
| Lakebase project | `apex-recon-lb` (branch `production`, database `databricks_postgres`) | `app/app.yaml`, `scripts/grant_app.sh` |
| Lakebase host | `ep-cold-cell-d2f24olw.database.us-east-1.cloud.databricks.com` | `app/app.yaml`, `scripts/grant_app.sh`, `tests/app_smoke_test.py` |
| Synced-table pipeline ID | `e8b6f9fb-9b3b-4a4d-a55b-3372393e5240` | `resources/jobs.yml` (`refresh_lakebase_queue`); you get it in step 7 |
| Genie space ID | `01f1c1a695ce1f47baa2f07ef9f73663` | `resources/app.yml`, `tests/app_smoke_test.py`; you get it in step 8 |
| Your email | `megan.fogal@databricks.com` | `src/02_governance.sql` (access table seed) |

Find your warehouse ID with `databricks warehouses list -p <profile>`, and the Lakebase host with
`databricks postgres list-endpoints projects/<project>/branches/production -p <profile>`.

---

## 2. Catalogs (one-time)

1. **Main catalog `apex_recon`.** Create it in Catalog Explorer (or through your workspace's catalog provisioning tool).
   If the catalog lives in another workspace on the same metastore, bind it to this workspace (Catalog → Workspaces).
2. **Schemas and landing volume:**
   ```bash
   python3 scripts/run_sql.py src/00_setup_uc.sql --profile <profile> --warehouse <warehouse_id>
   ```
   This creates `landing`, `bronze`, `silver`, `gold`, `ml`, `ops`, `serving` and the volume `apex_recon.landing.raw`.

---

## 3. Lakebase project and its Unity Catalog catalog (one-time)

1. **Project.** In the workspace: app switcher → **Lakebase** → **New project** → name `apex-recon-lb`.
   It comes with the default branch `production` and database `databricks_postgres`. Don't create another branch.
   (CLI alternative: `databricks postgres create-project apex-recon-lb -p <profile>`.)
2. **Register it in Unity Catalog as `apex_recon_ops`.** Catalog Explorer → **+ → Create catalog** → type
   **Lakebase Postgres** (not Standard) → project `apex-recon-lb`, branch `production`, database `databricks_postgres`.
   (CLI alternative:)
   ```bash
   databricks postgres create-catalog apex_recon_ops -p <profile> \
     --json '{"spec": {"postgres_database": "databricks_postgres", "branch": "projects/apex-recon-lb/branches/production"}}'
   ```
3. **Make sure your Postgres role can create tables.** If the project is owned by someone else (e.g. a provisioning
   service principal), give your role superuser membership:
   ```bash
   databricks postgres list-roles projects/apex-recon-lb/branches/production -p <profile>   # find your role's name
   databricks postgres update-role <your-role-name> spec.membership_roles -p <profile> \
     --json '{"spec": {"membership_roles": ["DATABRICKS_SUPERUSER"]}}'
   ```
4. **Create the case-management tables** (`recon.dispute_cases`, `recon.case_events`, `recon.credit_approvals`):
   ```bash
   TOKEN=$(databricks postgres generate-database-credential projects/apex-recon-lb/branches/production/endpoints/primary \
           -p <profile> -o json | python3 -c "import json,sys; print(json.load(sys.stdin)['token'])")
   PGPASSWORD=$TOKEN psql "host=<lakebase_host> dbname=databricks_postgres user=<your email> sslmode=require" \
     -f src/05_lakebase_schema.sql
   ```
5. Check: `SELECT * FROM apex_recon_ops.recon.dispute_cases` in the SQL editor should return 0 rows, not an error.

---

## 4. First deploy (pipeline + job)

The app needs a Genie space ID that doesn't exist yet, so on a brand-new workspace, park the app config for the first deploy:
```bash
mv resources/app.yml resources/app.yml.pending     # skip if you already have a Genie space ID in it
databricks bundle validate -p <profile>
databricks bundle deploy -p <profile>
```
This uploads the notebooks (`src/`), the Lakeflow pipeline (`apex-recon-pipeline`) and the job (`apex-recon-build`)
to `/Workspace/Users/<you>/.bundle/apex-recon-copilot/dev/`.

On a brand-new workspace the `refresh_lakebase_queue` task points at a pipeline that doesn't exist yet (step 7).
Run the job without it the first time.

---

## 5. Run the build

```bash
databricks bundle run apex_recon_build -p <profile> \
  --only generate_data,ingest_and_reconcile,train_root_cause_model,score_and_draft_disputes,apply_governance,publish_case_status_view
```
(Once step 7 is done, just run `databricks bundle run apex_recon_build -p <profile>` for all 7 tasks.)

| Task | What it does | ~Time |
|---|---|---|
| `generate_data` | Writes 9 months of synthetic CTV data to `/Volumes/apex_recon/landing/raw` | 6 min |
| `ingest_and_reconcile` | Lakeflow pipeline, full refresh: bronze → silver → gold + ML features | 2–3 min |
| `train_root_cause_model` | Trains, logs to MLflow, registers `apex_recon.ml.discrepancy_root_cause@champion` | 1–2 min |
| `score_and_draft_disputes` | Scores all deal-months, builds `gold.dispute_queue`, drafts 250 disputes with `ai_query` | 3–4 min |
| `apply_governance` | Row filter, column masks, tags (`src/02_governance.sql`) | <1 min |
| `refresh_lakebase_queue` | Refreshes the Lakebase synced table | <1 min |
| `publish_case_status_view` | Live `ops.dispute_case_status` view over Lakebase (`src/07_case_status_view.sql`) | <1 min |

Watch it in **Jobs & Pipelines → apex-recon-build**. Each notebook's summary is in its task output.

**If the pipeline fails with "Table … is already managed by pipeline …"**: the tables were created by a pipeline
that no longer exists (e.g. an old workspace). Drop the pipeline-owned tables and rerun. The job recreates them:
```sql
-- list them
SELECT table_schema, table_name, table_type FROM apex_recon.information_schema.tables
WHERE table_schema IN ('bronze','silver','gold','ml') AND table_type IN ('STREAMING_TABLE','MATERIALIZED_VIEW');
-- then DROP TABLE apex_recon.<schema>.<streaming_table>; / DROP MATERIALIZED VIEW apex_recon.<schema>.<mv>;
```

---

## 6. Check the governance

Run the proof script. It switches your own entitlement to an Atlantic partner manager and back, so the same query
returns fewer rows with dollars masked:
```bash
python3 scripts/run_sql.py evidence/sql/05_governance_demo.sql --profile <profile> --warehouse <warehouse_id>
```
To give someone access, add a row to `apex_recon.ops.recon_access` (`principal`, `partner_team` or `*`, `can_see_revenue`).

---

## 7. Lakebase synced table for the app (one-time)

```bash
databricks postgres create-synced-table apex_recon.serving.case_workbench -p <profile> --json '{"spec": {
  "source_table_full_name": "apex_recon.gold.case_workbench", "primary_key_columns": ["case_id"],
  "scheduling_policy": "SNAPSHOT", "branch": "projects/apex-recon-lb/branches/production",
  "postgres_database": "databricks_postgres", "create_database_objects_if_missing": true}}'
```
Copy the `pipeline_id` from the output into `resources/jobs.yml` (task `refresh_lakebase_queue`), then
`databricks bundle deploy -p <profile>`. Check status with
`databricks postgres get-synced-table synced_tables/apex_recon.serving.case_workbench -p <profile>`. It should become
`SYNCED_TABLE_ONLINE...`.

---

## 8. Genie space (one-time)

```bash
python3 scripts/create_genie_space.py --profile <profile> --warehouse <warehouse_id>          # prints the new space ID
# later, to push edits to instructions/examples into the same space:
python3 scripts/create_genie_space.py --profile <profile> --warehouse <warehouse_id> --space-id <space_id>
```
Put the space ID into `resources/app.yml` (`genie_space.space_id`) and `tests/app_smoke_test.py`.

---

## 9. App

```bash
mv resources/app.yml.pending resources/app.yml      # if you parked it in step 4
databricks bundle deploy -p <profile>
databricks bundle run recon_workbench -p <profile>  # starts the app and prints its URL
scripts/grant_app.sh <profile>                      # UC + Lakebase grants for the app's service principal
```
`grant_app.sh` looks up the app's service principal and runs `src/06_app_grants.sql` (UC grants + Finance entitlement)
and `src/06_app_grants_lakebase.sql` (Postgres role + table grants). Rerun it if you ever recreate the app.

Open the URL: **Close overview → Triage queue → click a case → Send to partner / Resolve → Ask Genie**.
Anything you do in the app shows up immediately in `apex_recon.ops.dispute_case_status` and in Genie.

---

## 10. Tests and evidence (optional, regenerates `evidence/`)

```bash
# app end-to-end test (headless; writes one real case to Lakebase)
UV_NATIVE_TLS=1 uv venv .venv --python 3.12
UV_NATIVE_TLS=1 uv pip install --python .venv/bin/python -r app/requirements.txt   # add --index-url https://pypi-proxy.dev.databricks.com/simple/ on the corporate network
DATABRICKS_CONFIG_PROFILE=<profile> LAKEBASE_USER=<your email> .venv/bin/python tests/app_smoke_test.py

# Genie benchmark (12 questions vs reference SQL)
cd scripts && python3 genie_benchmark.py <space_id> ../evidence/06_genie_benchmark.md --profile <profile> --warehouse <warehouse_id> && cd ..

# job run summary
python3 scripts/capture_job_run.py <run_id> evidence/01_build_job_run.md --profile <profile>

# SQL evidence
for f in 02_pipeline_evidence 05_governance_demo 08_lakebase_live_status 09_lineage 10_business_impact; do
  python3 scripts/run_sql.py evidence/sql/$f.sql --profile <profile> --warehouse <warehouse_id> > evidence/$f.md
done
```
`evidence/sql/02_pipeline_evidence.sql` reads the pipeline event log by pipeline ID. If you redeploy the pipeline,
update the ID (`databricks pipelines list-pipelines -p <profile>`).

The deck PDF is rendered from `deck/apex_recon_deck.md`:
```bash
cd deck && pandoc apex_recon_deck.md -s --metadata pagetitle="Apex Exchange" -c deck.css -o apex_recon_deck.html
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --print-to-pdf=apex_recon_deck.pdf "file://$PWD/apex_recon_deck.html"
```

---

## Day-to-day

| I want to… | Do this |
|---|---|
| Rebuild everything from fresh data | `databricks bundle run apex_recon_build -p <profile>` |
| Change data volume, causes or noise | Edit constants in `src/01_generate_data.py` (seed 42 is reproducible); run locally first with `python3 src/01_generate_data.py` (writes to `/tmp/apex_raw`) |
| Change the pipeline | Edit `src/pipeline/*.py`, `databricks bundle deploy`, rerun the job |
| Reset the app's case data | `TRUNCATE recon.credit_approvals, recon.case_events, recon.dispute_cases RESTART IDENTITY;` in Lakebase |
| Stop paying for idle compute | Stop the app (`databricks apps stop apex-recon-workbench -p <profile>`); Lakebase autoscaling suspends itself when idle |
