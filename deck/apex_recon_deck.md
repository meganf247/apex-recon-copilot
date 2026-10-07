# Close faster, recover more
## AI-powered CTV revenue reconciliation for Apex Exchange

Prepared for: CFO / VP Revenue Accounting · Director of Billing Operations · VP Data Engineering

---

## 1 · The headline

**$18.1M of Q3 CTV revenue is in dispute with DSPs. $6.1M of it is recoverable, and today each case takes 3 weeks.**

The Reconciliation Copilot finds every gap the day a partner's file lands, tells Billing Ops *why* it happened,
drafts the dispute, and tracks it to cash, on one governed platform.

| What changes | Today | With the Copilot |
|---|---|---|
| Root cause right on first look | 82% (analyst rules of thumb) | **95%** (model, Jul–Sep test) |
| Time to resolve a dispute | 21 days avg · 33 days p90 | **Target ≤ 7 days** |
| Cases that need a credit or a reporting fix, not a chase | Not separated | **359 cases / $8.7M** routed straight to the right fix |
| Bad rows in partner files | Found in spreadsheets, if at all | **1,728 caught automatically** before billing |

---

## 2 · Why this matters to Apex

- Apex sits in the middle of the money: **DSPs pay Apex, Apex pays publishers** and keeps its fee. When a DSP pays on
  a lower count than Apex owes the publisher, **Apex eats the difference**.
- Q3 2026: **$432M gross CTV revenue; $24.4M (5.7%) not matched by DSP reports.**
- 715 deal-months across **39 of 40 DSPs** needed review in Q3.
- Disputed invoices sit unpaid: about **$200K of disputed revenue a day**.

---

## 3 · Why the counts don't match

| Root cause | What happens in CTV | What to do | Q3 exposure |
|---|---|---|---|
| IVT filtering | The DSP's fraud vendor removes spoofed CTV traffic | Credit only verified IVT | $8.2M |
| Billing error | Unexplained under-reporting on some days | Dispute (60% recovered historically) | $4.9M |
| Missing data | Days missing from the DSP's report | Get the days, then bill (90% recovered) | $3.5M |
| Timezone shift | DSP reports in US time; primetime crosses midnight UTC | Ask for UTC reporting; no billing change | $0.6M |
| Within tolerance | Normal noise near the threshold | None | $0.9M |

*Recovery rates are Billing Ops' actual Jan–Jun 2026 outcomes. Real cases are often mixed (e.g. a billing error plus
some IVT); the model names the main cause.*

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

- **Close overview:** September: Apex $153.5M vs DSP-reported $144.6M, **$8.9M at risk**, 219 cases, recovered-to-date.
- **Triage queue:** cases ranked by dollars at risk, with the model's root cause and confidence.
- **Case detail:** e.g. *Mosaic Bid · Bluebird TV OS · Entertainment PMP, September: $252,043 gap (23%) vs a 5%
  threshold. Model: billing error (99.8%).* Daily Apex-vs-DSP chart, evidence, AI case summary, an editable dispute
  email, and Send / Resolve / Approve credit.
- **Ask Genie:** *"What's our revenue at risk by partner team for September?"* → Central $3.52M, Atlantic $2.44M,
  Pacific $2.23M, EMEA $0.72M.

---

## 6 · Impact on your KPIs

| KPI (owner) | Baseline (Q3 2026 data) | Target | Annual value* |
|---|---|---|---|
| Revenue recovered from DSPs (CFO) | $6.1M recoverable per quarter; team reaches ~60% of cases today* | Pursue every recoverable case | **≈ $10M / year** |
| Dispute cycle time / DSO (CFO) | 21 days | ≤ 7 days | **≈ $2.8M cash released** (one-time; ~$200K/day × 14 days) |
| Analyst effort (Billing Ops) | ~270 cases/month × ~2.5 h* ≈ 4.2 FTE | ~45 min per case (draft + evidence ready) | **≈ 3 FTE redeployed** |
| Right fix first time (Billing Ops) | Every flagged case gets chased | Half the queue goes straight to a credit or reporting fix | 359 cases / quarter not chased |
| Month-end close (CFO) | ~10 business days* | ~4 days | Faster, auditable close |

\* Assumptions to validate in discovery: today's coverage (60%), manual effort per case (2.5 h), close length (10 days).
Everything else is computed from the build's data.

---

## 7 · For the CFO

- **More cash, sooner:** ≈ $10M a year of recoverable revenue that currently goes stale, plus faster collection.
- **Audit-ready:** every number traces from the partner file to the invoice (Unity Catalog lineage), and every analyst
  action is logged.
- **Controls:** dollar figures are visible to Finance only; partner managers see only their own DSPs. Enforced by the
  platform, not the app.

---

## 8 · For the Director of Billing Operations

- One queue, ranked by dollars, so the team works the right cases first.
- The right root cause on first look 95% of the time, vs 82% today. Analysts confirm or override, and that feedback
  retrains the model.
- Dispute emails drafted from the evidence and the contract: 250 drafts, every dollar figure checked, every ask checked
  against the contract's billing basis, rated 4.8/5 for accuracy by an independent AI judge.
- Bad partner files caught on arrival, not at month-end.

---

## 9 · How it works: one governed platform

| Need | Databricks |
|---|---|
| Ingest SSP logs + DSP reports, check quality | **Lakeflow**: bronze → silver → gold, 4 data-quality rules |
| Govern revenue data by partner and role | **Unity Catalog**: row filters, column masks, lineage |
| Explain the gap, draft the dispute | **ML** (MLflow, model registry) + **GenAI** (`ai_query`, Claude) |
| Live case workflow | **Lakebase** (Postgres), queryable live in Unity Catalog |
| Plain-English questions | **Genie** |
| The analyst's workbench | **Databricks App** |

---

## 10 · Proof from the build

- 3.57M hourly log rows and 158K DSP report rows, covering 9 months, 40 DSPs and 800 CTV deals.
- 1,728 bad partner rows caught by the pipeline's quality rules.
- Root-cause model: F1 **0.92** on Jul–Sep vs **0.58** for today's rules (0.82 vs 0.56 against past analyst labels).
- GenAI: 100% of dollar figures grounded; 100% consistent with the contract; 0 parse failures.
- Genie: **12/12** finance questions answered correctly against reference SQL.
- App: tested end to end, from opening a case to sending the dispute to resolving with a credit. The result shows up
  in Unity Catalog and Genie immediately.

---

## 11 · Rollout plan

| When | What | Success measure |
|---|---|---|
| Days 0–30 | Pilot with the **top 5 DSPs (38% of Q3 revenue at risk)** on Apex's real files; analysts run the workbench alongside spreadsheets | Root-cause agreement with analysts ≥ 85% |
| Days 31–60 | All 40 DSPs; on-behalf-of-user access in the app | Cycle time ≤ 10 days |
| Days 61–90 | Retire the spreadsheet process; retrain on analyst-confirmed causes | Cycle time ≤ 7 days, close ≤ 4 days |

---

## 12 · Next steps

1. **Discovery session with Billing Ops** to validate the assumptions (coverage, effort per case, close length).
2. **Data access:** one month of auction log extracts + DSP billing files for the top 5 DSPs.
3. **Pilot sponsor:** VP Revenue Accounting, with success criteria agreed up front.
4. **Executive readout** at day 30 with recovered dollars and cycle-time results.
