# Executed notebook: `03_ml_and_disputes`

- Task run ID: `153382223878704` (job run `542978415804640`)
- Result: **SUCCESS**
- Run page: https://fevm-megant-fevm.cloud.databricks.com/?o=7474649371849429#job/800507315624085/run/153382223878704
- Every cell below is shown with the output it produced in that run.

# 03 · Root-cause model and dispute drafts

> **Execution evidence:** this is the source the job runs. The same notebook with every cell's output from the
> latest job run is in [`evidence/notebook_runs/03_ml_and_disputes.md`](../evidence/notebook_runs/03_ml_and_disputes.md) (and `.ipynb`).

1. **Features:** how each deal's daily gap behaves across the month → `ml.root_cause_features`
2. **Model:** learn the root cause from the Jan–Jun disputes Billing Ops resolved, compare with the analysts'
   rules of thumb, register `@champion` → `ml.discrepancy_predictions`
3. **Work queue:** Jul–Sep deal-months that need review → `gold.dispute_queue`
4. **GenAI:** draft a case summary and partner dispute email with `ai_query`, then check every draft → `gold.dispute_drafts`
5. **Serve:** queue + drafts → `gold.case_workbench`, refreshed into Lakebase for the app

```python
import json
import re

import mlflow
import pandas as pd
from databricks.sdk import WorkspaceClient
from mlflow.models import infer_signature
from pyspark.sql import Window
from pyspark.sql import functions as F
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

dbutils.widgets.text("catalog", "apex_recon")
dbutils.widgets.text("draft_model", "databricks-claude-sonnet-4-6")
dbutils.widgets.text("judge_model", "databricks-gpt-5-4-mini")
CATALOG = dbutils.widgets.get("catalog")
DRAFT_MODEL, JUDGE_MODEL = dbutils.widgets.get("draft_model"), dbutils.widgets.get("judge_model")
MODEL_NAME = f"{CATALOG}.ml.discrepancy_root_cause"
mlflow.set_registry_uri("databricks-uc")
mlflow.set_experiment(f"/Users/{spark.sql('SELECT current_user()').first()[0]}/apex-recon-root-cause")
```

## 1 · Features
The shape of the daily gap tells the causes apart: timezone shifts swing up and down day to day but net out;
IVT is a steady haircut that's worse on risky publishers; missing data leaves whole days blank; billing errors
hit some days hard and others not at all.

```python
daily = (spark.table(f"{CATALOG}.silver.ssp_daily")
         .join(spark.table(f"{CATALOG}.silver.dsp_daily").select("deal_id", "report_date", "dsp_impressions"),
               ["deal_id", "report_date"])
         .withColumn("billing_month", F.date_format("report_date", "yyyy-MM"))
         .withColumn("gap", 100 * (F.col("ssp_impressions") - F.col("dsp_impressions")) / F.col("ssp_impressions"))
         .withColumn("prev_gap", F.lag("gap").over(Window.partitionBy("deal_id", "billing_month").orderBy("report_date"))))
shape = daily.groupBy("deal_id", "billing_month").agg(
    F.stddev("gap").alias("daily_gap_std"), F.expr("percentile_approx(gap, 0.5)").alias("daily_gap_median"),
    F.min("gap").alias("daily_gap_min"), F.max("gap").alias("daily_gap_max"),
    F.corr("gap", "prev_gap").alias("daily_gap_lag1_autocorr"),
    F.avg((F.col("gap") < -2).cast("double")).alias("share_days_dsp_over"))
(spark.table(f"{CATALOG}.gold.recon_deal_month")
 .select("deal_id", "billing_month", "dsp_id", "impression_gap_pct", "revenue_gap_pct", "large_gap_day_share",
         (F.col("days_missing_in_dsp_report") / F.col("days_delivered")).alias("missing_day_share"),
         "ivt_risk_score", "discrepancy_threshold_pct", F.col("is_live").cast("double").alias("is_live"),
         "content_genre", "deal_type")
 .join(shape, ["deal_id", "billing_month"], "left").fillna(0.0)
 .write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOG}.ml.root_cause_features"))

NUMERIC = ["impression_gap_pct", "revenue_gap_pct", "large_gap_day_share", "missing_day_share", "daily_gap_std",
           "daily_gap_median", "daily_gap_min", "daily_gap_max", "daily_gap_lag1_autocorr", "share_days_dsp_over",
           "ivt_risk_score", "discrepancy_threshold_pct", "is_live"]
CATEGORICAL = ["content_genre", "deal_type"]
FEATURES = NUMERIC + CATEGORICAL
feats = spark.table(f"{CATALOG}.ml.root_cause_features").toPandas()
labels = spark.table(f"{CATALOG}.ml.dispute_history").select("deal_id", "billing_month", "resolved_root_cause").toPandas()
truth = spark.table(f"{CATALOG}.ml.ground_truth_root_causes").select("deal_id", "billing_month", "root_cause").toPandas()
KEYS = ["deal_id", "billing_month"]  # sorted so the train/test split (and the scores) are the same on every run
train_df = feats.merge(labels, on=KEYS).sort_values(KEYS, ignore_index=True)
current = feats[feats.billing_month >= "2026-07"].merge(truth, on=KEYS).sort_values(KEYS, ignore_index=True)
print(f"{len(feats):,} deal-months · {len(train_df):,} labelled history cases · {len(current):,} Jul–Sep deal-months")
```

Output:

```text
5,562 deal-months · 1,615 labelled history cases · 2,025 Jul–Sep deal-months
```

## 2 · Model vs. the analysts' rules of thumb

```python
def playbook(r):
    if abs(r.revenue_gap_pct) <= r.discrepancy_threshold_pct and r.large_gap_day_share < 0.3:
        return "WITHIN_TOLERANCE"
    if r.missing_day_share > 0:
        return "LATE_OR_MISSING_DATA"
    if abs(r.revenue_gap_pct) <= r.discrepancy_threshold_pct:
        return "TIMEZONE_SHIFT"
    return "IVT_FILTERING"  # the explanation most DSPs give


def scores(y_true, y_pred):
    return {"accuracy": round(accuracy_score(y_true, y_pred), 4), "macro_f1": round(f1_score(y_true, y_pred, average="macro"), 4)}


X_tr, X_te, y_tr, y_te = train_test_split(train_df[FEATURES], train_df.resolved_root_cause, test_size=0.25,
                                          stratify=train_df.resolved_root_cause, random_state=7)
model = Pipeline([
    ("prep", ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL)],
                               remainder="passthrough")),
    ("gbm", HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08, class_weight="balanced", random_state=7)),
])
with mlflow.start_run(run_name="hgb_root_cause") as run:
    model.fit(X_tr, y_tr)
    results = {"holdout_vs_analyst_labels": {"model": scores(y_te, model.predict(X_te)),
                                             "playbook": scores(y_te, X_te.apply(playbook, axis=1))},
               "jul_sep_vs_true_cause": {"model": scores(current.root_cause, model.predict(current[FEATURES])),
                                         "playbook": scores(current.root_cause, current[FEATURES].apply(playbook, axis=1))}}
    # The cases analysts actually work: Jul-Sep deal-months that need review. Most deal-months are within tolerance and
    # easy to call, so this is the honest comparison with the rules of thumb.
    review = spark.table(f"{CATALOG}.gold.recon_deal_month").filter("needs_review AND billing_month >= '2026-07'") \
        .select("deal_id", "billing_month").toPandas()
    in_queue = current.merge(review, on=["deal_id", "billing_month"])
    results["jul_sep_review_queue_vs_true_cause"] = {
        "cases": len(in_queue), "model": scores(in_queue.root_cause, model.predict(in_queue[FEATURES])),
        "playbook": scores(in_queue.root_cause, in_queue[FEATURES].apply(playbook, axis=1))}
    report = classification_report(current.root_cause, model.predict(current[FEATURES]), digits=3, zero_division=0)
    queue_report = classification_report(in_queue.root_cause, model.predict(in_queue[FEATURES]), digits=3, zero_division=0)
    for test, r in results.items():
        mlflow.log_metrics({f"{test}_{who}_{m}": v for who, s in r.items() if who != "cases" for m, v in s.items()})
    mlflow.log_text(report, "jul_sep_classification_report.txt")
    mlflow.log_text(queue_report, "jul_sep_review_queue_classification_report.txt")
    mlflow.sklearn.log_model(model, "model", signature=infer_signature(X_tr, model.predict(X_tr)),
                             input_example=X_tr.head(3), registered_model_name=MODEL_NAME)
client = mlflow.MlflowClient()
version = max(int(v.version) for v in client.search_model_versions(f"name='{MODEL_NAME}'"))
client.set_registered_model_alias(MODEL_NAME, "champion", version)
print(json.dumps(results, indent=2))
print("All Jul-Sep deal-months:\n" + report)
print("Review queue only:\n" + queue_report)
```

Output:

```text
2026/11/02 15:53:26 WARNING mlflow.models.model: `artifact_path` is deprecated. Please use `name` instead.
🔗 View Logged Model at: https://fevm-megant-fevm.cloud.databricks.com/ml/experiments/272241904346403/models/m-8425e6dd1dbb4bc3a508781964eb98e7?o=7474649371849429
Registered model 'apex_recon.ml.discrepancy_root_cause' already exists. Creating a new version of this model...
🔗 Created version '10' of model 'apex_recon.ml.discrepancy_root_cause': https://fevm-megant-fevm.cloud.databricks.com/explore/data/models/apex_recon/ml/discrepancy_root_cause/version/10?o=7474649371849429
{
  "holdout_vs_analyst_labels": {
    "model": {
      "accuracy": 0.854,
      "macro_f1": 0.8497
    },
    "playbook": {
      "accuracy": 0.6361,
      "macro_f1": 0.5442
    }
  },
  "jul_sep_vs_true_cause": {
    "model": {
      "accuracy": 0.9452,
      "macro_f1": 0.9109
    },
    "playbook": {
      "accuracy": 0.8212,
      "macro_f1": 0.5797
    }
  },
  "jul_sep_review_queue_vs_true_cause": {
    "cases": 715,
    "model": {
      "accuracy": 0.9245,
      "macro_f1": 0.9073
    },
    "playbook": {
      "accuracy": 0.5524,
      "macro_f1": 0.4119
    }
  }
}
All Jul-Sep deal-months:
                       precision    recall  f1-score   support

GENUINE_BILLING_ERROR      0.909     0.959     0.933       146
        IVT_FILTERING      0.917     0.957     0.936       276
 LATE_OR_MISSING_DATA      0.832     0.944     0.884       142
       TIMEZONE_SHIFT      0.756     0.934     0.835       106
     WITHIN_TOLERANCE      0.989     0.942     0.965      1355

             accuracy                          0.945      2025
            macro avg      0.881     0.947     0.911      2025
         weighted avg      0.950     0.945     0.947      2025

Review queue only:
                       precision    recall  f1-score   support

GENUINE_BILLING_ERROR      0.908     0.965     0.936       143
        IVT_FILTERING      0.963     0.959     0.961       270
 LATE_OR_MISSING_DATA      0.862     0.954     0.906       131
       TIMEZONE_SHIFT      0.987     0.929     0.957        84
     WITHIN_TOLERANCE      0.871     0.701     0.777        87

             accuracy                          0.924       715
            macro avg      0.918     0.902     0.907       715
         weighted avg      0.925     0.924     0.923       715
```

```python
ACTIONS = {
    "WITHIN_TOLERANCE": "No action: gap is within contract tolerance.",
    "TIMEZONE_SHIFT": "No billing adjustment; ask the partner to report daily in UTC as the contract requires.",
    "IVT_FILTERING": "Ask for the partner's third-party IVT report; credit only verified invalid traffic.",
    "LATE_OR_MISSING_DATA": "Ask the partner to send the missing days; hold the invoice adjustment until data is complete.",
    "GENUINE_BILLING_ERROR": "Dispute: invoice on the contract's count with Apex log evidence attached.",
}
proba = model.predict_proba(feats[FEATURES])
top = proba.argsort(axis=1)
preds = pd.DataFrame({"deal_id": feats.deal_id, "billing_month": feats.billing_month,
                      "predicted_root_cause": model.classes_[top[:, -1]],
                      "confidence": proba[range(len(feats)), top[:, -1]].round(4),
                      "runner_up_cause": model.classes_[top[:, -2]], "model_version": version})
preds["recommended_action"] = preds.predicted_root_cause.map(ACTIONS)
spark.createDataFrame(preds).write.mode("overwrite").option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.ml.discrepancy_predictions")
```

## 3 · Work queue for the open closes (Jul–Sep)

```python
spark.sql(f"""
CREATE OR REPLACE TABLE {CATALOG}.gold.dispute_queue
COMMENT 'Open reconciliation cases for the Jul-Sep closes, ranked by revenue at risk, with the model root cause, evidence and recommended action. apex_exposure_usd is the part of revenue at risk that hits Apex''s own P&L.'
AS SELECT concat('CASE-', d.billing_month, '-', d.deal_id) AS case_id,
  d.billing_month, d.dsp_id, d.dsp_name, d.partner_team, d.deal_id, d.deal_name, d.publisher_name, d.content_genre,
  d.is_live, d.billing_count_basis, d.discrepancy_threshold_pct,
  d.ssp_impressions, d.dsp_impressions, d.impression_gap_pct,
  d.ssp_revenue_usd, d.dsp_revenue_usd, d.revenue_gap_usd, d.revenue_gap_pct, d.revenue_at_risk_usd,
  d.apex_take_rate_pct, d.publisher_paid_on, d.apex_exposure_usd,
  d.days_delivered, d.days_missing_in_dsp_report, d.large_gap_day_share,
  round(f.daily_gap_lag1_autocorr, 2) AS daily_gap_swing, d.ivt_risk_score,
  p.predicted_root_cause, p.confidence, p.runner_up_cause, p.recommended_action, p.model_version
FROM {CATALOG}.gold.recon_deal_month d
JOIN {CATALOG}.ml.root_cause_features f USING (deal_id, billing_month)
JOIN {CATALOG}.ml.discrepancy_predictions p USING (deal_id, billing_month)
WHERE d.billing_month >= '2026-07' AND d.needs_review
""")
q = spark.table(f"{CATALOG}.gold.dispute_queue")
queue = q.groupBy("billing_month").agg(F.count("*").alias("cases"), F.round(F.sum("revenue_at_risk_usd")).alias("usd"),
                                      F.round(F.sum("apex_exposure_usd")).alias("apex_exposure_usd")) \
         .toPandas().set_index("billing_month").to_dict("index")
print(queue)
```

Output:

```text
{'2026-08': {'cases': 257, 'usd': 6698764.0, 'apex_exposure_usd': 3366663.0}, '2026-07': {'cases': 239, 'usd': 4636200.0, 'apex_exposure_usd': 2262746.0}, '2026-09': {'cases': 219, 'usd': 6778508.0, 'apex_exposure_usd': 3294686.0}}
```

## 4 · Draft disputes with `ai_query`, then check them

```python
PROMPT = """You are a senior billing operations analyst at Apex Exchange, a CTV sell-side platform.
Draft a case summary for an internal analyst and a dispute email to the DSP partner, using ONLY the evidence below.
Rules:
- Quote dollar amounts and percentages exactly as given; do not invent numbers, dates or names; be firm, factual and courteous.
- Make exactly the ask in partner_ask. Respect billing_count_basis: if it is DSP, the partner's count governs the
  invoice, so ask the partner to correct and restate its report; never say Apex will invoice on its own count.
  If it is SSP, Apex's count governs and the invoice stands at the Apex amount.
- If the root cause implies no billing adjustment, say so, request the reporting fix, and set proposed_adjustment_usd to 0.
Return JSON only, with keys: case_summary (<=80 words), email_subject, email_body (<=180 words, signed 'Apex Exchange Billing Operations'),
proposed_adjustment_usd (number; 0 if no adjustment is requested).

EVIDENCE:
"""
spark.sql(f"""
WITH ev AS (
  SELECT case_id, to_json(named_struct(
    'case_id', case_id, 'billing_month', billing_month, 'partner', dsp_name, 'deal_id', deal_id, 'deal_name', deal_name,
    'apex_impressions', ssp_impressions, 'partner_impressions', dsp_impressions,
    'apex_revenue_usd', round(ssp_revenue_usd, 2), 'partner_revenue_usd', round(dsp_revenue_usd, 2),
    'revenue_gap_usd', round(revenue_gap_usd, 2), 'revenue_gap_pct', round(revenue_gap_pct, 2),
    'contract_threshold_pct', discrepancy_threshold_pct, 'billing_count_basis', billing_count_basis,
    'days_missing_in_partner_report', days_missing_in_dsp_report,
    'predicted_root_cause', predicted_root_cause, 'model_confidence', round(confidence, 2),
    'partner_ask', CASE
      WHEN predicted_root_cause IN ('TIMEZONE_SHIFT', 'WITHIN_TOLERANCE') THEN 'Correct reporting going forward; no billing adjustment.'
      WHEN predicted_root_cause = 'IVT_FILTERING' THEN 'Share the third-party IVT report supporting the removed impressions; only verified IVT will be credited.'
      WHEN predicted_root_cause = 'LATE_OR_MISSING_DATA' THEN 'Send the missing report days so the invoice can be reconciled.'
      WHEN billing_count_basis = 'SSP' THEN 'Pay the invoice at the Apex count, which governs under the contract.'
      ELSE 'Restate the report with corrected counts so the invoice can be reissued.' END)) AS evidence
  FROM (SELECT *, row_number() OVER (ORDER BY revenue_at_risk_usd DESC) AS rk
        FROM {CATALOG}.gold.dispute_queue WHERE predicted_root_cause <> 'WITHIN_TOLERANCE')
  WHERE rk <= 250
)
SELECT case_id, evidence,
  ai_query('{DRAFT_MODEL}', concat({json.dumps(PROMPT)}, evidence),
           modelParameters => named_struct('temperature', 0.0, 'max_tokens', 900)) AS raw_response
FROM ev
""").withColumn("j", F.from_json(F.regexp_replace("raw_response", r"(?s)^[^{]*|[^}]*$", ""),
                                 "case_summary STRING, email_subject STRING, email_body STRING, proposed_adjustment_usd DOUBLE")) \
    .select("case_id", "evidence", "j.*", F.lit(DRAFT_MODEL).alias("draft_model")) \
    .write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOG}.gold.dispute_drafts")
d = spark.table(f"{CATALOG}.gold.dispute_drafts").toPandas()


def grounded(row):  # every dollar figure in the draft must come from the evidence
    ev = json.loads(row.evidence)
    allowed = {round(abs(float(v))) for v in ev.values() if isinstance(v, (int, float))} | {round(abs(row.proposed_adjustment_usd or 0))}
    found = {round(float(x.replace(",", ""))) for x in re.findall(r"\$\s?([\d,]+(?:\.\d+)?)", f"{row.case_summary} {row.email_body}")}
    return all(any(abs(f - a) <= 1 for a in allowed) for f in found)


def contract_consistent(row):  # under a DSP-count contract, Apex can't invoice on its own count
    text = f"{row.case_summary} {row.email_body}".lower()
    return json.loads(row.evidence)["billing_count_basis"] != "DSP" or not re.search(r"invoic\w* (?:on|at|based on) (?:the )?apex", text)


judge = spark.createDataFrame(d[["case_id", "evidence", "email_body"]].head(30)).selectExpr("case_id", f"""ai_query('{JUDGE_MODEL}', concat(
  'Rate this dispute email against its evidence. Return JSON only: {{"accuracy":1-5,"tone":1-5,"actionable":1-5}}. ',
  'accuracy = every fact matches the evidence and the ask respects billing_count_basis; tone = professional; actionable = clear ask. ',
  'EVIDENCE: ', evidence, ' EMAIL: ', email_body), modelParameters => named_struct('temperature', 0.0)) AS verdict""").toPandas()
judge_scores = judge.verdict.str.extract(r"(\{.*\})", expand=False).apply(json.loads).apply(pd.Series)
genai = {"drafts": len(d), "parse_failures": int(d.email_body.isna().sum()),
         "dollars_grounded_rate": round(float(d.apply(grounded, axis=1).mean()), 4),
         "contract_consistent_rate": round(float(d.apply(contract_consistent, axis=1).mean()), 4),
         "judge_mean_n30": judge_scores[["accuracy", "tone", "actionable"]].astype(float).mean().round(2).to_dict(),
         "draft_model": DRAFT_MODEL, "judge_model": JUDGE_MODEL}
print(json.dumps(genai, indent=2))
sample = d.sort_values("case_id").head(2)
for r in sample.itertuples():
    print(f"\n===== {r.case_id} =====\n{r.case_summary}\n\nSUBJECT: {r.email_subject}\n{r.email_body}")
```

Output:

```text
{
  "drafts": 250,
  "parse_failures": 0,
  "dollars_grounded_rate": 1.0,
  "contract_consistent_rate": 1.0,
  "judge_mean_n30": {
    "accuracy": 4.7,
    "tone": 5.0,
    "actionable": 4.97
  },
  "draft_model": "databricks-claude-sonnet-4-6",
  "judge_model": "databricks-gpt-5-4-mini"
}

===== CASE-2026-07-D00015 =====
CASE-2026-07-D00015: Ember Ads (Deal D00015, Summit News Live · Sports · OPEN) shows a $34,563.45 (9.33%) revenue gap for July 2026, exceeding the 7.5% contract threshold. Apex recorded 7,886,882 impressions vs. Ember Ads' 7,153,576. Billing basis is DSP. Predicted root cause is late/missing data; partner report is missing 2 days. Resolution requires Ember Ads to submit the missing report days for full reconciliation.

SUBJECT: Billing Dispute – CASE-2026-07-D00015 | Deal D00015 Summit News Live · Sports · OPEN | July 2026 | Missing Report Days
Dear Ember Ads Billing Team,

We are writing regarding a discrepancy identified for Deal D00015 (Summit News Live · Sports · OPEN) for the billing period July 2026.

Our review shows the following:
- Apex Impressions: 7,886,882
- Ember Ads Reported Impressions: 7,153,576
- Apex Revenue: $370,386.36
- Ember Ads Reported Revenue: $335,822.91
- Revenue Gap: $34,563.45 (9.33%)

This gap exceeds the contractual threshold of 7.5%. As billing is governed by DSP counts, we have identified that your report appears to be missing 2 days of data, which we believe is the primary driver of this discrepancy.

We kindly ask that you submit the missing report days so that we can complete reconciliation and finalize the invoice accordingly.

Please respond at your earliest convenience. We are happy to assist in resolving this promptly.

Best regards,
Apex Exchange Billing Operations

===== CASE-2026-07-D00017 =====
CASE-2026-07-D00017: For deal D00017 (Lakeshore Stream · Entertainment · PG), Kestrel Demand reported 4,431,012 impressions vs. Apex's 5,199,466—a gap of 768,454 impressions driving a $27,869.76 (14.78%) revenue shortfall against a 10.0% contract threshold. Billing basis is DSP. Predicted root cause is IVT filtering (confidence: 100%). No missing report days. Partner must provide third-party IVT documentation; only verified IVT will be credited.

SUBJECT: Billing Dispute – CASE-2026-07-D00017 | Deal D00017 Lakeshore Stream · Entertainment · PG | July 2026 | IVT Filtering Documentation Required
Dear Kestrel Demand Billing Team,

We are writing regarding a discrepancy identified for Deal D00017 (Lakeshore Stream · Entertainment · PG) for the billing period July 2026.

Apex recorded 5,199,466 impressions ($188,572.42), while your report reflects 4,431,012 impressions ($160,702.66)—a revenue gap of $27,869.76 (14.78%), which exceeds our contractual threshold of 10.0%.

Our analysis indicates the likely root cause is IVT filtering applied on your side. As billing is governed by DSP count, we require supporting documentation to evaluate any adjustment.

Action Required: Please share the third-party IVT report substantiating the impressions removed from your count. Only impressions verified as IVT through a recognized third-party provider will be eligible for credit.

Kindly provide the documentation within 5 business days. We are happy to discuss further if needed.

Best regards,
Apex Exchange Billing Operations
```

## 5 · Serving table for the app, refreshed into Lakebase

```python
spark.sql(f"""
CREATE OR REPLACE TABLE {CATALOG}.gold.case_workbench
COMMENT 'One row per open case with evidence, model root cause and GenAI draft. Synced to Lakebase (serving.case_workbench) for the app.'
AS SELECT q.*, d.case_summary, d.email_subject, d.email_body, d.proposed_adjustment_usd
FROM {CATALOG}.gold.dispute_queue q LEFT JOIN {CATALOG}.gold.dispute_drafts d USING (case_id)
""")
w = WorkspaceClient()
try:
    synced = w.api_client.do("GET", f"/api/2.0/postgres/synced_tables/{CATALOG}.serving.case_workbench")
    w.pipelines.start_update(synced["status"]["pipeline_id"])
    lakebase = f"refresh started (pipeline {synced['status']['pipeline_id']})"
except Exception as e:  # the synced table is created once by hand; see RUNBOOK
    lakebase = f"not refreshed: {e}"
print("Lakebase sync:", lakebase)

dbutils.notebook.exit(json.dumps({"model_version": version, "model_results": results, "queue": queue,
                                  "genai": genai, "lakebase_sync": lakebase,
                                  "sample_drafts": sample[["case_id", "case_summary", "email_body"]].to_dict("records")}, default=str))
```

Output:

```text
Notebook exit value:
{"model_version": 10, "model_results": {"holdout_vs_analyst_labels": {"model": {"accuracy": 0.854, "macro_f1": 0.8497}, "playbook": {"accuracy": 0.6361, "macro_f1": 0.5442}}, "jul_sep_vs_true_cause": {"model": {"accuracy": 0.9452, "macro_f1": 0.9109}, "playbook": {"accuracy": 0.8212, "macro_f1": 0.5797}}, "jul_sep_review_queue_vs_true_cause": {"cases": 715, "model": {"accuracy": 0.9245, "macro_f1": 0.9073}, "playbook": {"accuracy": 0.5524, "macro_f1": 0.4119}}}, "queue": {"2026-08": {"cases": 257, "usd": 6698764.0, "apex_exposure_usd": 3366663.0}, "2026-07": {"cases": 239, "usd": 4636200.0, "apex_exposure_usd": 2262746.0}, "2026-09": {"cases": 219, "usd": 6778508.0, "apex_exposure_usd": 3294686.0}}, "genai": {"drafts": 250, "parse_failures": 0, "dollars_grounded_rate": 1.0, "contract_consistent_rate": 1.0, "judge_mean_n30": {"accuracy": 4.7, "tone": 5.0, "actionable": 4.97}, "draft_model": "databricks-claude-sonnet-4-6", "judge_model": "databricks-gpt-5-4-mini"}, "lakebase_sync": "refresh started (pipeline 48cbab11-7eab-4c56-90ea-ec35cee07631)", "sample_drafts": [{"case_id": "CASE-2026-07-D00015", "case_summary": "CASE-2026-07-D00015: Ember Ads (Deal D00015, Summit News Live \u00b7 Sports \u00b7 OPEN) shows a $34,563.45 (9.33%) revenue gap for July 2026, exceeding the 7.5% contract threshold. Apex recorded 7,886,882 impressions vs. Ember Ads' 7,153,576. Billing basis is DSP. Predicted root cause is late/missing data; partner report is missing 2 days. Resolution requires Ember Ads to submit the missing report days for full reconciliation.", "email_body": "Dear Ember Ads Billing Team,\n\nWe are writing regarding a discrepancy identified for Deal D00015 (Summit News Live \u00b7 Sports \u00b7 OPEN) for the billing period July 2026.\n\nOur review shows the following:\n- Apex Impressions: 7,886,882\n- Ember Ads Reported Impressions: 7,153,576\n- Apex Revenue: $370,386.36\n- Ember Ads Reported Revenue: $335,822.91\n- Revenue Gap: $34,563.45 (9.33%)\n\nThis gap exceeds the contractual threshold of 7.5%. As billing is governed by DSP counts, we have identified that your report appears to be missing 2 days of data, which we believe is the primary driver of this discrepancy.\n\nWe kindly ask that you submit the missing report days so that we can complete reconciliation and finalize the invoice accordingly.\n\nPlease respond at your earliest convenience. We are happy to assist in resolving this promptly.\n\nBest regards,\nApex Exchange Billing Operations"}, {"case_id": "CASE-2026-07-D00017", "case_summary": "CASE-2026-07-D00017: For deal D00017 (Lakeshore Stream \u00b7 Entertainment \u00b7 PG), Kestrel Demand reported 4,431,012 impressions vs. Apex's 5,199,466\u2014a gap of 768,454 impressions driving a $27,869.76 (14.78%) revenue shortfall against a 10.0% contract threshold. Billing basis is DSP. Predicted root cause is IVT filtering (confidence: 100%). No missing report days. Partner must provide third-party IVT documentation; only verified IVT will be credited.", "email_body": "Dear Kestrel Demand Billing Team,\n\nWe are writing regarding a discrepancy identified for Deal D00017 (Lakeshore Stream \u00b7 Entertainment \u00b7 PG) for the billing period July 2026.\n\nApex recorded 5,199,466 impressions ($188,572.42), while your report reflects 4,431,012 impressions ($160,702.66)\u2014a revenue gap of $27,869.76 (14.78%), which exceeds our contractual threshold of 10.0%.\n\nOur analysis indicates the likely root cause is IVT filtering applied on your side. As billing is governed by DSP count, we require supporting documentation to evaluate any adjustment.\n\nAction Required: Please share the third-party IVT report substantiating the impressions removed from your count. Only impressions verified as IVT through a recognized third-party provider will be eligible for credit.\n\nKindly provide the documentation within 5 business days. We are happy to discuss further if needed.\n\nBest regards,\nApex Exchange Billing Operations"}]}
```
