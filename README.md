# Apex Exchange · CTV Revenue Reconciliation Copilot

An end-to-end Databricks build for a **CTV sell-side platform (SSP)**. It reconciles the SSP's own auction logs
against the billing reports of the DSPs who pay it, explains *why* each gap happened, drafts the partner dispute, and
gives Billing Ops one app to resolve cases.

> **Apex Exchange is fictional and all data is synthetic** (`src/01_generate_data.ipynb`, seed 42). No customer data is used.

## The customer problem

Apex Exchange runs about **$1.7B a year in gross CTV ad spend** (Q3 2026: $432M). Money flows DSP → Apex → publisher:
the DSP pays Apex for each impression, Apex keeps its fee and pays the publisher the rest. Every month Apex's count
and each DSP's count disagree.

- **Q3 2026: $24.4M of delivered revenue (5.7% of gross) was not matched by DSP reports**; 715 deal-months across 39 of 40 DSPs needed review.
- A dispute takes **21 days** to resolve on average (p90: 33). The analysts' rules of thumb name the right cause
  only 65–82% of the time, so effort goes to cases that won't recover money while recoverable money ages.

**Buyers:** CFO / VP Revenue Accounting (sponsor) · Director of Billing Operations (domain owner) · VP Data Engineering (technical).

**Five root causes** in the data, each with a different fix:

| Cause | What happens | Fix |
|---|---|---|
| Within tolerance | Normal measurement noise | None |
| Timezone shift | The DSP reports days in US time; CTV primetime crosses midnight UTC, so daily counts swing but the month nets out | Ask for UTC reporting; no billing change |
| IVT filtering | The DSP's fraud vendor removes invalid (spoofed) CTV traffic | Credit only verified IVT |
| Missing data | Days missing from the DSP's report | Get the missing days, then bill |
| Billing error | Unexplained under-reporting on some days | Dispute with log evidence |

About 30% of problem cases also have a smaller second cause, and ~11% of past analyst labels are wrong, as in real life.

## How it's built

```
Generator ─► /Volumes/apex_recon/landing/raw ── ssp_logs/*.json.gz   (Apex, hourly)
                                             └─ dsp_reports/<dsp>/*.csv (each DSP, daily)
          ─► silver.deals, silver.dsps (reference), ml.dispute_history (labels)

Lakeflow pipeline (src/02_pipeline.py), 6 tables, 3 joins:
  bronze.ssp_logs ────► silver.ssp_daily ──┐
                                           ├─► gold.recon_deal_month ──► gold.recon_partner_month
  bronze.dsp_reports ─► silver.dsp_daily ──┘    (SSP ⋈ DSP, + deals, + DSPs)
                        4 data-quality rules

ML + GenAI (src/03_ml_and_disputes.ipynb) ─► ml.discrepancy_root_cause@champion ─► gold.dispute_queue ─► gold.dispute_drafts
                                                                           └─► gold.case_workbench ══sync══► Lakebase
Publish (src/04_publish.sql) ─► row filter + revenue masks on the queue · live view ops.dispute_case_status over Lakebase

Genie space ◄── gold + ops.dispute_case_status            App ◄── UC (SQL) + Lakebase (read queue, write cases) + Genie
```

| Stage | Databricks | In this build | Evidence |
|---|---|---|---|
| **Ingest** | Lakeflow Spark Declarative Pipelines + Auto Loader | 273 SSP log files and 360 DSP report files land in a UC Volume; the pipeline goes bronze → silver → gold in 6 tables with 3 joins. 4 data-quality rules (missing deal ID, bad date, negative impressions, duplicate row) drop bad DSP rows and record the counts. | [`02_pipeline_evidence`](evidence/02_pipeline_evidence.md) |
| **Govern** | Unity Catalog | Row filter (partner managers see only their team's DSPs) and column masks (dollar amounts for Finance only), driven by an access table; tags; table comments; automatic lineage. | [`04_publish_check`](evidence/04_publish_check.md), [`05_governance_demo`](evidence/05_governance_demo.md), [`09_lineage`](evidence/09_lineage.md) |
| **ML** | MLflow + UC Model Registry | Gradient-boosted classifier predicts the root cause from how the daily gap behaves across the month (swing, missing days, big-gap days, publisher IVT risk…). Registered as `apex_recon.ml.discrepancy_root_cause@champion`. | [`01_build_job_run`](evidence/01_build_job_run.md), [executed notebook](evidence/notebook_runs/03_ml_and_disputes.md) |
| **GenAI** | `ai_query` + Foundation Model APIs | Claude Sonnet 4.6 drafts a case summary and partner dispute email for the top 250 cases from a JSON evidence pack, following each contract's billing basis. Every draft is checked: dollar figures must come from the evidence, the ask must fit the contract, plus an LLM judge on 30. | same |
| **Operational serving** | Lakebase + Lakebase UC catalog | The case queue is synced into Lakebase; the app writes case status, an audit trail and credit approvals to `recon.*`. Lakebase is registered in UC as **`apex_recon_ops`**, so `ops.dispute_case_status` reads those tables **live**. | [`07_app_e2e_test`](evidence/07_app_e2e_test.md), [`08_lakebase_live_status`](evidence/08_lakebase_live_status.md) |
| **Natural language** | Genie | "Apex Exchange · CTV Revenue Reconciliation", with business definitions, sample questions and certified example SQL, benchmarked against reference SQL. | [`06_genie_benchmark`](evidence/06_genie_benchmark.md) |
| **Surface** | Databricks App (Streamlit) | **Reconciliation Workbench**: Close overview → Triage queue → Case detail (evidence, AI root cause, editable email, send / resolve / credit) → Ask Genie. | [`07_app_e2e_test`](evidence/07_app_e2e_test.md) |
| **Orchestrate** | Lakeflow Jobs + Asset Bundle | One job, 4 steps: `generate_data` → `pipeline` → `ml_and_disputes` → `publish`. Everything deploys from `databricks.yml`. | [`01_build_job_run`](evidence/01_build_job_run.md), [executed generator notebook](evidence/notebook_runs/01_generate_data.md) |

## Results (from the committed run output)

| | Result |
|---|---|
| Data | 3.57M SSP deal-hours (31.5B impressions, $1.13B gross, Jan–Sep 2026); 158,242 DSP report rows from 40 DSPs |
| Data quality | 1,728 bad DSP rows dropped: 633 missing deal ID, 481 duplicates, 331 bad dates, 290 negative impressions |
| Reconciliation | September close: Apex $153.5M vs DSP-reported $144.6M; **$8.9M revenue at risk**; 219 deals need review |
| Root-cause model | Against Jan–Jun analyst labels (holdout): **macro F1 0.82** vs 0.56 for the rules of thumb. Against the true causes for Jul–Sep: **F1 0.92, accuracy 95%** vs 0.58 / 82%. It scores higher on true causes because it learns past the analysts' labelling mistakes. |
| GenAI drafts | 250 drafts, 0 parse failures, 100% of dollar figures traced to the evidence, 100% consistent with the contract's billing basis, LLM judge 4.8 / 5.0 / 5.0 for accuracy, tone, actionability (n=30) |
| Q3 work queue | 715 cases, $18.1M at risk; **$6.1M recoverable** at Billing Ops' historical recovery rates; $8.7M (359 cases) is IVT or timezone, where the fix is a credit or a reporting change, not a chase |
| Genie | 12/12 finance questions match reference SQL |
| App | End-to-end test passed: all pages render; a case goes open → sent → resolved with credit; rows land in Lakebase and show up live in UC |

## Repo layout

```
databricks.yml, resources/   Bundle: pipeline, 4-step job, app
src/01_generate_data.ipynb   Synthetic data, reference tables, dispute history
src/02_pipeline.py           Lakeflow pipeline: bronze → silver → gold (6 tables, 3 joins)
src/03_ml_and_disputes.ipynb Features, model, work queue, ai_query drafts and checks, Lakebase refresh
src/04_publish.sql           Governance (row filter, masks, tags) + live case-status view over Lakebase
src/00_setup_uc.sql          One-time: schemas and landing volume
src/00_setup_lakebase.sql    One-time: Lakebase case tables
src/app_grants*.sql          App service principal grants (run by scripts/grant_app.sh)
app/                         Streamlit Reconciliation Workbench
scripts/                     run_sql, capture_job_run, export_notebook_run, create_genie_space, genie_benchmark, grant_app
tests/app_smoke_test.py      Headless end-to-end app test
evidence/                    Text output from every stage (queries in evidence/sql; executed notebooks with cell outputs in evidence/notebook_runs)
deck/                        Business presentation (PDF + markdown)
RUNBOOK.md                   How to run and demo it
```

## How to run

See **[RUNBOOK.md](RUNBOOK.md)**. Once set up, it's:
```bash
databricks bundle deploy -p <profile>
databricks bundle run apex_recon_build -p <profile>
```

## Design notes and limitations

- **Simple on purpose.** The pipeline is 6 tables with 3 joins; reference data and dispute history are written once
  by the generator, and ML features live in the ML notebook rather than the pipeline.
- **Synthetic data is cleaner than real life,** even with the secondary causes and label noise. The app records the
  analyst's confirmed cause next to the model's, which becomes new training data in production.
- **Governance uses an access table** (`ops.recon_access`, keyed on `current_user()`) because account groups can't be
  created in this FE workspace. In production it would be `is_account_group_member()` on IdP groups.
- **The app runs as its service principal**, with Finance scope. Next step: on-behalf-of-user auth so the row filter
  applies to each signed-in user.
- `databricks-claude-sonnet-5-5` isn't enabled for `ai_query` batch inference in this workspace, so drafts use Sonnet 4.6.
