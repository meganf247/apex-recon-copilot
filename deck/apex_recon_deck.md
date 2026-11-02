# Close faster, recover more
## AI-powered CTV revenue reconciliation for Apex Exchange

Prepared for: CFO / VP Revenue Accounting · Director of Billing Operations · VP Data Engineering

---

## 1 · The headline

**$8.9M of Apex's own Q3 net revenue (14% of it) is exposed to DSP billing gaps. $3.0M of that is recoverable,
and today each dispute takes 3 weeks.**

The Reconciliation Copilot finds every gap the day a partner's file lands, tells Billing Ops *why* it happened,
drafts the dispute, and tracks it to cash, on one governed platform.

| What changes | Today | With the Copilot |
|---|---|---|
| Right root cause on the cases analysts work (715 in Q3) | 55% (analyst rules of thumb) | **92%** (model, Jul–Sep test) |
| Time to resolve a dispute | 21 days avg · 33 days p90 | **Target ≤ 7 days** |
| Cases that need a credit or a reporting fix, not a chase | Not separated | **348 cases / $8.5M** routed straight to the right fix |
| Bad rows in partner files | Found in spreadsheets, if at all | **1,728 caught automatically** before billing |

---

## 2 · Why this matters to Apex

- Apex sits in the middle of the money: **DSPs pay Apex, Apex pays publishers and keeps its take** (14.3% on average).
  Q3 2026: **$432M gross CTV spend, $61.9M Apex net revenue.**
- When a DSP pays on a lower count, who absorbs it depends on the publisher's terms:
    - **Publisher paid on Apex's count** (most guaranteed deals): Apex still owes the publisher, so **Apex absorbs the whole gap**.
    - **Publisher paid on cleared revenue:** the publisher absorbs most of it; Apex loses its take, and the publisher relationship takes the hit.
- Q3: **$24.4M billing shortfall** across all deals (5.7% of gross). **$18.1M** of it is on 715 deal-months over
  contract tolerance across 39 of 40 DSPs: that's the **revenue at risk**. **$8.9M** of that hits Apex's own P&L.
- Disputed invoices sit unpaid: about **$200K of revenue at risk a day**.

| Q3 2026 | Cases | Revenue at risk | Apex net exposure |
|---|---:|---:|---:|
| Publisher paid on Apex's count | 279 | $7.3M | **$7.3M** |
| Publisher paid on cleared revenue | 436 | $10.8M | **$1.6M** |
| **Total** | **715** | **$18.1M** | **$8.9M** |

---

## 3 · Why the counts don't match

| Root cause | What happens in CTV | What to do | Q3 revenue at risk | Apex net exposure |
|---|---|---|---:|---:|
| IVT filtering | The DSP's fraud vendor removes spoofed CTV traffic | Credit only third-party-verified IVT | $7.9M | $4.1M |
| Billing error | Unexplained under-reporting on some days | Dispute (60% recovered historically) | $5.2M | $2.4M |
| Missing data | Days missing from the DSP's report | Get the days, then bill (90% recovered) | $3.5M | $1.7M |
| Timezone shift | DSP reports in US time; primetime crosses midnight UTC | Ask for UTC reporting; no billing change | $0.6M | $0.3M |
| Within tolerance | Daily noise flagged the deal; the month is within contract | None | $0.8M | $0.5M |

*Root causes are the model's calls on the Q3 queue. Recovery rates are Billing Ops' actual Jan–Jun 2026 outcomes. Real
cases are often mixed (e.g. a billing error plus some IVT); the model names the main cause.*

---

## 4 · Today vs. tomorrow

**Today:** download each DSP's file → spreadsheet lookups → email back and forth → guess the cause → write off what's left.

**Tomorrow:**
1. Partner files are ingested and checked automatically (Lakeflow).
2. Every deal is reconciled against Apex's logs, daily and monthly.
3. A model explains *why* each gap happened, and a draft dispute is ready (AI).
4. Analysts work one ranked queue and resolve in a click (Databricks App + Lakebase).
5. Finance asks questions in plain English (Genie).

---

## 5 · The Reconciliation Workbench

- **Close overview:** September: Apex $153.5M vs DSP-reported $144.6M. $8.9M billing shortfall, of which
  **$6.8M is at risk in 219 cases** and **$3.3M is Apex's own exposure**.
- **Triage queue:** cases ranked by dollars at risk, with the model's root cause and confidence.
- **Case detail:** e.g. *Mosaic Bid · Bluebird TV OS · Entertainment PMP, September: $252,043 gap (23%) vs a 5%
  threshold. Model: billing error (100%). Publisher paid on cleared revenue at a 13.4% take, so Apex's own exposure is
  $33,774.* Daily Apex-vs-DSP chart, evidence, AI case summary, an editable dispute email, and Send / Resolve.
  For IVT, the analyst credits only what the partner's third-party report verifies and recovers the rest.
- **Ask Genie:** *"What's our revenue at risk by partner team for September?"* → Central $2.88M, Pacific $1.79M,
  Atlantic $1.58M, EMEA $0.52M.

---

## 6 · Impact on your KPIs

| KPI (owner) | Baseline (Q3 2026 data) | Target | Annual value |
|---|---|---|---|
| Net revenue recovered (CFO) | $3.0M recoverable to Apex's P&L per quarter ($6.3M gross); team works ~60% of cases today* | Pursue every recoverable case | **≈ $4.7M / year to Apex's P&L** (40% × $3.0M × 4; ≈ $10M gross cash) |
| Dispute cycle time / DSO (CFO) | 21 days | ≤ 7 days | **≈ $2.8M cash released** (one-time; ~$200K/day × 14 days) |
| Analyst effort (Billing Ops) | ~270 cases/month × ~2.5 h* ≈ 4.2 FTE | ~45 min per case (draft + evidence ready) | **≈ 3 FTE redeployed** |
| Right fix first time (Billing Ops) | Rules of thumb pick the right cause 55% of the time | Model: 92% | 348 cases / quarter go straight to a credit or reporting fix |
| Month-end close (CFO) | ~10 business days* | ~4 days | Faster, auditable close |

\* Assumptions to validate in discovery: today's coverage (60%), manual effort per case (2.5 h), close length (10 days).
Everything else is computed from the build's data.

---

## 7 · What it costs to run

| | Measured on this build (list price) | Production estimate |
|---|---|---|
| Full build (ingest, reconcile, retrain, 250 AI drafts) | **≈ $3.80 per run** (6 runs in October, ~9 min each) | Daily: ≈ $1.4K / year |
| Reconciliation Workbench app | ≈ $11 / day, always on | ≈ $4K / year |
| Lakebase case store + sync | < $1 for the month | negligible |
| **Total** | | **≈ $5.4K / year at build scale; budget ≈ $55K / year at 10× for Apex's full volume** |

**≈ $4.7M a year to Apex's P&L for ≈ $55K a year to run: ~85× return**, before cycle time and analyst capacity.
*Costs come from Databricks system billing tables for this build. The SQL warehouse is shared, so it isn't included.*

---

## 8 · For the CFO

- **More net revenue, sooner:** ≈ $4.7M a year to Apex's P&L that currently goes stale, plus faster collection.
- **Know your real exposure:** every gap split into what Apex absorbs vs. what passes through to publishers, by
  partner, deal and cause.
- **Audit-ready:** every number traces from the partner file to the invoice (Unity Catalog lineage), and every analyst
  action is logged.
- **Controls:** dollar figures are visible to Finance only; partner managers see only their own DSPs, in every
  reconciliation table, the case queue and Genie. Enforced by the platform, not the app.

---

## 9 · For the Director of Billing Operations

- One queue, ranked by dollars, so the team works the right cases first.
- The right root cause on the cases you actually work 92% of the time, vs 55% for today's rules of thumb.
  Analysts confirm or override, and that feedback retrains the model.
- Dispute emails drafted from the evidence and the contract: 250 drafts, every dollar figure checked, every ask checked
  against the contract's billing basis, rated 4.7/5 for accuracy by an independent AI judge.
- IVT handled by the book: credit only verified invalid traffic, recover the rest.
- Bad partner files caught on arrival, not at month-end.

---

## 10 · How it works: one governed platform

| Need | Databricks |
|---|---|
| Ingest SSP logs + DSP reports, check quality | **Lakeflow**: bronze → silver → gold, 4 data-quality rules |
| Govern revenue data by partner and role | **Unity Catalog**: row filters, column masks, lineage |
| Explain the gap, draft the dispute | **ML** (MLflow, model registry) + **GenAI** (`ai_query`, Claude) |
| Live case workflow | **Lakebase** (Postgres), queryable live in Unity Catalog |
| Plain-English questions | **Genie** |
| The analyst's workbench | **Databricks App** |

---

## 11 · Proof from the build

- 3.57M hourly log rows and 158K DSP report rows, covering 9 months, 40 DSPs and 800 CTV deals.
- 1,728 bad partner rows caught by the pipeline's quality rules.
- Root-cause model on the 715 Q3 cases: **92% accuracy, macro F1 0.91** vs 55% / 0.41 for today's rules
  (0.85 vs 0.54 F1 against past analyst labels).
- GenAI: 100% of dollar figures grounded; 100% consistent with the contract; 0 parse failures.
- Genie: **14/14** finance questions answered correctly against reference SQL.
- App: tested end to end, from opening a case to sending the dispute to resolving with a verified IVT credit. The
  result shows up in Unity Catalog and Genie immediately.

---

## 12 · Rollout plan

| When | What | Success measure |
|---|---|---|
| Days 0–30 | Pilot with the **top 5 DSPs (38% of Q3 revenue at risk)** on Apex's real files; analysts run the workbench alongside spreadsheets | Root-cause agreement with analysts ≥ 85% |
| Days 31–60 | All 40 DSPs; on-behalf-of-user access in the app | Cycle time ≤ 10 days |
| Days 61–90 | Retire the spreadsheet process; retrain on analyst-confirmed causes | Cycle time ≤ 7 days, close ≤ 4 days |

---

## 13 · Next steps

1. **Discovery session with Billing Ops** to validate the assumptions (coverage, effort per case, close length) and
   confirm publisher payment terms by deal.
2. **Data access:** one month of auction log extracts + DSP billing files for the top 5 DSPs.
3. **Pilot sponsor:** VP Revenue Accounting, with success criteria agreed up front.
4. **Executive readout** at day 30 with recovered dollars and cycle-time results.
