# Apex Exchange · CTV Revenue Reconciliation Copilot

> **Outcome.** Apex Exchange, a CTV sell-side platform, loses **$8.9M a quarter (14% of its net revenue)** to DSP
> billing gaps, and each dispute takes 21 days. This copilot finds every gap the day a partner's file lands, names the
> root cause (**92% right vs. 55%** for today's rules of thumb), drafts the dispute and tracks it to cash. Value:
> **≈ $4.7M a year back to Apex's P&L**, ≈ $2.8M of cash released and ≈ 3 analysts' capacity, for **≈ $55K a year**
> to run (~85×). Every number here comes from committed run output in [`evidence/`](evidence/).

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
| Q3 work queue | 715 cases, $18.1M at risk, $8.9M Apex net exposure. **$6.3M recoverable** at Billing Ops' historical recovery rates, **$3.0M of it to Apex's P&L**. $8.5M (348 cases) is IVT or timezone, where the fix is a credit or a reporting change, not a chase. Publishers paid on Apex's count: 279 cases, $7.3M, all of it Apex's exposure. Publishers paid on cleared revenue: 436 cases, $10.8M, of which Apex's exposure is $1.6M. ([`10_business_impact`](evidence/10_business_impact.md)) |
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

## Decisions and trade-offs

| Decision | Why | Trade-off / alternative considered |
|---|---|---|
| **Reconcile per deal × day, dispute per deal × month** | Matches how CTV contracts are billed and disputed; the daily shape of the gap is what tells the root causes apart | Impression-level matching would be more precise but far more costly, and contracts don't settle at that grain |
| **Three measures: shortfall, revenue at risk, Apex net exposure** | The CFO's question is "what does this cost *Apex*?", not "how big is the gap?". Two gaps of the same size can differ 6× in P&L impact depending on publisher terms | Needs each deal's take rate and publisher payment terms. They're synthetic here and the first thing to confirm in discovery |
| **Gradient-boosted classifier for root cause, not an LLM** | Tabular features, cheap to run on every deal-month, measurable (accuracy / F1), registered and versioned in MLflow | An LLM could classify from the evidence pack, but it costs more per call, is harder to evaluate and drifts with model updates. The LLM does the language part only |
| **Train on analyst labels, evaluate on true causes, report the queue score** | Real labels are noisy (~11% wrong here), and most deal-months are easy within-tolerance calls | The headline is 92% on the 715 cases analysts work, not the flattering 95% on all deal-months. The pilot bar on real data is 85% |
| **Batch `ai_query` drafts for the top 250 cases by dollars** | One SQL statement, governed in Unity Catalog, runs in the nightly job; drafts are ready when analysts arrive | No live drafting for the long tail of small cases yet; a real-time endpoint call from the app is the next step |
| **Code checks plus an LLM judge on every draft run** | Deterministic checks catch what matters most (every dollar figure must appear in the evidence; the ask must fit the contract); the judge scores tone and clarity | The judge runs on a sample of 30, not all 250, to keep cost down |
| **Lakebase for case state, not Delta write-back** | Case work is transactional: small row updates, an audit trail, foreign keys, fast reads for the app. Registered in Unity Catalog, so Finance and Genie see updates live with no copy job | One more component to operate. The queue syncs as a snapshot per run, and a schema change means recreating the synced table (`scripts/create_synced_table.sh`) |
| **Governance policies declared in the pipeline** for the gold tables, applied in the publish step for the queue | Declared policies survive the pipeline's full refresh; the queue is rebuilt by the ML notebook, so the publish step re-applies its policies | Two places to maintain, both documented in `src/04_publish.sql` |
| **Access table keyed on `current_user()`** | Account groups can't be created in this FE workspace | In production it would be `is_account_group_member()` on IdP groups. The app runs as its service principal with Finance scope; on-behalf-of-user auth is the next step |
| **One bundle, one 4-step serverless job, full refresh** | Simple to deploy and reason about; a full run takes ~9 minutes and ≈ $3.80 | At production volume, bronze ingestion and gold would move to incremental processing |
| **Synthetic data with mixed causes and label noise** | No customer data can be used; the generator plants five causes, a secondary cause on ~30% of problem cases, and wrong labels on ~11% of history | Still cleaner than real life. The app stores the analyst's confirmed cause next to the model's, which becomes new training data |
| **Streamlit for the app** | Fast to build, Python end to end, deploys as a Databricks App | A production team might embed the queue in an existing billing or ticketing tool instead |

Other notes: `databricks-claude-sonnet-5-5` isn't enabled for `ai_query` batch inference in this workspace, so drafts
use Sonnet 4.6. Training rows are sorted before the train/test split, so model scores are reproducible across runs.

## How AI was used to build this

**Tools.** Claude Code built the whole thing: one session for the initial build and a second session for review and
fixes. Both drove the Databricks CLI, the Python SDK and Asset Bundles against the live workspace. Session IDs are
available on request.

**Patterns that worked:**

- **Requirements in, rubric review out.** The FE Bar requirements were given to the agent as the spec. A separate
  review session was then asked to *grade the build against the same rubric* before fixing anything. That review
  found real problems: an inflated accuracy claim (95% on all deal-months vs. 92% on the cases that matter), two
  different definitions of "revenue at risk", gross spend presented as revenue, and governance on only one table.
- **Evidence-first, so the AI can't claim what didn't run.** The agent wrote the evidence tooling
  (`scripts/capture_job_run.py`, `export_notebook_run.py`, `run_sql.py`, `genie_benchmark.py`,
  `tests/app_smoke_test.py`). Every number in this README and the deck comes from committed output of the same job run.
- **Verify, don't trust.** Each change was checked by rerunning the real system: the full job, a headless test that
  clicks through the app, a Genie benchmark against reference SQL, and SQL checks of the row filters and masks.
- **Human in the loop for decisions.** The agent proposed and implemented; the builder chose the scenario, approved
  each change and every push to this public repo, and made the calls on scope.

**AI inside the product**, with the prompts in the repo:

| Where | Prompt / config | Guardrail |
|---|---|---|
| Dispute drafting (Claude via `ai_query`) | `PROMPT` in `src/03_ml_and_disputes.ipynb`, section 4: evidence-only, exact figures, contract-aware ask, JSON output, temperature 0 | Code checks: every dollar figure must trace to the evidence; the ask must match the billing basis |
| Draft quality judge (a second model) | Judge prompt in the same cell: accuracy, tone, actionability, each 1–5 | Different model family from the drafter, temperature 0 |
| Genie | Instructions, definitions and certified example SQL in `scripts/create_genie_space.py` | Benchmarked 14/14 against independently written reference SQL (`scripts/genie_benchmark.py`) |
