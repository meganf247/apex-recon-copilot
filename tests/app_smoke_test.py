"""Headless end-to-end test of the Reconciliation Workbench with Streamlit AppTest against the live workspace:
renders every page, then works the top September IVT case (open -> send dispute -> resolve: credit the IVT the
partner's third-party report verifies, recover the rest) and verifies the writes landed in Lakebase. Prints a text log used as execution evidence.

Run: DATABRICKS_CONFIG_PROFILE=megan-fevm2 LAKEBASE_USER=<you> .venv/bin/python tests/app_smoke_test.py
"""
import os
import sys
import time

from streamlit.testing.v1 import AppTest

os.environ.setdefault("DATABRICKS_WAREHOUSE_ID", "93d767746e247a90")
os.environ.setdefault("GENIE_SPACE_ID", "01f1c1a695ce1f47baa2f07ef9f73663")
os.environ.setdefault("LAKEBASE_HOST", "ep-cold-cell-d2f24olw.database.us-east-1.cloud.databricks.com")
APP = os.path.join(os.path.dirname(__file__), "..", "app", "app.py")


def check(at, label):
    errs = [e.value for e in at.exception] + [e.value for e in at.error]
    print(f"[{'FAIL' if errs else ' OK '}] {label}")
    for e in errs:
        print("       ", str(e)[:500])
    return not errs


def texts(at):
    return [m.label + " = " + str(m.value) for m in at.metric]


at = AppTest.from_file(APP, default_timeout=240)
at.run()
ok = check(at, "Close overview renders")
print("        metrics:", texts(at))

at.sidebar.radio[0].set_value("Triage queue").run()
ok &= check(at, "Triage queue renders")
print("        ", [c.value for c in at.caption][:2])

# Work the highest-$ open September IVT case (the app sorts by revenue at risk)
sys.path.insert(0, os.path.dirname(APP))
import app as appmod  # noqa: E402  (module import re-runs page code harmlessly outside a session)

q = appmod.queue("2026-09")
case = q[(q.status != "RESOLVED") & (q.predicted_root_cause == "IVT_FILTERING")].iloc[0]  # IVT -> credit the DSP for verified invalid traffic
print(f"        selected {case.case_id}: {case.dsp_name} · ${case.revenue_at_risk_usd:,.0f} at risk · model={case.predicted_root_cause}")
at.session_state["case_id"] = case.case_id
at.sidebar.radio[0].set_value("Case detail").run()
ok &= check(at, "Case detail renders (case opened -> IN_REVIEW in Lakebase)")
print("         metrics:", texts(at)[:5])
print("         AI summary:", (at.info[0].value if at.info else "")[:300])

at.button[0].click().run()  # Send to partner
ok &= check(at, "Send dispute to partner")
at.selectbox[0].set_value("CREDIT_ISSUED").run()
verified = round(0.6 * float(case.revenue_at_risk_usd), 2)  # the partner's IVT report verifies 60% of the removed traffic
at.number_input[0].set_value(verified).run()
at.number_input[1].set_value(round(float(case.revenue_at_risk_usd) - verified, 2)).run()
print(f"        verified IVT credit ${verified:,.2f} · recovering the unverified ${float(case.revenue_at_risk_usd) - verified:,.2f}")
[b for b in at.button if b.label == "Confirm resolution"][0].click().run()
ok &= check(at, "Resolve case: credit verified IVT, recover the remainder")

time.sleep(1)
rows = appmod.pg_df("SELECT case_id, status, resolution, confirmed_root_cause, recovered_usd, owner FROM recon.dispute_cases WHERE case_id=%s",
                    (case.case_id,))
events = appmod.pg_df("SELECT event_type, actor, detail FROM recon.case_events WHERE case_id=%s ORDER BY event_id", (case.case_id,))
credits = appmod.pg_df("SELECT amount_usd, approved_by, reason FROM recon.credit_approvals WHERE case_id=%s", (case.case_id,))
print("\nLakebase recon.dispute_cases:\n", rows.to_string(index=False))
print("\nLakebase recon.case_events:\n", events.to_string(index=False))
print("\nLakebase recon.credit_approvals:\n", credits.to_string(index=False))
ok &= (len(rows) == 1 and rows.status[0] == "RESOLVED" and len(credits) == 1
       and abs(float(credits.amount_usd[0]) - verified) < 0.01 and float(rows.recovered_usd[0]) > 0)

at.sidebar.radio[0].set_value("Ask Genie").run()
at.chat_input[0].set_value("What's our total revenue at risk by partner team for the September close?").run()
ok &= check(at, "Ask Genie answers")
print("         Genie:", [m.value for m in at.markdown][-2:])
print("\nRESULT:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
