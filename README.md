# Apex Exchange · CTV Revenue Reconciliation Copilot

An end-to-end Databricks build for a **CTV sell-side platform (SSP)**. It reconciles the SSP's own auction logs
against the billing reports of the DSPs who pay it, explains *why* each gap happened, drafts the partner dispute, and
gives Billing Ops one app to resolve cases.

> **Apex Exchange is fictional and all data is synthetic** (`src/01_generate_data.ipynb`, seed 42). No customer data is used.

## The customer problem

Apex Exchange runs about **$1.7B a year in gross CTV ad spend** (Q3 2026: $432M gross, $61.9M Apex net revenue at a
14.3% average take). Money flows DSP → Apex → publisher: the DSP pays Apex for each impression, Apex keeps its take and
pays the publisher the rest. Every month Apex's count and each DSP's count disagree.

- **Q3 2026: $24.4M billing shortfall** (5.7% of gross). **$18.1M** of it is on 715 deal-months over contract
  tolerance across 39 of 40 DSPs (the revenue at risk), and **$8.9M** of that hits Apex's own P&L: 14% of its Q3 net revenue.
- A dispute takes **21 days** to resolve on average (p90: 33). On the cases analysts actually work, their rules of
  thumb name the right cause only **55%** of the time, so effort goes to cases that won't recover money while
  recoverable money ages.

**Three measures, used the same way everywhere** (pipeline, app, Genie, deck):

| Measure | Column | Meaning | Q3 2026 |
|---|---|---|---:|
| Billing shortfall | `billing_shortfall_usd` | Positive gap on every deal, including deals within contract tolerance | $24.4M |
| Revenue at risk | `revenue_at_risk_usd` | The shortfall on deals that need review: exactly the dispute queue | $18.1M (715 cases) |
| Apex net exposure | `apex_exposure_usd` | The part of revenue at risk that hits Apex's P&L: all of it when the publisher is paid on Apex's count (`publisher_paid_on = APEX_COUNT`), only Apex's take when the publisher is paid on cleared revenue | $8.9M |

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
                        4 data-quality rules            row filter + revenue masks on both gold tables

ML + GenAI (src/03_ml_and_disputes.ipynb) ─► ml.discrepancy_root_cause@champion ─► gold.dispute_queue ─► gold.dispute_drafts
                                                                           └─► gold.case_workbench ══sync══► Lakebase
Publish (src/04_publish.sql) ─► row filter + revenue masks on the queue · governed live view ops.dispute_case_status over Lakebase

Genie space ◄── gold + ops.dispute_case_status            App ◄── UC (SQL) + Lakebase (read queue, write cases) + Genie
```

| Stage | Databricks | In this build | Evidence |
|---|---|---|---|
| **Ingest** | Lakeflow Spark Declarative Pipelines + Auto Loader | 273 SSP log files and 360 DSP report files land in a UC Volume; the pipeline goes bronze → silver → gold in 6 tables with 3 joins. 4 data-quality rules (missing deal ID, bad date, negative impressions, duplicate row) drop bad DSP rows and record the counts. | [`02_pipeline_evidence`](evidence/02_pipeline_evidence.md) |
| **Govern** | Unity Catalog | Row filter (partner managers see only their team's DSPs) and column masks (dollar amounts for Finance only), driven by an access table, on every table a partner manager or Genie can query: both gold reconciliation tables (declared in the pipeline), the work queue and the live case-status view. Working tables (Lakebase sync source, model inputs, drafts) are granted only to Finance and the app. Tags; table comments; automatic lineage. | [`04_publish_check`](evidence/04_publish_check.md), [`05_governance_demo`](evidence/05_governance_demo.md), [`09_lineage`](evidence/09_lineage.md) |
| **ML** | MLflow + UC Model Registry | Gradient-boosted classifier predicts the root cause from how the daily gap behaves across the month (swing, missing days, big-gap days, publisher IVT risk…). Registered as `apex_recon.ml.discrepancy_root_cause@champion`. | [`01_build_job_run`](evidence/01_build_job_run.md), [executed notebook](evidence/notebook_runs/03_ml_and_disputes.md) |
| **GenAI** | `ai_query` + Foundation Model APIs | Claude Sonnet 4.6 drafts a case summary and partner dispute email for the top 250 cases from a JSON evidence pack, following each contract's billing basis. Every draft is checked: dollar figures must come from the evidence, the ask must fit the contract, plus an LLM judge on 30. | same |
| **Operational serving** | Lakebase + Lakebase UC catalog | The case queue is synced into Lakebase; the app writes case status, an audit trail and credit approvals to `recon.*`. Lakebase is registered in UC as **`apex_recon_ops`**, so `ops.dispute_case_status` reads those tables **live**. | [`07_app_e2e_test`](evidence/07_app_e2e_test.md), [`08_lakebase_live_status`](evidence/08_lakebase_live_status.md) |
| **Natural language** | Genie | "Apex Exchange · CTV Revenue Reconciliation", with business definitions (including gross spend vs. Apex net revenue and exposure), sample questions and certified example SQL, benchmarked against reference SQL. | [`06_genie_benchmark`](evidence/06_genie_benchmark.md) |
| **Surface** | Databricks App (Streamlit) | **Reconciliation Workbench**: Close overview → Triage queue → Case detail (evidence, AI root cause, editable email, send / resolve / credit) → Ask Genie. | [`07_app_e2e_test`](evidence/07_app_e2e_test.md) |
| **Orchestrate** | Lakeflow Jobs + Asset Bundle | One job, 4 steps: `generate_data` → `pipeline` → `ml_and_disputes` → `publish`. Everything deploys from `databricks.yml`. | [`01_build_job_run`](evidence/01_build_job_run.md), [executed generator notebook](evidence/notebook_runs/01_generate_data.md) |

## Results (from the committed run output)

| | Result |
|---|---|
| Data | 3.57M SSP deal-hours (31.5B impressions, $1.13B gross, Jan–Sep 2026); 158,242 DSP report rows from 40 DSPs |
| Data quality | 1,728 bad DSP rows dropped. Per rule: 633 missing deal ID, 481 duplicates, 331 bad dates, 290 negative impressions. The generator injects each fault independently and copies duplicates after injecting, so a few rows carry two faults; that's why the rule counts sum to slightly more than the rows dropped (and than each injected count). |
| Reconciliation | September close: Apex $153.5M vs DSP-reported $144.6M; $8.9M billing shortfall, of which **$6.8M is revenue at risk in 219 cases** and **$3.3M is Apex's own exposure** |
| Root-cause model | On the 715 Jul–Sep cases analysts actually work, against the true causes: **accuracy 92%, macro F1 0.91** vs 55% / 0.41 for the rules of thumb. Against Jan–Jun analyst labels (holdout): macro F1 0.85 vs 0.54. On all 2,025 Jul–Sep deal-months, most of them easy within-tolerance calls: 95% / 0.91 vs 82% / 0.58. The model scores higher on true causes than on analyst labels because it learns past the analysts' labelling mistakes. |
| GenAI drafts | 250 drafts, 0 parse failures, 100% of dollar figures traced to the evidence, 100% consistent with the contract's billing basis, LLM judge 4.7 / 5.0 / 5.0 for accuracy, tone, actionability (n=30) |
| Q3 work queue | 715 cases, $18.1M at risk, $8.9M Apex net exposure. **$6.3M recoverable** at Billing Ops' historical recovery rates, **$3.0M of it to Apex's P&L**. $8.5M (348 cases) is IVT or timezone, where the fix is a credit or a reporting change, not a chase. Publishers paid on Apex's count: 279 cases, $7.3M, all of it Apex's exposure. Publishers paid on cleared revenue: 436 cases, $10.8M, of which Apex's exposure is $1.6M. |
| Genie | 14/14 finance questions match reference SQL |
| App | End-to-end test passed: all pages render; an IVT case goes open → sent → resolved, crediting only the verified IVT and recovering the rest; rows land in Lakebase and show up live in UC |
| Cost to run | ≈ $3.80 per full build run, ≈ $11/day for the always-on app, at list price from system billing tables ([`11_build_cost`](evidence/11_build_cost.md)) |

## Repo layout

```
databricks.yml, resources/   Bundle: pipeline, 4-step job, app
src/01_generate_data.ipynb   Synthetic data, reference tables, dispute history
src/02_pipeline.py           Lakeflow pipeline: bronze → silver → gold (6 tables, 3 joins)
src/03_ml_and_disputes.ipynb Features, model, work queue, ai_query drafts and checks, Lakebase refresh
src/04_publish.sql           Governance (row filter, masks, tags) + live case-status view over Lakebase
src/00_setup_uc.sql          One-time: schemas, landing volume, access table and the row filter / mask functions
src/00_setup_lakebase.sql    One-time: Lakebase case tables
src/app_grants*.sql          App service principal grants (run by scripts/grant_app.sh)
app/                         Streamlit Reconciliation Workbench
scripts/                     run_sql, capture_job_run, export_notebook_run, create_genie_space, genie_benchmark,
                             create_synced_table, grant_app
tests/app_smoke_test.py      Headless end-to-end app test
evidence/                    Text output from every stage (queries in evidence/sql; executed notebooks with cell outputs in evidence/notebook_runs)
deck/                        Business presentation: PowerPoint + PDF built by deck/build_deck.py, text version in markdown
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
- **Take rates and publisher payment terms are synthetic too** (by deal type: PG ~11%, PMP ~14%, open ~18%; publishers
  on guaranteed deals are mostly paid on Apex's count). They're the first thing to confirm in discovery, because they
  decide how much of each gap is Apex's own loss.
- **The model's scores are reproducible:** training rows are sorted before the train/test split, so a rerun gives the same numbers.
- **Governance uses an access table** (`ops.recon_access`, keyed on `current_user()`) because account groups can't be
  created in this FE workspace. In production it would be `is_account_group_member()` on IdP groups.
- **The app runs as its service principal**, with Finance scope. Next step: on-behalf-of-user auth so the row filter
  applies to each signed-in user.
- `databricks-claude-sonnet-5-5` isn't enabled for `ai_query` batch inference in this workspace, so drafts use Sonnet 4.6.
