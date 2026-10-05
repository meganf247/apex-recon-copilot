"""Create (or replace) the Apex Exchange reconciliation Genie space: tables, instructions, sample questions and
certified example SQL. Prints the space ID.

Usage: python scripts/create_genie_space.py [--profile megan-fevm] [--warehouse <id>] [--space-id <existing id>]
"""
import argparse
import json
import subprocess
import uuid

C = "apex_recon"
TABLES = [f"{C}.gold.case_workbench", f"{C}.gold.dispute_queue", f"{C}.gold.publisher_recon_month",
          f"{C}.gold.recon_deal_month", f"{C}.gold.recon_partner_month", f"{C}.ops.dispute_case_status",
          f"{C}.silver.dim_deals", f"{C}.silver.dim_dsps", f"{C}.silver.dim_publishers"]

INSTRUCTIONS = """You answer questions for Apex Exchange's Finance and Billing Operations teams about CTV revenue reconciliation.
Business context: Apex Exchange is a CTV sell-side platform (SSP). DSPs pay Apex for impressions; Apex pays publishers their revenue share and keeps the rest (take rate).
Each month Apex reconciles its own auction logs (ssp_* columns, the system of record) against each DSP's billing report (dsp_* columns).
Definitions:
- revenue gap = ssp_revenue_usd - dsp_revenue_usd; positive means the DSP reported less than Apex delivered.
- revenue_gap_pct = 100 * revenue gap / ssp_revenue_usd.
- revenue at risk = revenue_at_risk_usd (positive gaps only). Always use this column for "money at risk" or "exposure".
- A partner or deal is "over threshold" when abs(revenue_gap_pct) > discrepancy_threshold_pct (the contract tolerance).
- needs_review = over threshold OR at least 30% of days with a daily gap over 7.5%.
- billing_month is a 'yyyy-MM' string. "This quarter" / "Q3" means billing_month IN ('2026-07','2026-08','2026-09'). The latest close is '2026-09'.
- Root causes (predicted_root_cause / confirmed_root_cause): WITHIN_TOLERANCE, TIMEZONE_SHIFT, IVT_FILTERING, SSAI_BEACON_LOSS, DEAL_ID_MISMAPPING, FX_MISMATCH, LATE_OR_MISSING_DATA, GENUINE_BILLING_ERROR. Present them in plain words (e.g. "SSAI beacon loss").
- Dispute workflow status lives in ops.dispute_case_status (OPEN, IN_REVIEW, SENT_TO_PARTNER, RESOLVED). A case with no row there is OPEN.
- Prefer gold.recon_partner_month for partner-level questions, gold.recon_deal_month for deal-level questions, gold.dispute_queue for open cases and model root causes.
Counting: when asked "how many" partners/deals meet a condition across several months, return ONE row with the count (aggregate per entity in a subquery, then count).
Formatting: report money in USD rounded to whole dollars, percentages to one decimal. Sort by revenue at risk descending unless asked otherwise."""

QUESTIONS = [
    "What's our total revenue at risk by DSP for the September close?",
    "Which DSPs were over threshold in all three months of Q3?",
    "How much revenue at risk did timezone issues cause in Q3?",
    "What's the discrepancy rate on live sports vs VOD, by SSAI vendor, this quarter?",
    "How many disputes are still open and how much money do they cover?",
    "What take rate did we earn by publisher type in September?",
]

EXAMPLES = [
    ("Revenue at risk by DSP for a billing month",
     f"""SELECT dsp_name, partner_team, round(revenue_at_risk_usd) AS revenue_at_risk_usd, round(revenue_gap_pct, 1) AS revenue_gap_pct,
  discrepancy_threshold_pct, over_threshold, deals_needing_review
FROM {C}.gold.recon_partner_month WHERE billing_month = '2026-09' ORDER BY revenue_at_risk_usd DESC"""),
    ("DSPs over threshold every month of Q3",
     f"""SELECT dsp_name, partner_team, round(sum(revenue_at_risk_usd)) AS q3_revenue_at_risk_usd
FROM {C}.gold.recon_partner_month WHERE billing_month IN ('2026-07','2026-08','2026-09')
GROUP BY dsp_name, partner_team HAVING sum(CASE WHEN over_threshold THEN 1 ELSE 0 END) = 3
ORDER BY q3_revenue_at_risk_usd DESC"""),
    ("How many DSPs were over threshold in every month of Q3",
     f"""SELECT count(*) AS dsps_over_threshold_all_q3_months FROM (
  SELECT dsp_id FROM {C}.gold.recon_partner_month WHERE billing_month IN ('2026-07','2026-08','2026-09')
  GROUP BY dsp_id HAVING sum(CASE WHEN over_threshold THEN 1 ELSE 0 END) = 3)"""),
    ("Revenue at risk by root cause this quarter",
     f"""SELECT predicted_root_cause, count(*) AS cases, round(sum(revenue_at_risk_usd)) AS revenue_at_risk_usd
FROM {C}.gold.dispute_queue GROUP BY predicted_root_cause ORDER BY revenue_at_risk_usd DESC"""),
    ("Open disputes and the money they cover",
     f"""SELECT coalesce(s.status, 'OPEN') AS status, count(*) AS cases, round(sum(q.revenue_at_risk_usd)) AS revenue_at_risk_usd,
  round(sum(coalesce(s.recovered_usd, 0))) AS recovered_usd
FROM {C}.gold.dispute_queue q LEFT JOIN {C}.ops.dispute_case_status s USING (case_id)
GROUP BY 1 ORDER BY 2 DESC"""),
]


def hexid():
    return uuid.uuid4().hex


def serialized():
    return json.dumps({
        "version": 1,
        "config": {"sample_questions": sorted([{"id": hexid(), "question": [q]} for q in QUESTIONS], key=lambda x: x["id"])},
        "data_sources": {"tables": [{"identifier": t} for t in sorted(TABLES)]},
        "instructions": {
            "text_instructions": [{"id": hexid(), "content": [INSTRUCTIONS]}],
            "example_question_sqls": sorted([{"id": hexid(), "question": [q], "sql": [s]} for q, s in EXAMPLES],
                                            key=lambda x: x["id"]),
        },
    })


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--profile", default="megan-fevm")
    p.add_argument("--warehouse", default="75019f3de4c19846")
    p.add_argument("--space-id")
    a = p.parse_args()
    body = {"title": "Apex Exchange · CTV Revenue Reconciliation",
            "description": "Ask about DSP billing discrepancies, revenue at risk, root causes and dispute status for Apex Exchange's CTV business.",
            "warehouse_id": a.warehouse, "serialized_space": serialized()}
    method, path = ("patch", f"/api/2.0/genie/spaces/{a.space_id}") if a.space_id else ("post", "/api/2.0/genie/spaces")
    out = subprocess.run(["databricks", "api", method, path, "-p", a.profile, "--json", json.dumps(body)],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(out.stderr)
    print(json.loads(out.stdout).get("space_id"))
