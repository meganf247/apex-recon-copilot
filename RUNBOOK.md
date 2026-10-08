# Runbook: running Apex Recon Copilot in your workspace

Everything is already set up in **`fevm-megant-fevm`**. These instructions are for running and demoing it there.
The one-time setup is listed at the end for reference.

## What's where

| Thing | Where |
|---|---|
| Workspace | https://fevm-megant-fevm.cloud.databricks.com |
| CLI profile on your laptop | `megan-fevm2` |
| Repo on your laptop | `~/apex-recon-copilot` (GitHub: `megan-fogal_data/apex-recon-copilot`) |
| Notebooks and code in the workspace | `/Workspace/Users/megan.fogal@databricks.com/apex-recon-copilot/src/` |
| Build job | **Jobs & Pipelines → `[dev megan_fogal] apex-recon-build`** (job ID `800507315624085`) |
| Lakeflow pipeline | `[dev megan_fogal] apex-recon-pipeline` (`7e5bc896-605c-44f6-a2e3-039922e893a9`) |
| Data | Catalog `apex_recon` (schemas `landing`, `bronze`, `silver`, `gold`, `ml`, `ops`, `serving`) |
| Lakebase | Project `apex-recon-lb`, branch `production`, database `databricks_postgres`; in Unity Catalog as **`apex_recon_ops`** |
| ML model | `apex_recon.ml.discrepancy_root_cause@champion` |
| Genie space | **"Apex Exchange · CTV Revenue Reconciliation"** (ID `01f1c1a695ce1f47baa2f07ef9f73663`) |
| App | https://apex-recon-workbench-7474649371849429.aws.databricksapps.com |
| SQL warehouse | Serverless Starter Warehouse (`93d767746e247a90`) |

---

## 1. Rerun the whole build

**From the UI:** Jobs & Pipelines → `[dev megan_fogal] apex-recon-build` → **Run now**.

**From your laptop:**
```bash
cd ~/apex-recon-copilot
databricks auth login --profile megan-fevm2        # only if your login has expired
databricks bundle run apex_recon_build -p megan-fevm2
```

It takes about 15 minutes. The 4 steps:

| Step | What it does | ~Time |
|---|---|---|
| `generate_data` | Regenerates 9 months of synthetic data into `/Volumes/apex_recon/landing/raw` plus the reference tables (`silver.deals`, `silver.dsps`) and dispute history (`ml.dispute_history`). Seed 42, so the same data every time. | 6 min |
| `pipeline` | Lakeflow pipeline, full refresh: `bronze.ssp_logs`, `bronze.dsp_reports` → `silver.ssp_daily`, `silver.dsp_daily` → `gold.recon_deal_month` → `gold.recon_partner_month` | 2–3 min |
| `ml_and_disputes` | Builds features, trains and registers the root-cause model, builds `gold.dispute_queue`, drafts 250 disputes with Claude, checks them, refreshes the Lakebase queue | 4–5 min |
| `publish` | Reapplies the row filter, revenue masks and tags; recreates the live case-status view over Lakebase | <1 min |

Click any task in the run to see its output. Each notebook ends with a JSON summary (row counts, model scores, GenAI checks).

Rerunning doesn't delete case work done in the app: Lakebase case tables are kept. To start the demo clean, see
"Reset the app's cases" below.

---

## 2. Demo the app

Open https://apex-recon-workbench-7474649371849429.aws.databricksapps.com and sign in with your Databricks account.

1. **Close overview:** pick **2026-09**. You'll see Apex vs DSP-reported revenue, revenue at risk, cases open and
   recovered-to-date, plus revenue at risk by DSP and by root cause.
2. **Triage queue:** cases sorted by dollars at risk, with the model's root cause and confidence. Click a row.
3. **Case detail:** the daily Apex-vs-DSP chart, evidence tiles (days missing in the DSP report, days with a big gap, day-to-day swing, publisher IVT risk),
   the AI case summary, and the editable dispute email.
   - **Send to partner** marks the case sent and logs it.
   - **Resolve case** records the resolution, confirmed root cause and recovered or credited amount.
   - Notes and the audit trail are at the bottom.
4. **Ask Genie:** e.g. *"How much revenue at risk did timezone issues cause in Q3?"* or
   *"How many disputes are still open and how much money do they cover?"*

Everything you do in the app is written to Lakebase and shows up **immediately** in Unity Catalog. Run this in the SQL editor:
```sql
SELECT * FROM apex_recon_ops.recon.dispute_cases ORDER BY updated_at DESC;
SELECT status, count(*), round(sum(revenue_at_risk_usd)) FROM apex_recon.ops.dispute_case_status GROUP BY status;
```

If the app shows "Stopped", start it from **Compute → Apps → apex-recon-workbench → Start**, or run
`databricks bundle run recon_workbench -p megan-fevm2`.

---

## 3. Show each piece in the workspace

| To show | Go to |
|---|---|
| Raw files (hourly SSP logs, daily DSP reports, one folder per DSP) | Catalog → `apex_recon` → `landing` → volume `raw` |
| Pipeline graph and data-quality results | Jobs & Pipelines → `apex-recon-pipeline` → latest update → click `silver.dsp_daily` for the 4 rules' pass/fail counts |
| The 3 joins | `src/02_pipeline.py`, function `recon_deal_month` |
| Reconciliation results | `apex_recon.gold.recon_partner_month`, `recon_deal_month`, `dispute_queue` |
| Lineage | Catalog → `apex_recon.gold.dispute_queue` → **Lineage** tab |
| Row filter and masks | Catalog → `apex_recon.gold.dispute_queue` → Overview (row filter + masked columns); access is in `apex_recon.ops.recon_access` |
| Model runs and metrics | Experiments → `/Users/megan.fogal@databricks.com/apex-recon-root-cause` |
| Registered model | Catalog → `apex_recon.ml.discrepancy_root_cause` |
| GenAI drafts | `SELECT case_id, case_summary, email_body FROM apex_recon.gold.dispute_drafts` |
| Lakebase | App switcher → Lakebase → `apex-recon-lb`; or Catalog → `apex_recon_ops` |
| Genie | Genie → "Apex Exchange · CTV Revenue Reconciliation" |

**Governance demo** (switches your own access to an Atlantic partner manager and back, so you can show the same
query returning fewer rows with dollars hidden):
```bash
cd ~/apex-recon-copilot
python3 scripts/run_sql.py evidence/sql/05_governance_demo.sql
```
To do it by hand: `UPDATE apex_recon.ops.recon_access SET partner_team = 'Atlantic', can_see_revenue = FALSE WHERE principal = current_user();`
then query `apex_recon.gold.dispute_queue`. Restore with `SET partner_team = '*', can_see_revenue = TRUE`.

---

## 4. Common tasks

| I want to… | Do this |
|---|---|
| Change code and redeploy | Edit files in `~/apex-recon-copilot`, then `databricks bundle deploy -p megan-fevm2` (then rerun the job) |
| Change data volume, causes or noise | Edit `src/01_generate_data.ipynb`, then deploy and rerun the job |
| Change the pipeline | Edit `src/02_pipeline.py`, deploy, rerun the job |
| Change Genie instructions or example SQL | Edit `scripts/create_genie_space.py`, then `python3 scripts/create_genie_space.py --space-id 01f1c1a695ce1f47baa2f07ef9f73663` |
| Reset the app's cases | In the Lakebase SQL editor (`apex-recon-lb` → `databricks_postgres`): `TRUNCATE recon.credit_approvals, recon.case_events, recon.dispute_cases RESTART IDENTITY;` |
| Give someone access to the data | Add a row to `apex_recon.ops.recon_access` (`principal`, `partner_team` or `*`, `can_see_revenue`) |
| Redeploy the app after a code change | `databricks bundle deploy -p megan-fevm2 && databricks bundle run recon_workbench -p megan-fevm2` |
| Stop paying for idle compute | `databricks apps stop apex-recon-workbench -p megan-fevm2` (Lakebase suspends itself when idle) |
| Push changes to GitHub | `cd ~/apex-recon-copilot && git add -A && git commit -m "..." && git push` |

---

## 5. Refresh the evidence files (before submitting, if you change anything)

```bash
cd ~/apex-recon-copilot

# job run summary (use the run ID from the job page or the bundle run output)
python3 scripts/capture_job_run.py <run_id> evidence/01_build_job_run.md

# executed notebooks, every cell with its output (task run IDs: databricks jobs get-run <run_id> -p megan-fevm2)
python3 scripts/export_notebook_run.py <generate_data_task_run_id> evidence/notebook_runs/01_generate_data --job-run <run_id>
python3 scripts/export_notebook_run.py <ml_and_disputes_task_run_id> evidence/notebook_runs/03_ml_and_disputes --job-run <run_id>

# SQL evidence
for f in 02_pipeline_evidence 04_publish_check 05_governance_demo 08_lakebase_live_status 09_lineage 10_business_impact; do
  python3 scripts/run_sql.py evidence/sql/$f.sql > evidence/$f.md
done

# Genie benchmark (12 questions checked against reference SQL)
cd scripts && python3 genie_benchmark.py 01f1c1a695ce1f47baa2f07ef9f73663 ../evidence/06_genie_benchmark.md && cd ..

# app end-to-end test (writes one real case to Lakebase); needs the local venv in ~/apex-recon-copilot/.venv
DATABRICKS_CONFIG_PROFILE=megan-fevm2 LAKEBASE_USER=megan.fogal@databricks.com .venv/bin/python tests/app_smoke_test.py
```
Then update any changed numbers in `README.md` and `deck/apex_recon_deck.md`, re-render the deck PDF, commit and push:
```bash
cd deck && pandoc apex_recon_deck.md -s --metadata pagetitle="Apex Exchange" -c deck.css -o apex_recon_deck.html \
  && "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --print-to-pdf=apex_recon_deck.pdf "file://$PWD/apex_recon_deck.html" && cd ..
```

---

## 6. If something goes wrong

| Symptom | Fix |
|---|---|
| CLI says the token is invalid or expired | `databricks auth login --profile megan-fevm2` |
| Pipeline fails: "Table … is already managed by pipeline …" | A table was created by a different pipeline. Drop the pipeline's 6 tables (`DROP TABLE` for the two bronze tables, `DROP MATERIALIZED VIEW` for the silver and gold ones) and rerun |
| App errors on the queue or a case | Check the synced table: `databricks postgres get-synced-table synced_tables/apex_recon.serving.case_workbench -p megan-fevm2` (should be `ONLINE`). The `ml_and_disputes` step refreshes it; its output says `Lakebase sync: refresh started` |
| You changed the columns of `gold.case_workbench` | Delete and recreate the synced table (appendix step 5), then rerun `scripts/grant_app.sh` |
| App can't write to Lakebase after recreating it | Rerun `scripts/grant_app.sh` (the app gets a new service principal) |
| `ai_query` fails with "not supported for batch inference" | The model endpoint isn't enabled for batch; keep `databricks-claude-sonnet-4-6` in `src/03_ml_and_disputes.ipynb` |
| Genie gives a wrong answer | Add an example query or instruction in `scripts/create_genie_space.py` and push it with `--space-id` |

---

## Appendix: one-time setup (already done)

For reference only, in case you rebuild elsewhere:
1. Catalog `apex_recon`, then `python3 scripts/run_sql.py src/00_setup_uc.sql` (schemas + volume).
2. Lakebase project `apex-recon-lb`, registered in Unity Catalog as `apex_recon_ops` (catalog type **Lakebase Postgres**,
   branch `production`, database `databricks_postgres`). Your Postgres role needs `DATABRICKS_SUPERUSER` membership to
   create tables (`databricks postgres update-role ... spec.membership_roles`).
3. Case tables: `psql ... -f src/00_setup_lakebase.sql` against `databricks_postgres`.
4. `databricks bundle deploy -p megan-fevm2`, then run the job once so `gold.case_workbench` exists.
5. Synced table:
   ```bash
   databricks postgres create-synced-table apex_recon.serving.case_workbench -p megan-fevm2 --json '{"spec": {
     "source_table_full_name": "apex_recon.gold.case_workbench", "primary_key_columns": ["case_id"],
     "scheduling_policy": "SNAPSHOT", "branch": "projects/apex-recon-lb/branches/production",
     "postgres_database": "databricks_postgres", "create_database_objects_if_missing": true}}'
   ```
6. Genie space: `python3 scripts/create_genie_space.py`; its ID goes in `resources/app.yml` and `tests/app_smoke_test.py`.
7. App: `databricks bundle run recon_workbench -p megan-fevm2`, then `scripts/grant_app.sh`.
