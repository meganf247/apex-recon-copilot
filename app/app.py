"""Apex Exchange · CTV Reconciliation Workbench (Databricks App).

Analytics come from Unity Catalog gold tables through a SQL warehouse; the case queue is read from Lakebase
(synced from gold) and every analyst action is written to Lakebase as transactional case state + audit trail.
"""
import json
import os
import time
import uuid

import altair as alt
import pandas as pd
import psycopg
import streamlit as st
from databricks import sql
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config

st.set_page_config(page_title="Apex Exchange · Reconciliation Workbench", layout="wide")

CATALOG = os.getenv("APEX_CATALOG", "apex_recon")
WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID")
GENIE_SPACE_ID = os.getenv("GENIE_SPACE_ID")
PG_ENDPOINT = os.getenv("LAKEBASE_ENDPOINT", "projects/apex-recon-lb/branches/production/endpoints/primary")
PG_HOST = os.getenv("LAKEBASE_HOST")
PG_DB = os.getenv("LAKEBASE_DATABASE", "databricks_postgres")

cfg = Config()
w = WorkspaceClient()
USER = st.context.headers.get("X-Forwarded-Email") or "billing.analyst@apexexchange.example"
RESOLUTIONS = ["RECOVERED", "CREDIT_ISSUED", "NO_ADJUSTMENT", "WRITTEN_OFF"]
CAUSES = ["WITHIN_TOLERANCE", "TIMEZONE_SHIFT", "IVT_FILTERING", "LATE_OR_MISSING_DATA", "GENUINE_BILLING_ERROR"]


# ---------------- data access ----------------

@st.cache_data(ttl=300, show_spinner=False)
def uc(query: str) -> pd.DataFrame:
    with sql.connect(server_hostname=cfg.host.replace("https://", ""), http_path=f"/sql/1.0/warehouses/{WAREHOUSE_ID}",
                     credentials_provider=lambda: cfg.authenticate) as conn, conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall_arrow().to_pandas()


def pg():
    token = w.postgres.generate_database_credential(endpoint=PG_ENDPOINT).token
    return psycopg.connect(host=PG_HOST, dbname=PG_DB, user=os.getenv("LAKEBASE_USER") or cfg.client_id or USER, password=token,
                           sslmode="require", autocommit=True)


def pg_df(query: str, params=None) -> pd.DataFrame:
    with pg() as conn, conn.cursor() as cur:
        cur.execute(query, params)
        return pd.DataFrame(cur.fetchall(), columns=[d.name for d in cur.description])


def pg_exec(statements):
    with pg() as conn, conn.transaction(), conn.cursor() as cur:
        for q, p in statements:
            cur.execute(q, p)


def log_event(case_id, event_type, detail):
    return ("INSERT INTO recon.case_events (case_id, event_type, actor, detail) VALUES (%s, %s, %s, %s)",
            (case_id, event_type, USER, json.dumps(detail, default=str)))


def ensure_case(row):
    pg_exec([
        ("""INSERT INTO recon.dispute_cases (case_id, billing_month, dsp_id, deal_id, status, owner, revenue_at_risk_usd)
            VALUES (%s, %s, %s, %s, 'IN_REVIEW', %s, %s) ON CONFLICT (case_id) DO NOTHING""",
         (row.case_id, row.billing_month, row.dsp_id, row.deal_id, USER, float(row.revenue_at_risk_usd or 0))),
        ("""INSERT INTO recon.case_events (case_id, event_type, actor, detail)
            SELECT %s, 'CREATED', %s, %s WHERE NOT EXISTS (SELECT 1 FROM recon.case_events WHERE case_id = %s)""",
         (row.case_id, USER, json.dumps({"model_root_cause": row.predicted_root_cause, "confidence": float(row.confidence)}),
          row.case_id)),
    ])


def queue(month: str) -> pd.DataFrame:
    return pg_df("""
        SELECT q.*, coalesce(c.status, 'OPEN') AS status, c.owner, c.resolution, c.recovered_usd, c.updated_at
        FROM serving.case_workbench q LEFT JOIN recon.dispute_cases c USING (case_id)
        WHERE q.billing_month = %s ORDER BY q.revenue_at_risk_usd DESC NULLS LAST""", (month,))


def usd(x):
    return "—" if x is None or pd.isna(x) else f"${x:,.0f}"


# ---------------- pages ----------------

def overview():
    st.title("Close overview")
    pm = uc(f"SELECT * FROM {CATALOG}.gold.recon_partner_month WHERE billing_month >= '2026-07'")
    month = st.segmented_control("Billing month", sorted(pm.billing_month.unique()), default=pm.billing_month.max())
    cur = pm[pm.billing_month == month]
    cases = pg_df("""SELECT coalesce(c.status,'OPEN') AS status, count(*) AS n, sum(q.revenue_at_risk_usd) AS usd,
                            sum(coalesce(c.recovered_usd,0)) AS recovered
                     FROM serving.case_workbench q LEFT JOIN recon.dispute_cases c USING (case_id)
                     WHERE q.billing_month = %s GROUP BY 1""", (month,))
    k = st.columns(5)
    k[0].metric("Gross CTV revenue (Apex)", usd(cur.ssp_revenue_usd.sum()))
    k[1].metric("Billed per DSP reports", usd(cur.dsp_revenue_usd.sum()))
    k[2].metric("Revenue at risk", usd(cur.revenue_at_risk_usd.sum()))
    k[3].metric("Cases open", int(cases[cases.status != "RESOLVED"].n.sum()))
    k[4].metric("Recovered so far", usd(cases.recovered.sum()))

    left, right = st.columns([3, 2])
    with left:
        st.subheader("Revenue at risk by DSP")
        top = cur.sort_values("revenue_at_risk_usd", ascending=False).head(15)
        st.altair_chart(alt.Chart(top).mark_bar().encode(
            x=alt.X("revenue_at_risk_usd:Q", title="Revenue at risk (USD)"),
            y=alt.Y("dsp_name:N", sort="-x", title=None),
            color=alt.condition(alt.datum.over_threshold, alt.value("#d1495b"), alt.value("#8d99ae")),
            tooltip=["dsp_name", "partner_team", "deals_needing_review", "revenue_gap_pct", "revenue_at_risk_usd"]),
            width="stretch")
        st.caption("Red = monthly gap over the partner's contract threshold.")
    with right:
        st.subheader("Why revenue is at risk (model root cause)")
        by_cause = pg_df("""SELECT predicted_root_cause, count(*) AS cases, sum(revenue_at_risk_usd) AS usd
                            FROM serving.case_workbench WHERE billing_month = %s GROUP BY 1 ORDER BY 3 DESC""", (month,))
        st.altair_chart(alt.Chart(by_cause).mark_arc(innerRadius=60).encode(
            theta="usd:Q", color=alt.Color("predicted_root_cause:N", title="Root cause"),
            tooltip=["predicted_root_cause", "cases", "usd"]), width="stretch")
    st.subheader("Trend")
    trend = uc(f"""SELECT billing_month, round(sum(revenue_at_risk_usd)) AS revenue_at_risk_usd,
                          round(100 * (sum(ssp_revenue_usd) - sum(dsp_revenue_usd)) / sum(ssp_revenue_usd), 2) AS net_gap_pct
                   FROM {CATALOG}.gold.recon_partner_month GROUP BY 1 ORDER BY 1""")
    st.altair_chart(alt.Chart(trend).mark_line(point=True).encode(x="billing_month:N", y="revenue_at_risk_usd:Q"),
                    width="stretch")


def triage():
    st.title("Triage queue")
    months = pg_df("SELECT DISTINCT billing_month FROM serving.case_workbench ORDER BY 1").billing_month.tolist()
    c1, c2, c3 = st.columns(3)
    month = c1.selectbox("Billing month", months, index=len(months) - 1)
    q = queue(month)
    status = c2.multiselect("Status", ["OPEN", "IN_REVIEW", "SENT_TO_PARTNER", "RESOLVED"],
                            default=["OPEN", "IN_REVIEW", "SENT_TO_PARTNER"])
    cause = c3.multiselect("Model root cause", sorted(q.predicted_root_cause.unique()))
    q = q[q.status.isin(status)]
    if cause:
        q = q[q.predicted_root_cause.isin(cause)]
    st.caption(f"{len(q)} cases · {usd(q.revenue_at_risk_usd.sum())} at risk · sorted by revenue at risk")
    view = q[["case_id", "dsp_name", "deal_name", "revenue_at_risk_usd", "revenue_gap_pct", "predicted_root_cause",
              "confidence", "status", "owner"]]
    sel = st.dataframe(view, hide_index=True, width="stretch", on_select="rerun", selection_mode="single-row",
                       column_config={"revenue_at_risk_usd": st.column_config.NumberColumn("At risk", format="$%,.0f"),
                                      "revenue_gap_pct": st.column_config.NumberColumn("Gap %", format="%.1f%%"),
                                      "confidence": st.column_config.ProgressColumn("Confidence", min_value=0, max_value=1)})
    if sel.selection.rows:
        st.session_state.case_id = view.iloc[sel.selection.rows[0]].case_id
        st.session_state.page = "Case detail"
        st.rerun()


def case_detail():
    case_id = st.session_state.get("case_id")
    if not case_id:
        st.info("Pick a case in the Triage queue.")
        return
    row = pg_df("""SELECT q.*, coalesce(c.status,'OPEN') AS status, c.owner, c.resolution, c.recovered_usd,
                          c.confirmed_root_cause, c.dispute_email_sent
                   FROM serving.case_workbench q LEFT JOIN recon.dispute_cases c USING (case_id) WHERE case_id = %s""",
                (case_id,)).iloc[0]
    ensure_case(row)
    st.title(f"{row.dsp_name} · {row.deal_name}")
    st.caption(f"{case_id} · {row.billing_month} · status **{row.status}** · owner {row.owner or USER}")
    k = st.columns(5)
    k[0].metric("Apex impressions", f"{row.ssp_impressions:,.0f}")
    k[1].metric("DSP impressions", f"{row.dsp_impressions:,.0f}", f"{-row.impression_gap_pct:.1f}%")
    k[2].metric("Revenue gap", usd(row.revenue_gap_usd), f"{-row.revenue_gap_pct:.1f}%")
    k[3].metric("Contract threshold", f"{row.discrepancy_threshold_pct:.1f}%")
    k[4].metric("Model root cause", row.predicted_root_cause.replace("_", " ").title(), f"{row.confidence:.0%} confidence",
                delta_color="off")

    daily = uc(f"""SELECT s.report_date, s.ssp_impressions, d.dsp_impressions
                   FROM {CATALOG}.silver.ssp_daily s
                   LEFT JOIN {CATALOG}.silver.dsp_daily d USING (deal_id, report_date)
                   WHERE s.deal_id = '{row.deal_id}' AND date_format(s.report_date, 'yyyy-MM') = '{row.billing_month}'
                   ORDER BY s.report_date""")
    long = daily.melt("report_date", ["ssp_impressions", "dsp_impressions"], "source", "impressions")
    st.altair_chart(alt.Chart(long).mark_line(point=True).encode(
        x=alt.X("report_date:T", title=None), y="impressions:Q",
        color=alt.Color("source:N", scale=alt.Scale(range=["#2b6cb0", "#d1495b"]))).properties(height=260),
        width="stretch")
    ev = st.columns(4)
    ev[0].metric("Days missing in DSP report", int(row.days_missing_in_dsp_report))
    ev[1].metric("Days with a big gap", f"{row.large_gap_day_share:.0%}")
    ev[2].metric("Day-to-day swing", f"{row.daily_gap_swing:+.2f}", "negative = gaps flip-flop (timezone)", delta_color="off")
    ev[3].metric("Publisher IVT risk", f"{row.ivt_risk_score:.2f}")

    st.subheader("AI case summary")
    st.info(row.case_summary or "No draft for this case.")
    st.markdown(f"**Recommended action:** {row.recommended_action}")

    st.subheader("Dispute email")
    subject = st.text_input("Subject", row.email_subject or f"Billing discrepancy {row.billing_month} · {row.deal_id}")
    body = st.text_area("Body", row.dispute_email_sent or row.email_body or "", height=260)
    a, b = st.columns(2)
    with a:
        if st.button("Send to partner", type="primary", disabled=row.status in ("SENT_TO_PARTNER", "RESOLVED")):
            pg_exec([("""UPDATE recon.dispute_cases SET status='SENT_TO_PARTNER', dispute_email_sent=%s, updated_at=now()
                         WHERE case_id=%s""", (body, case_id)),
                     log_event(case_id, "EMAIL_SENT", {"subject": subject, "edited": body != (row.email_body or "")})])
            st.toast("Dispute recorded as sent")
            st.rerun()
    with b:
        with st.popover("Resolve case", disabled=row.status == "RESOLVED"):
            resolution = st.selectbox("Resolution", RESOLUTIONS)
            confirmed = st.selectbox("Confirmed root cause", CAUSES, index=CAUSES.index(row.predicted_root_cause))
            amount = st.number_input("Recovered / credited (USD)", min_value=0.0,
                                     value=float(max(row.revenue_at_risk_usd or 0, 0)), step=100.0)
            if st.button("Confirm resolution"):
                stmts = [("""UPDATE recon.dispute_cases SET status='RESOLVED', resolution=%s, confirmed_root_cause=%s,
                             recovered_usd=%s, updated_at=now() WHERE case_id=%s""",
                          (resolution, confirmed, amount if resolution == "RECOVERED" else 0, case_id)),
                         log_event(case_id, "STATUS_CHANGED", {"status": "RESOLVED", "resolution": resolution,
                                                               "confirmed_root_cause": confirmed,
                                                               "model_root_cause": row.predicted_root_cause})]
                if resolution == "CREDIT_ISSUED":
                    stmts.append(("""INSERT INTO recon.credit_approvals (case_id, amount_usd, approved_by, reason)
                                     VALUES (%s, %s, %s, %s)""", (case_id, amount, USER, confirmed)))
                pg_exec(stmts)
                st.toast("Case resolved")
                st.rerun()
    note = st.chat_input("Add a note to the case")
    if note:
        pg_exec([log_event(case_id, "NOTE", {"note": note})])
    st.subheader("Audit trail")
    st.dataframe(pg_df("SELECT created_at, event_type, actor, detail FROM recon.case_events WHERE case_id=%s ORDER BY created_at DESC",
                       (case_id,)), hide_index=True, width="stretch")


def ask_genie():
    st.title("Ask Genie")
    st.caption("Ask about reconciliation in plain English: partners, deals, gaps, root causes and dispute status.")
    if not GENIE_SPACE_ID:
        st.warning("GENIE_SPACE_ID is not configured.")
        return
    hist = st.session_state.setdefault("genie", [])
    for m in hist:
        with st.chat_message(m["role"]):
            st.markdown(m["text"])
            if m.get("df") is not None:
                st.dataframe(m["df"], hide_index=True)
    prompt = st.chat_input("e.g. Which DSPs were over threshold in all three months this quarter?")
    if not prompt:
        return
    hist.append({"role": "user", "text": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"), st.spinner("Genie is thinking…"):
        conv = st.session_state.get("genie_conv")
        msg = (w.genie.create_message_and_wait(GENIE_SPACE_ID, conv, prompt) if conv
               else w.genie.start_conversation_and_wait(GENIE_SPACE_ID, prompt))
        st.session_state.genie_conv = msg.conversation_id
        text, df = [], None
        for att in msg.attachments or []:
            if att.text:
                text.append(att.text.content)
            if att.query:
                text.append(f"_{att.query.description or ''}_")
                res = w.genie.get_message_attachment_query_result(GENIE_SPACE_ID, msg.conversation_id, msg.id,
                                                                  att.attachment_id)
                sr = res.statement_response
                cols = [c.name for c in sr.manifest.schema.columns]
                df = pd.DataFrame(sr.result.data_array or [], columns=cols)
        answer = "\n\n".join(t for t in text if t) or "No answer returned."
        st.markdown(answer)
        if df is not None:
            st.dataframe(df, hide_index=True)
        hist.append({"role": "assistant", "text": answer, "df": df})


PAGES = {"Close overview": overview, "Triage queue": triage, "Case detail": case_detail, "Ask Genie": ask_genie}
with st.sidebar:
    st.markdown("### Apex Exchange\n**CTV Reconciliation Workbench**")
    page = st.radio("Go to", list(PAGES), key="page", label_visibility="collapsed")
    st.caption(f"Signed in as {USER}")
PAGES[page]()
