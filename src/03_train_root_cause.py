# Databricks notebook source
# MAGIC %md
# MAGIC # 03 · Root-cause classifier
# MAGIC
# MAGIC Learns from **2,000+ disputes Billing Ops resolved in Jan–Jun 2026** to predict *why* a CTV deal's DSP billing
# MAGIC report doesn't match Apex's logs. Compared against the analysts' current rule-of-thumb playbook, then evaluated
# MAGIC out-of-time on Jul–Sep (the three open closes) against the generator's planted ground truth, which the model never sees.

# COMMAND ----------

import json

import mlflow
import numpy as np
import pandas as pd
from mlflow.models import infer_signature
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

dbutils.widgets.text("catalog", "apex_recon")
CATALOG = dbutils.widgets.get("catalog")
MODEL_NAME = f"{CATALOG}.ml.discrepancy_root_cause"
mlflow.set_registry_uri("databricks-uc")
user = spark.sql("SELECT current_user()").first()[0]
mlflow.set_experiment(f"/Users/{user}/apex-recon-root-cause")

NUMERIC = ["impression_gap_pct", "revenue_gap_pct", "rev_minus_imp_gap_pct", "large_gap_day_share", "missing_day_share",
           "daily_gap_std", "daily_gap_median", "daily_gap_min", "daily_gap_max", "daily_gap_lag1_autocorr",
           "gap_volume_corr", "share_days_dsp_over", "tz_shift_gain", "best_shift_hours", "sibling_offset_match",
           "ivt_risk_score", "discrepancy_threshold_pct"]
BOOLEAN = ["is_live", "is_non_usd"]
CATEGORICAL = ["ssai_vendor", "content_genre", "publisher_type", "device_type", "deal_type"]
FEATURES = NUMERIC + BOOLEAN + CATEGORICAL

# COMMAND ----------

feats = spark.table(f"{CATALOG}.ml.discrepancy_features").toPandas()
labels = spark.table(f"{CATALOG}.silver.dispute_history").select("deal_id", "billing_month", "resolved_root_cause").toPandas()
truth = spark.table(f"{CATALOG}.ml.ground_truth_root_causes").select("deal_id", "billing_month", "root_cause").toPandas()

for c in BOOLEAN:
    feats[c] = feats[c].astype(float)
train_df = feats.merge(labels, on=["deal_id", "billing_month"])
current = feats[feats.billing_month >= "2026-07"].merge(truth, on=["deal_id", "billing_month"])
print(f"labelled history cases: {len(train_df):,}   current deal-months to score: {len(current):,}")
print(train_df.resolved_root_cause.value_counts().to_string())

# COMMAND ----------

# MAGIC %md ## Baseline: today's analyst playbook as rules

# COMMAND ----------


def playbook(r):
    if abs(r.revenue_gap_pct) <= r.discrepancy_threshold_pct and r.large_gap_day_share < 0.3:
        return "WITHIN_TOLERANCE"
    if r.missing_day_share > 0:
        return "LATE_OR_MISSING_DATA"
    if r.is_non_usd and abs(r.rev_minus_imp_gap_pct) > 3:
        return "FX_MISMATCH"
    if abs(r.impression_gap_pct) > 25:
        return "DEAL_ID_MISMAPPING"
    if abs(r.revenue_gap_pct) <= r.discrepancy_threshold_pct:
        return "TIMEZONE_SHIFT"
    return "IVT_FILTERING"  # the default answer most DSPs give


# COMMAND ----------

X, y = train_df[FEATURES], train_df.resolved_root_cause
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, stratify=y, random_state=7)

model = Pipeline([
    ("prep", ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL)],
                               remainder="passthrough")),
    ("gbm", HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08, max_leaf_nodes=31,
                                           l2_regularization=0.1, class_weight="balanced", random_state=7)),
])


def scores(y_true, y_pred):
    return {"accuracy": round(accuracy_score(y_true, y_pred), 4),
            "macro_f1": round(f1_score(y_true, y_pred, average="macro"), 4),
            "weighted_f1": round(f1_score(y_true, y_pred, average="weighted"), 4)}


with mlflow.start_run(run_name="hgb_root_cause") as run:
    model.fit(X_tr, y_tr)
    holdout = scores(y_te, model.predict(X_te))
    holdout_rules = scores(y_te, X_te.apply(playbook, axis=1))
    oot_pred = model.predict(current[FEATURES])
    oot = scores(current.root_cause, oot_pred)
    oot_rules = scores(current.root_cause, current[FEATURES].apply(playbook, axis=1))

    mlflow.log_params({"model": "HistGradientBoostingClassifier", "max_iter": 300, "learning_rate": 0.08,
                       "train_rows": len(X_tr), "features": len(FEATURES)})
    for prefix, s in [("holdout", holdout), ("holdout_rules", holdout_rules), ("oot", oot), ("oot_rules", oot_rules)]:
        mlflow.log_metrics({f"{prefix}_{k}": v for k, v in s.items()})

    classes = sorted(set(current.root_cause) | set(oot_pred))
    cm = pd.DataFrame(confusion_matrix(current.root_cause, oot_pred, labels=classes), index=classes, columns=classes)
    report = classification_report(current.root_cause, oot_pred, digits=3, zero_division=0)
    mlflow.log_text(cm.to_string(), "oot_confusion_matrix.txt")
    mlflow.log_text(report, "oot_classification_report.txt")
    mlflow.sklearn.log_model(model, "model", signature=infer_signature(X_tr, model.predict(X_tr)),
                             input_example=X_tr.head(3), registered_model_name=MODEL_NAME)

version = max(int(v.version) for v in mlflow.MlflowClient().search_model_versions(f"name='{MODEL_NAME}'"))
mlflow.MlflowClient().set_registered_model_alias(MODEL_NAME, "champion", version)

print("Holdout (Jan-Jun cases):  model", holdout, "| playbook", holdout_rules)
print("Out-of-time (Jul-Sep):    model", oot, "| playbook", oot_rules)
print("\nOut-of-time confusion matrix (rows = true cause, cols = predicted):\n", cm.to_string())
print("\n", report)

# COMMAND ----------

dbutils.notebook.exit(json.dumps({
    "mlflow_run_id": run.info.run_id, "registered_model": MODEL_NAME, "version": version, "alias": "champion",
    "train_rows": len(X_tr), "holdout_rows": len(X_te), "oot_rows": len(current),
    "holdout_model": holdout, "holdout_playbook": holdout_rules, "oot_model": oot, "oot_playbook": oot_rules,
    "oot_confusion_matrix": cm.to_dict(), "oot_classification_report": report,
}))
