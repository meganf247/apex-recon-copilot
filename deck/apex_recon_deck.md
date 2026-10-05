# Close faster, recover more
## AI-powered CTV revenue reconciliation for Apex Exchange

Prepared for: CFO / VP Revenue Accounting · Director of Billing Operations · VP Data Engineering

---

## 1 · The headline

**$22.6M of Q3 CTV revenue is in dispute with DSPs. About $11.8M of it is recoverable, and today it takes 3 weeks per case to get it.**

The Reconciliation Copilot finds every discrepancy the day the partner file lands, tells Billing Ops *why* it
happened, drafts the dispute, and tracks it to cash, all on one governed platform.

| What changes | Today | With the Copilot |
|---|---|---|
| Root cause right on first look | 47% (analyst playbook) | **97%** (model, Jul–Sep out-of-time test) |
| Time to resolve a dispute | 20.7 days avg · 34 days p90 | **Target ≤ 7 days** |
| Cases worth chasing, identified up front | Not separated | **323 cases / $5.6M flagged as no-recovery** (timezone, verified IVT) |
| Partner files with bad rows caught before billing | Found in spreadsheets, if at all | **1,718 rows quarantined automatically, with the reason** |

---

## 2 · Why this matters to Apex

- Apex sits in the middle of the money: **DSPs pay Apex, and Apex pays publishers** (~84% of revenue; Apex keeps a ~16% take rate).
  When a DSP pays on a lower count than Apex owes the publisher, **Apex eats the difference**.
- Q3 2026: **$428M gross CTV revenue; $27.9M (6.5%) not matched by DSP reports.**
- 921 deal-months across **39 of 40 DSPs** needed review in Q3, about 360 new disputes every month.
- Disputed invoices sit unpaid. At ~$250K of disputed revenue a day, every day of resolution time is working capital
  locked up.

---

## 3 · Why CTV discrepancies happen (and why spreadsheets can't keep up)

Three systems count the same impression: **Apex's auction logs**, the **DSP's billing report**, and the **publisher's ad server**.

| Root cause | What happens in CTV | Recoverable? | Q3 exposure |
|---|---|---|---|
| SSAI beacon loss | Server-side ad insertion beacons don't fire at peak load and on live events | Partly (40%) | $5.0M |
| IVT filtering | DSP's fraud vendor removes spoofed CTV devices | Credit if verified | $4.6M |
| Deal-ID mis-mapping | DSP books delivery under the wrong deal | Yes (95%) | $3.8M |
| Genuine billing error | Unexplained under-reporting | Mostly (60%) | $3.5M |
| Late / missing data | Report days never arrive | Yes (90%) | $3.2M |
| FX mismatch | EUR/GBP partners convert at the wrong rate | Yes (90%) | $1.3M |
| Timezone shift | Partner reports in ET/PT; primetime crosses midnight UTC | No: reporting fix only | $0.9M |

*Recovery rates are Billing Ops' actual Jan–Jun 2026 outcomes on resolved cases.*

---

## 4 · Today vs. tomorrow

**Today:** download 40 partner portals' files in 3 formats → VLOOKUPs → email back and forth → guess the cause → write off what's left.

**Tomorrow:**
1. Partner files are ingested and validated automatically (Lakeflow).
2. Every deal is reconciled daily and monthly against Apex logs.
3. A model explains *why* each gap happened, and a draft dispute is ready (AI).
4. Analysts work one prioritized queue and resolve in one click (Databricks App + Lakebase).
5. Finance asks questions in plain English (Genie).

---

## 5 · The Reconciliation Workbench (what the analyst sees)

- **Close overview:** September: Apex $146.8M vs DSP-reported $138.5M, **$9.64M at risk**, 287 cases open, recovered-to-date counter.
- **Triage queue:** sorted by dollars at risk, with model root cause and confidence.
- **Case detail:** e.g. *Mosaic Bid · Coastal Home Screen · Sports PMP, Sept: $423,608 gap (12.2%) vs a 7.5% threshold.
  Model: FX mismatch (99.99%).* Daily Apex-vs-DSP chart, evidence tiles, AI case summary, an editable dispute email,
  and Send / Resolve / Approve credit buttons.
- **Ask Genie:** *"What's our revenue at risk by partner team for September?"* → Pacific $5.26M, EMEA $1.74M, Central $1.49M, Atlantic $1.16M.

---

## 6 · Impact on your KPIs

| KPI (owner) | Baseline (Q3 2026 data) | Target | Annual value* |
|---|---|---|---|
| Revenue recovered from DSPs (CFO) | Recoverable exposure $11.8M / quarter; team reaches ~60% of cases today* | Pursue 100% of recoverable cases | **≈ $19M / year** |
| Dispute cycle time / DSO (CFO) | 20.7 days avg | ≤ 7 days | **≈ $3.4M cash released** (one-time; ~$250K/day × 14 days faster) |
| Analyst effort (Billing Ops) | ~360 cases/month × ~2.5 h each* ≈ 5.6 FTE | ~45 min per case (draft + evidence ready) | **≈ 3.9 FTE redeployed** |
| Wasted effort (Billing Ops) | Every flagged case gets chased | 35% of queue triaged as no-recovery | 323 cases / quarter not chased |
| Month-end close (CFO) | ~10 business days* | ~4 days | Faster, auditable close |

\* Assumptions to validate with Apex in discovery: current coverage (60%), manual effort per case (2.5 h), close length (10 days). All other figures are computed from the build's data.

---

## 7 · For the CFO

- **More cash, sooner:** ≈ $19M a year of recoverable revenue that currently goes stale, plus faster collection on disputed invoices.
- **Audit-ready:** every number traces from the partner file to the invoice (Unity Catalog lineage). Every analyst action
  is logged (who, what, when, model vs final cause).
- **Controls:** revenue figures are visible to Finance only; partner managers see only their own DSPs. Enforced by the
  platform, not by the app.
- **A forecastable close:** daily reconciliation means no month-end surprise.

---

## 8 · For the Director of Billing Operations

- One queue, ranked by dollars, so the team works the right cases first.
- Root cause on first look 97% of the time, vs 47% with today's rules of thumb. Analysts confirm or override, and that
  feedback retrains the model.
- Dispute emails drafted from the evidence: 250 drafts, every dollar figure checked against the source, rated 5/5 for
  accuracy and tone by an independent AI judge.
- Bad partner files caught on arrival (unknown deals, duplicates, bad dates, negative counts, wrong seat), not at month-end.

---

## 9 · How it works: one governed platform

| Need | Databricks |
|---|---|
| Ingest 3 partner formats + SSP logs, validate | **Lakeflow** declarative pipelines, Auto Loader, data-quality expectations |
| Govern revenue data by partner and role | **Unity Catalog**: row filters, column masks, tags, lineage |
| Explain the gap, draft the dispute | **ML** (MLflow, model registry) + **GenAI** (`ai_query`, Claude) |
| Live case workflow | **Lakebase** (Postgres) synced with the lakehouse |
| Plain-English questions | **Genie** |
| The analyst's workbench | **Databricks App** |

No data leaves the platform, and there's no separate operational database or BI tool to stitch together.

---

## 10 · Proof from the build

- 3.54M hourly log rows, 157K DSP report rows and 159K publisher rows ingested, covering 9 months, 40 DSPs, 150 CTV publishers and 800 deals.
- 1,718 bad partner rows quarantined, matching the defects injected into the partner files.
- Root-cause model: macro F1 **0.97** out-of-time vs **0.47** for the current playbook.
- GenAI: 100% of dollar figures grounded; 0 parse failures.
- Genie: benchmarked against reference SQL on finance questions (see `evidence/06_genie_benchmark.md`).
- App: end-to-end test from case open → dispute sent → resolved with credit, written to Lakebase and visible in Genie.

---

## 11 · Rollout plan

| When | What | Success measure |
|---|---|---|
| Days 0–30 | Pilot with the **top 5 DSPs (49% of Q3 revenue at risk)** on Apex's real partner files; analysts run the workbench alongside spreadsheets | Root-cause agreement with analysts ≥ 85% |
| Days 31–60 | All 40 DSPs; publisher-side payout reconciliation; on-behalf-of-user access in the app | Cycle time ≤ 10 days |
| Days 61–90 | Retire spreadsheet process; model retraining on analyst-confirmed causes; close on daily reconciliation | Cycle time ≤ 7 days, close ≤ 4 days |

---

## 12 · Next steps

1. **Discovery session with Billing Ops** to validate the baseline assumptions (coverage, effort per case, close length).
2. **Data access:** one month of Apex auction log extracts + DSP billing files for the top 5 DSPs.
3. **Pilot sponsor:** VP Revenue Accounting; success criteria agreed up front.
4. **Executive readout** at day 30 with recovered dollars and cycle-time results.
