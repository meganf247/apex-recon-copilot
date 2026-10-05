# Databricks notebook source
# MAGIC %md
# MAGIC # 07 · Lakebase → Unity Catalog: case status back to the lakehouse
# MAGIC
# MAGIC Analysts work cases in the app, which writes to Lakebase (`apex_ops.recon.*`). This task snapshots those
# MAGIC operational tables into Unity Catalog so Genie, dashboards and Finance reporting see live dispute status and
# MAGIC recovered dollars alongside the reconciliation gold tables.

# COMMAND ----------

# MAGIC %pip install -q "psycopg[binary]>=3.2"

# COMMAND ----------

import json

import pandas as pd
import psycopg
from databricks.sdk import WorkspaceClient

dbutils.widgets.text("catalog", "apex_recon")
dbutils.widgets.text("endpoint", "projects/apex-recon/branches/production/endpoints/primary")
dbutils.widgets.text("host", "ep-crimson-term-d2b11cr0.database.us-east-1.cloud.databricks.com")
CATALOG, ENDPOINT, HOST = (dbutils.widgets.get(k) for k in ["catalog", "endpoint", "host"])

w = WorkspaceClient()
user = spark.sql("SELECT current_user()").first()[0]
token = w.postgres.generate_database_credential(endpoint=ENDPOINT).token

TABLES = {
    "dispute_cases": "SELECT * FROM recon.dispute_cases",
    "case_events": "SELECT event_id, case_id, event_type, actor, detail::text AS detail, created_at FROM recon.case_events",
    "credit_approvals": "SELECT * FROM recon.credit_approvals",
}
counts = {}
with psycopg.connect(host=HOST, dbname="apex_ops", user=user, password=token, sslmode="require") as conn:
    for name, query in TABLES.items():
        with conn.cursor() as cur:
            cur.execute(query)
            df = pd.DataFrame(cur.fetchall(), columns=[d.name for d in cur.description])
        counts[name] = len(df)
        if df.empty:
            continue  # keep the previous snapshot; Spark can't infer a schema from zero rows
        for c in df.columns:
            if "datetime" in str(df[c].dtype):
                df[c] = pd.to_datetime(df[c], utc=True).dt.tz_localize(None)
            elif df[c].map(lambda v: type(v).__name__).eq("Decimal").any():
                df[c] = df[c].astype(float)
        (spark.createDataFrame(df).write.mode("overwrite").option("overwriteSchema", "true")
         .saveAsTable(f"{CATALOG}.ops.lakebase_{name}"))
print(counts)

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE VIEW {CATALOG}.ops.dispute_case_status
COMMENT 'Current dispute workflow status per case from the Reconciliation Workbench (Lakebase), joined to the open-case queue. Cases with no workbench activity are OPEN.'
AS SELECT q.case_id, q.billing_month, q.dsp_id, q.dsp_name, q.partner_team, q.deal_id,
          coalesce(c.status, 'OPEN') AS status, c.resolution, c.owner, c.confirmed_root_cause, q.predicted_root_cause,
          q.revenue_at_risk_usd, coalesce(c.recovered_usd, 0) AS recovered_usd,
          coalesce(a.credited_usd, 0) AS credited_usd, c.updated_at AS last_activity_at
   FROM {CATALOG}.gold.case_workbench q
   LEFT JOIN {CATALOG}.ops.lakebase_dispute_cases c USING (case_id)
   LEFT JOIN (SELECT case_id, sum(amount_usd) AS credited_usd FROM {CATALOG}.ops.lakebase_credit_approvals GROUP BY case_id) a USING (case_id)
""")
summary = spark.sql(f"""SELECT status, count(*) AS cases, round(sum(revenue_at_risk_usd)) AS revenue_at_risk_usd,
                               round(sum(recovered_usd)) AS recovered_usd, round(sum(credited_usd)) AS credited_usd
                        FROM {CATALOG}.ops.dispute_case_status GROUP BY status ORDER BY status""").toPandas()
print(summary.to_string(index=False))
dbutils.notebook.exit(json.dumps({"rows_snapshotted": counts, "status_summary": summary.to_dict("records")}, default=str))
