# Databricks notebook source
# MAGIC %md
# MAGIC # 04 · Score discrepancies and draft disputes
# MAGIC
# MAGIC 1. Score every deal-month with the `@champion` root-cause model → `ml.discrepancy_predictions`
# MAGIC 2. Build the Billing Ops work queue for the open closes (Jul–Sep) → `gold.dispute_queue`
# MAGIC 3. Draft a case summary and a partner-ready dispute email for each case with `ai_query` → `gold.dispute_drafts`
# MAGIC 4. Check the drafts: every dollar figure must come from the evidence, plus an LLM judge on accuracy and tone

# COMMAND ----------

import json
import re

import mlflow
import pandas as pd
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "apex_recon")
dbutils.widgets.text("draft_model", "databricks-claude-sonnet-4-6")
dbutils.widgets.text("judge_model", "databricks-gpt-5-4-mini")
dbutils.widgets.text("max_drafts", "250")
CATALOG = dbutils.widgets.get("catalog")
DRAFT_MODEL, JUDGE_MODEL = dbutils.widgets.get("draft_model"), dbutils.widgets.get("judge_model")
MAX_DRAFTS = int(dbutils.widgets.get("max_drafts"))
MODEL_NAME = f"{CATALOG}.ml.discrepancy_root_cause"
mlflow.set_registry_uri("databricks-uc")

ACTIONS = {
    "WITHIN_TOLERANCE": "No action: gap is within contract tolerance.",
    "TIMEZONE_SHIFT": "No billing adjustment expected; ask the partner to restate daily reporting in UTC as the contract requires.",
    "IVT_FILTERING": "Request the partner's third-party IVT report; credit only verified invalid traffic per contract.",
    "SSAI_BEACON_LOSS": "Share Apex SSAI beacon logs, open a ticket with the SSAI vendor and propose a split of the gap.",
    "DEAL_ID_MISMAPPING": "Ask the partner to re-attribute impressions to the correct deal ID; partner total should net out.",
    "FX_MISMATCH": "Request restatement at the contract FX reference rate for each delivery day.",
    "LATE_OR_MISSING_DATA": "Request the missing days' report rows; hold invoice adjustment until data is complete.",
    "GENUINE_BILLING_ERROR": "Dispute: invoice on the Apex count with log-level evidence attached.",
}

# COMMAND ----------

# MAGIC %md ## 1 · Score with the champion model

# COMMAND ----------

client = mlflow.MlflowClient()
version = client.get_model_version_by_alias(MODEL_NAME, "champion").version
model = mlflow.sklearn.load_model(f"models:/{MODEL_NAME}@champion")
features = list(model.feature_names_in_)

feats = spark.table(f"{CATALOG}.ml.discrepancy_features").toPandas()
X = feats[features].copy()
for c in ["is_live", "is_non_usd"]:
    X[c] = X[c].astype(float)
proba = model.predict_proba(X)
classes = model.classes_
order = proba.argsort(axis=1)
preds = pd.DataFrame({
    "deal_id": feats.deal_id, "billing_month": feats.billing_month,
    "predicted_root_cause": classes[order[:, -1]],
    "confidence": proba[range(len(X)), order[:, -1]].round(4),
    "runner_up_cause": classes[order[:, -2]],
    "runner_up_confidence": proba[range(len(X)), order[:, -2]].round(4),
    "model_version": int(version),
})
preds["recommended_action"] = preds.predicted_root_cause.map(ACTIONS)
(spark.createDataFrame(preds).withColumn("scored_at", F.current_timestamp())
 .write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOG}.ml.discrepancy_predictions"))
spark.sql(f"COMMENT ON TABLE {CATALOG}.ml.discrepancy_predictions IS "
          "'Predicted root cause per deal-month from the @champion model, with confidence, runner-up and recommended action.'")
print(f"scored {len(preds):,} deal-months with {MODEL_NAME} v{version}")
print(preds.predicted_root_cause.value_counts().to_string())

# COMMAND ----------

# MAGIC %md ## 2 · Billing Ops work queue (open closes Jul–Sep)

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE TABLE {CATALOG}.gold.dispute_queue
COMMENT 'Open reconciliation cases for the Jul-Sep closes: deal-months needing review, ranked by revenue at risk, with the model root cause, evidence and recommended action.'
AS
SELECT
  concat('CASE-', d.billing_month, '-', d.deal_id) AS case_id,
  d.billing_month, d.dsp_id, d.dsp_name, d.partner_team, d.deal_id, d.deal_name, d.publisher_id, d.publisher_name,
  d.content_genre, d.is_live, d.ssai_vendor, d.reporting_currency, d.billing_count_basis, d.discrepancy_threshold_pct,
  d.ssp_impressions, d.dsp_impressions, d.impression_gap_pct,
  d.ssp_revenue_usd, d.dsp_revenue_usd, d.revenue_gap_usd, d.revenue_gap_pct, d.revenue_at_risk_usd,
  d.days_delivered, d.days_missing_in_dsp_report, d.days_with_large_gap,
  f.tz_shift_gain, f.best_shift_hours, f.sibling_offset_match, f.rev_minus_imp_gap_pct, f.ivt_risk_score,
  p.predicted_root_cause, p.confidence, p.runner_up_cause, p.runner_up_confidence, p.recommended_action, p.model_version
FROM {CATALOG}.gold.recon_deal_month d
JOIN {CATALOG}.ml.discrepancy_features f USING (deal_id, billing_month)
JOIN {CATALOG}.ml.discrepancy_predictions p USING (deal_id, billing_month)
WHERE d.billing_month >= '2026-07' AND d.needs_review
""")
q = spark.table(f"{CATALOG}.gold.dispute_queue")
display(q.groupBy("billing_month", "predicted_root_cause").agg(F.count("*").alias("cases"),
        F.round(F.sum("revenue_at_risk_usd"), 0).alias("revenue_at_risk_usd")).orderBy("billing_month", "predicted_root_cause"))

# COMMAND ----------

# MAGIC %md ## 3 · Draft case summaries and dispute emails with `ai_query`

# COMMAND ----------

PROMPT = """You are a senior billing operations analyst at Apex Exchange, a CTV sell-side platform.
Draft a case summary for an internal analyst and a dispute email to the DSP partner, using ONLY the evidence below.
Rules: quote dollar amounts and percentages exactly as given; do not invent numbers, dates or names; be firm, factual
and courteous; if the root cause implies no billing adjustment, say so and request the reporting fix instead.
Return JSON only, with keys: case_summary (<=80 words), email_subject, email_body (<=180 words, signed 'Apex Exchange Billing Operations'),
proposed_adjustment_usd (number; 0 if no adjustment is requested).

EVIDENCE:
"""

drafts = spark.sql(f"""
WITH ranked AS (
  SELECT *, row_number() OVER (ORDER BY revenue_at_risk_usd DESC) AS rk
  FROM {CATALOG}.gold.dispute_queue WHERE predicted_root_cause <> 'WITHIN_TOLERANCE'
),
ev AS (
  SELECT case_id, rk, to_json(named_struct(
    'case_id', case_id, 'billing_month', billing_month, 'partner', dsp_name, 'deal_id', deal_id, 'deal_name', deal_name,
    'apex_impressions', ssp_impressions, 'partner_impressions', dsp_impressions,
    'apex_revenue_usd', round(ssp_revenue_usd, 2), 'partner_revenue_usd', round(dsp_revenue_usd, 2),
    'revenue_gap_usd', round(revenue_gap_usd, 2), 'revenue_gap_pct', round(revenue_gap_pct, 2),
    'contract_threshold_pct', discrepancy_threshold_pct, 'billing_count_basis', billing_count_basis,
    'days_missing_in_partner_report', days_missing_in_dsp_report, 'best_fit_timezone_shift_hours', best_shift_hours,
    'predicted_root_cause', predicted_root_cause, 'model_confidence', round(confidence, 2),
    'recommended_action', recommended_action)) AS evidence
  FROM ranked WHERE rk <= {MAX_DRAFTS}
)
SELECT case_id, evidence,
  ai_query('{DRAFT_MODEL}', concat({json.dumps(PROMPT)}, evidence),
           modelParameters => named_struct('temperature', 0.0, 'max_tokens', 900)) AS raw_response
FROM ev
""")
schema = "case_summary STRING, email_subject STRING, email_body STRING, proposed_adjustment_usd DOUBLE"
drafts = (drafts.withColumn("clean", F.regexp_replace("raw_response", r"(?s)^[^{]*|[^}]*$", ""))
          .withColumn("j", F.from_json("clean", schema))
          .select("case_id", "evidence", "j.*", F.lit(DRAFT_MODEL).alias("draft_model"),
                  F.current_timestamp().alias("drafted_at")))
drafts.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOG}.gold.dispute_drafts")
spark.sql(f"COMMENT ON TABLE {CATALOG}.gold.dispute_drafts IS 'GenAI-drafted case summary and partner dispute email per open case, grounded in the case evidence JSON.'")
d = spark.table(f"{CATALOG}.gold.dispute_drafts").toPandas()
print(f"drafted {len(d)} cases; parse failures: {int(d.email_body.isna().sum())}")

# Serving copy for the app: queue + drafts in one row per case, synced to Lakebase (see 05_lakebase_sync).
spark.sql(f"""
CREATE OR REPLACE TABLE {CATALOG}.gold.case_workbench
COMMENT 'Serving table for the Reconciliation Workbench: one row per open case with evidence, model root cause and GenAI draft. Synced to Lakebase; read by the app service principal only.'
TBLPROPERTIES (delta.enableChangeDataFeed = true)
AS SELECT q.*, d.case_summary, d.email_subject, d.email_body, d.proposed_adjustment_usd
FROM {CATALOG}.gold.dispute_queue q LEFT JOIN {CATALOG}.gold.dispute_drafts d USING (case_id)
""")

# COMMAND ----------

# MAGIC %md ## 4 · Check the drafts

# COMMAND ----------


def money(text):
    return {round(float(x.replace(",", "")), 0) for x in re.findall(r"\$\s?([\d,]+(?:\.\d+)?)", text or "")}


def grounded(row):
    ev = json.loads(row.evidence)
    allowed = {round(abs(float(v)), 0) for v in ev.values() if isinstance(v, (int, float))}
    allowed.add(round(abs(row.proposed_adjustment_usd or 0), 0))
    found = money(f"{row.case_summary} {row.email_body}")
    return all(any(abs(f - a) <= 1 for a in allowed) for f in found)


d["dollars_grounded"] = d.apply(grounded, axis=1)
judge = spark.createDataFrame(d[["case_id", "evidence", "email_body"]].head(30)).selectExpr(
    "case_id",
    f"""ai_query('{JUDGE_MODEL}', concat(
      'Rate this dispute email against its evidence. Return JSON only: {{"accuracy":1-5,"tone":1-5,"actionable":1-5,"issue":"<short>"}}.',
      ' accuracy = every fact matches the evidence; tone = professional and courteous; actionable = clear ask of the partner.',
      ' EVIDENCE: ', evidence, ' EMAIL: ', email_body),
      modelParameters => named_struct('temperature', 0.0)) AS verdict""").toPandas()
judge = pd.concat([judge.case_id, judge.verdict.str.extract(r"(\{.*\})", expand=False).apply(json.loads).apply(pd.Series)], axis=1)
eval_summary = {
    "drafts": len(d),
    "parse_failures": int(d.email_body.isna().sum()),
    "dollars_grounded_rate": round(float(d.dollars_grounded.mean()), 4),
    "judge_sample": len(judge),
    "judge_mean": judge[["accuracy", "tone", "actionable"]].astype(float).mean().round(2).to_dict(),
    "draft_model": DRAFT_MODEL, "judge_model": JUDGE_MODEL,
}
print(json.dumps(eval_summary, indent=2))
sample = d.sort_values("case_id").head(3)[["case_id", "case_summary", "email_subject", "email_body", "proposed_adjustment_usd"]]
for r in sample.itertuples():
    print(f"\n===== {r.case_id} =====\nSUMMARY: {r.case_summary}\nSUBJECT: {r.email_subject}\n{r.email_body}\nPROPOSED ADJUSTMENT: ${r.proposed_adjustment_usd:,.2f}")

# COMMAND ----------

dbutils.notebook.exit(json.dumps({
    "model_version": int(version), "deal_months_scored": len(preds),
    "prediction_distribution": preds.predicted_root_cause.value_counts().to_dict(),
    "queue": q.groupBy("billing_month").agg(F.count("*").alias("cases"), F.round(F.sum("revenue_at_risk_usd"), 0).alias("usd"))
              .toPandas().set_index("billing_month").to_dict("index"),
    "genai_eval": eval_summary,
    "judge_issues": judge[["case_id", "accuracy", "tone", "actionable", "issue"]].head(10).to_dict("records"),
    "sample_drafts": sample.to_dict("records"),
}, default=str))
