# Apex Exchange · CTV Revenue Reconciliation Copilot: business deck (text version)

Text version of `apex_recon_deck.pptx` / `apex_recon_deck.pdf` (built by `deck/build_deck.py`). Every number comes from
the committed evidence (job run 542978415804640). Apex Exchange is fictional; all data is synthetic.

---

## 1 · Recover $4.7M a year that DSP billing gaps take from Apex's P&L

Close faster, recover more: an AI copilot for Finance and Billing Operations, on one governed platform.

For: CFO / VP Revenue Accounting · Director of Billing Operations · VP Data Engineering

---

## 2 · Executive summary: Apex loses 14% of its net revenue to DSP billing gaps each quarter. Most of it is recoverable faster.

| | Today (Q3 2026) | With the Copilot |
|---|---|---|
| Money | **$8.9M** Apex net exposure per quarter: 14% of Q3 net revenue ($61.9M), after publisher pass-through | **$4.7M / year** back to Apex's P&L: every recoverable case pursued, not ~60% |
| Speed | **21 days** to resolve one dispute (p90 33 days, ~270 cases a month) | **≤ 7 days** dispute cycle target; ≈ $2.8M cash released once |
| Accuracy | **55%** right root cause on first look (analysts' rules of thumb on the 715 Q3 cases) | **92%** right root cause (model on the same 715 cases); ≈ 3 FTE redeployed |

---

## 3 · The problem: a $24M billing shortfall in Q3. $8.9M of it comes out of Apex's own P&L.

From the gap with DSPs to Apex's own loss, Q3 2026:

| Measure | Q3 2026 |
|---|---:|
| Billing shortfall (all deals) | $24.4M |
| Revenue at risk (715 cases over tolerance) | $18.1M |
| Apex net exposure (after publisher pass-through) | $8.9M |

Gross CTV spend in Q3 was $432M; Apex keeps a 14.3% take ($61.9M net revenue). The shortfall is 5.7% of gross; the
exposure is 14% of Apex's net.

**Who absorbs the gap depends on the publisher's terms:**
- **Paid on Apex's count:** 279 cases, $7.3M at risk. Apex still owes the publisher, so **all $7.3M is Apex's loss**.
- **Paid on cleared revenue:** 436 cases, $10.8M at risk. The publisher absorbs most of it; **Apex loses $1.6M** (its take), plus publisher goodwill.

39 of 40 DSPs had at least one case. The top 5 DSPs account for 38% of revenue at risk.

---

## 4 · Why the counts don't match: five root causes, each with a different fix. Only two are worth chasing.

| Root cause | What happens in CTV | Fix | Q3 revenue at risk |
|---|---|---|---:|
| IVT filtering | DSP's fraud vendor removes spoofed CTV traffic | Credit only third-party-verified IVT | $7.9M |
| **Billing error** (chase) | Unexplained under-reporting on some days | Dispute with log evidence; 60% recovered historically | $5.2M |
| **Missing data** (chase) | Days missing from the DSP's report | Get the days, then bill; 90% recovered | $3.5M |
| Within tolerance | Daily noise flagged the deal; the month is within contract | No action | $0.8M |
| Timezone shift | DSP reports in US time; primetime crosses midnight UTC | Ask for UTC reporting; no billing change | $0.6M |

348 cases / $8.5M are IVT or timezone: a credit or a reporting fix, not a chase. Root causes are the model's calls on the Q3 queue.

---

## 5 · How it works for Billing Ops: from spreadsheets and guesswork to one ranked queue with the cause and the draft ready

**Today:** download each DSP's file → spreadsheet lookups → guess the cause (right 55% of the time) → email back and
forth for 21 days → write off what's left.

**With the Copilot:**
1. **Ingest & check** (Lakeflow): partner files land and are quality-checked the same day.
2. **Reconcile** (Unity Catalog): every deal vs. Apex's logs, daily and monthly, with Apex's net exposure.
3. **Explain** (ML + GenAI): a model names the root cause; AI drafts the dispute from the evidence.
4. **Resolve** (App + Lakebase): analysts work one ranked queue; every action is logged.
5. **Ask** (Genie): Finance asks questions in plain English, on governed numbers.

---

## 6 · The Reconciliation Workbench: two September cases with similar gaps, one costs Apex 6× more than the other

| | Mosaic Bid · Bluebird TV OS · Entertainment PMP | Umbra Ads · Pinecrest Kids TV · Sports PMP |
|---|---|---|
| Gap with the DSP | $252,043 (23% vs a 5% threshold) | $203,794 (16% vs a 5% threshold) |
| Model | Billing error (100%) | IVT filtering (100%) |
| Publisher terms | Paid on cleared revenue, 13.4% take | Paid on Apex's count |
| **Apex net exposure** | **$33,774 (13% of the gap)** | **$203,794 (100% of the gap)** |
| Action | Dispute it, but it's not the priority for Apex's P&L | Every dollar is Apex's: credit only verified IVT, recover the rest |

In the app: Close overview (shortfall, revenue at risk, Apex exposure, recovered) · Triage queue ranked by dollars, with
the model's cause · Case detail with evidence, AI summary and an editable dispute email · Ask Genie.

---

## 7 · AI you can check: the model is right 92% of the time on the cases analysts work, vs. 55% today

Right root cause on the 715 Q3 review cases (vs. true cause): today's rules of thumb **55%**, Copilot model **92%**.
Macro F1 0.91 vs 0.41. Trained on 1,615 resolved Jan–Jun disputes (with ~11% analyst labelling mistakes, like real life),
tested on Jul–Sep. Analysts confirm or override every call, and that feedback retrains the model.

- **250** dispute drafts from a JSON evidence pack, Claude via `ai_query`
- **100%** of dollar figures traced back to the evidence
- **100%** consistent with each contract's billing basis
- **4.7 / 5** accuracy from an independent AI judge (n = 30)
- **14 / 14** finance questions Genie answered correctly vs. reference SQL

---

## 8 · Impact on your KPIs: ≈ $4.7M a year to Apex's P&L, ≈ $2.8M of cash released and ≈ 3 analysts' capacity back

| KPI | Owner | Baseline (Q3 2026) | Target | Annual value |
|---|---|---|---|---|
| Net revenue recovered | CFO | $3.0M recoverable to Apex's P&L per quarter; ~60% of cases worked today* | Pursue every recoverable case | ≈ $4.7M / year to P&L (≈ $10M gross cash) |
| Dispute cycle time / DSO | CFO | 21 days avg · 33 days p90 | ≤ 7 days | ≈ $2.8M cash released once (~$200K/day × 14 days) |
| Analyst effort | Billing Ops | ~270 cases/month × ~2.5 h* ≈ 4.2 FTE | ~45 min per case | ≈ 3 FTE redeployed |
| Right fix first time | Billing Ops | Right cause 55% of the time | 92% (model) | 348 cases/quarter go straight to a credit or reporting fix |
| Month-end close | CFO | ~10 business days* | ~4 days | Faster, auditable close |

\* Assumptions to validate in discovery: today's coverage (60%), effort per case (2.5 h), close length (10 days), and
publisher payment terms by deal. Everything else is computed from the build's data.

---

## 9 · What it costs to run: ≈ $55K a year at full volume, for ≈ $4.7M a year to the P&L (~85× return)

| Component | Measured on this build (list price) | Annual estimate |
|---|---|---:|
| Daily build: pipeline, model, AI drafts | ≈ $3.80 per run (6 runs in October, ~9 min each) | ≈ $1.4K |
| Reconciliation Workbench app | ≈ $11 per day, always on | ≈ $4K |
| Lakebase case store + sync | < $1 for the month | negligible |
| **Total at build scale** | | **≈ $5.4K** |
| **Budget at Apex's full volume (10×)** | | **≈ $55K** |

Measured from Databricks system billing tables for this build (`evidence/11_build_cost`). All compute is serverless and
can be capped with budget policies. The SQL warehouse is shared, so it isn't included.

---

## 10 · What each of you gets: one platform, three wins

**CFO / VP Revenue Accounting**
- *More net revenue, sooner:* ≈ $4.7M a year to the P&L, plus faster collection.
- *Your real exposure:* every gap split into what Apex absorbs vs. what passes through, by partner, deal and cause.
- *Audit-ready controls:* lineage from partner file to invoice; every analyst action logged; Finance-only dollars.

**Director of Billing Operations**
- *One ranked queue:* work the dollars that hit Apex first.
- *Right cause, ready draft:* 92% right on first look; dispute drafted from evidence and contract.
- *By the book:* credit only verified IVT; bad partner files caught on arrival.

**VP Data Engineering**
- *One governed platform:* ingest, ML, case workflow and natural-language questions without copying data across tools.
- *Policies in the platform:* row filters and masks on every table, including Genie's.
- *Simple to run:* one bundle, one serverless job, ~9 minutes a day.

---

## 11 · How it's built, and proof it runs: end to end on Databricks, from raw partner files to the analyst's workbench

Lakeflow (Auto Loader + declarative pipeline, bronze → silver → gold, 4 data-quality rules) → Unity Catalog (row filters
and column masks on every queryable table, tags, lineage) → ML + GenAI (root-cause model in MLflow `@champion`, Claude
drafts via `ai_query`, auto-checked) → Lakebase (Postgres case store: status, audit trail, credits, live in Unity
Catalog) → Genie (plain-English questions on the same governed numbers) → Databricks App (Reconciliation Workbench).

Proof from the committed run output:
- **3.57M** hourly log rows · 158K DSP report rows · 9 months · 40 DSPs · 800 deals
- **1,728** bad partner rows caught by the quality rules before billing
- **92% · 0.91** model accuracy · macro F1 on the 715 Q3 cases
- **14 / 14** Genie answers match reference SQL
- **PASS** app test: open → send → resolve with a verified IVT credit, live in Lakebase and Unity Catalog

---

## 12 · Rollout plan and next steps: a 30-day pilot on the top 5 DSPs, with success criteria agreed up front

| When | Phase | What | Success |
|---|---|---|---|
| Days 0–30 | Pilot | Top 5 DSPs (38% of revenue at risk) on Apex's real files, alongside the spreadsheets | Root-cause agreement with analysts ≥ 85% |
| Days 31–60 | Scale | All 40 DSPs; analysts sign in with their own access (on-behalf-of-user) | Cycle time ≤ 10 days |
| Days 61–90 | Run | Retire the spreadsheet process; retrain on analyst-confirmed causes | Cycle time ≤ 7 days, close ≤ 4 days |

**What we're asking for:**
1. **Discovery session with Billing Ops** to confirm coverage, effort per case, close length and publisher payment terms.
2. **One month of data:** auction log extracts + billing files for the top 5 DSPs.
3. **A pilot sponsor** in Revenue Accounting, with a day-30 readout on recovered dollars and cycle time.
