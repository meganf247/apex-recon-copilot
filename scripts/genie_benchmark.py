"""Benchmark the Genie space: ask each business question through the Conversation API, capture the SQL Genie wrote
and its answer, and compare against an independently written reference query. Writes markdown evidence.

Usage: python scripts/genie_benchmark.py <space_id> evidence/06_genie_benchmark.md [--profile megan-fevm]
"""
import argparse
import json
import subprocess
import time

from run_sql import fmt, run

C = "apex_recon"
# (question, reference SQL, how to compare: the first value of Genie's first row must match the reference's)
BENCH = [
    ("What was the total revenue at risk across all DSPs for the September 2026 close?",
     f"SELECT round(sum(revenue_at_risk_usd)) FROM {C}.gold.recon_partner_month WHERE billing_month = '2026-09'"),
    ("Which DSP had the most revenue at risk in September 2026?",
     f"SELECT dsp_name FROM {C}.gold.recon_partner_month WHERE billing_month = '2026-09' ORDER BY revenue_at_risk_usd DESC LIMIT 1"),
    ("How many DSPs were over their contract discrepancy threshold in all three months of Q3 2026?",
     f"""SELECT count(*) FROM (SELECT dsp_id FROM {C}.gold.recon_partner_month WHERE billing_month IN ('2026-07','2026-08','2026-09')
         GROUP BY dsp_id HAVING sum(CASE WHEN over_threshold THEN 1 ELSE 0 END) = 3)"""),
    ("How many open dispute cases are in the Q3 queue in total?",
     f"SELECT count(*) FROM {C}.gold.dispute_queue"),
    ("What is the most common predicted root cause among Q3 dispute cases?",
     f"SELECT predicted_root_cause FROM {C}.gold.dispute_queue GROUP BY 1 ORDER BY count(*) DESC LIMIT 1"),
    ("Which predicted root cause accounts for the most revenue at risk in Q3?",
     f"SELECT predicted_root_cause FROM {C}.gold.dispute_queue GROUP BY 1 ORDER BY sum(revenue_at_risk_usd) DESC LIMIT 1"),
    ("How much revenue at risk is attributed to timezone shift cases in Q3?",
     f"SELECT round(sum(revenue_at_risk_usd)) FROM {C}.gold.dispute_queue WHERE predicted_root_cause = 'TIMEZONE_SHIFT'"),
    ("Which partner team has the most revenue at risk in Q3?",
     f"SELECT partner_team FROM {C}.gold.dispute_queue GROUP BY 1 ORDER BY sum(revenue_at_risk_usd) DESC LIMIT 1"),
    ("How many deals needed review in the September 2026 close?",
     f"SELECT sum(CAST(needs_review AS INT)) FROM {C}.gold.recon_deal_month WHERE billing_month = '2026-09'"),
    ("Which SSAI vendor has the highest revenue at risk on live content in Q3?",
     f"SELECT ssai_vendor FROM {C}.gold.dispute_queue WHERE is_live GROUP BY 1 ORDER BY sum(revenue_at_risk_usd) DESC LIMIT 1"),
    ("How many dispute cases have been resolved so far?",
     f"SELECT count(*) FROM {C}.ops.dispute_case_status WHERE status = 'RESOLVED'"),
    ("How much money has been recovered from resolved disputes so far?",
     f"SELECT round(sum(recovered_usd)) FROM {C}.ops.dispute_case_status"),
]


def api(profile, method, path, body=None):
    cmd = ["databricks", "api", method, path, "-p", profile] + (["--json", json.dumps(body)] if body else [])
    for attempt in range(4):  # retry transient network errors
        out = subprocess.run(cmd, capture_output=True, text=True)
        if out.returncode == 0:
            return json.loads(out.stdout) if out.stdout.strip() else {}
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(out.stderr)


def ask(profile, space, question):
    base = f"/api/2.0/genie/spaces/{space}"
    m = api(profile, "post", f"{base}/start-conversation", {"content": question})
    cid, mid = m["conversation_id"], m["message_id"]
    for _ in range(90):
        msg = api(profile, "get", f"{base}/conversations/{cid}/messages/{mid}")
        if msg["status"] in ("COMPLETED", "FAILED", "CANCELLED"):
            break
        time.sleep(3)
    sql, rows, text = None, [], []
    for att in msg.get("attachments", []):
        if "text" in att:
            text.append(att["text"]["content"])
        if "query" in att:
            sql = att["query"]["query"]
            res = api(profile, "get", f"{base}/conversations/{cid}/messages/{mid}/attachments/{att['attachment_id']}/query-result")
            rows = res.get("statement_response", {}).get("result", {}).get("data_array", []) or []
    return msg["status"], sql, rows, " ".join(text)


def same(a, b):
    try:
        return abs(float(a) - float(b)) <= max(1.0, 0.005 * abs(float(b)))
    except (TypeError, ValueError):
        return str(a).strip().lower().replace(" ", "_") == str(b).strip().lower().replace(" ", "_")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("space_id")
    p.add_argument("out")
    p.add_argument("--profile", default="megan-fevm")
    p.add_argument("--warehouse", default="75019f3de4c19846")
    a = p.parse_args()
    md, passed = [f"# Genie benchmark: space `{a.space_id}`", ""], 0
    for i, (q, ref_sql) in enumerate(BENCH, 1):
        expected = (run(a.profile, a.warehouse, ref_sql).get("result", {}).get("data_array") or [[None]])[0][0]
        status, sql, rows, text = ask(a.profile, a.space_id, q)
        first = rows[0] if rows else []
        ok = any(same(v, expected) for v in first)
        passed += ok
        md += [f"## {i}. {q}", "", f"- Genie status: {status}  ", f"- Expected (reference SQL): `{expected}`  ",
               f"- Genie first row: `{first}`  ", f"- **{'PASS' if ok else 'FAIL'}**", "",
               "Genie SQL:", "```sql", sql or "(none)", "```", "Reference SQL:", "```sql", ref_sql, "```"]
        if text:
            md += ["", f"Genie text: {text}"]
        md.append("")
        print(f"{i:2d} {'PASS' if ok else 'FAIL'}  expected={expected}  genie={first[:3]}")
    md.insert(2, f"**Accuracy: {passed}/{len(BENCH)} questions answered correctly.**\n")
    open(a.out, "w").write("\n".join(md))
    print(f"{passed}/{len(BENCH)} -> {a.out}")
