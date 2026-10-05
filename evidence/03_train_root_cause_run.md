# Job run evidence: [dev megan_fogal] apex-recon-build

- Run ID: `1002111410920803`  
- Result: **FAILED**  
- Started: 2026-10-05 15:34:29 UTC  
- Ended: 2026-10-05 15:37:44 UTC  
- Run page: https://fevm-serverless-3dmees.cloud.databricks.com/?o=7474652285429726#job/602392988880313/run/1002111410920803

| Task | Result | Duration (min) |
|---|---|---:|
| `generate_data` | DISABLED | 0.0 |
| `ingest_and_reconcile` | DISABLED | 0.0 |
| `train_root_cause_model` | SUCCESS | 1.3 |
| `score_and_draft_disputes` | FAILED | 0.8 |
| `score_and_draft_disputes` | FAILED | 1.1 |

## Task `generate_data`


## Task `ingest_and_reconcile`

Pipeline `5d44a671-5813-463d-903e-33ca04bb3376`, update `b22496e9-3dfb-44ba-9e37-b8a8fc495095` → **COMPLETED**

Rows written and expectation results: see `evidence/02_pipeline_evidence.md`.

## Task `train_root_cause_model`

```json
{
  "mlflow_run_id": "7244ed517dfe4491ad525c6e5049b3e1",
  "registered_model": "apex_recon.ml.discrepancy_root_cause",
  "version": 1,
  "alias": "champion",
  "train_rows": 1614,
  "holdout_rows": 538,
  "oot_rows": 2009,
  "holdout_model": {
    "accuracy": 0.9424,
    "macro_f1": 0.943,
    "weighted_f1": 0.9424
  },
  "holdout_playbook": {
    "accuracy": 0.5093,
    "macro_f1": 0.4528,
    "weighted_f1": 0.4464
  },
  "oot_model": {
    "accuracy": 0.9786,
    "macro_f1": 0.9734,
    "weighted_f1": 0.9791
  },
  "oot_playbook": {
    "accuracy": 0.674,
    "macro_f1": 0.4685,
    "weighted_f1": 0.6265
  },
  "oot_confusion_matrix": {
    "DEAL_ID_MISMAPPING": {
      "DEAL_ID_MISMAPPING": 119,
      "FX_MISMATCH": 0,
      "GENUINE_BILLING_ERROR": 0,
      "IVT_FILTERING": 0,
      "LATE_OR_MISSING_DATA": 0,
      "SSAI_BEACON_LOSS": 0,
      "TIMEZONE_SHIFT": 0,
      "WITHIN_TOLERANCE": 0
    },
    "FX_MISMATCH": {
      "DEAL_ID_MISMAPPING": 0,
      "FX_MISMATCH": 94,
      "GENUINE_BILLING_ERROR": 0,
      "IVT_FILTERING": 0,
      "LATE_OR_MISSING_DATA": 0,
      "SSAI_BEACON_LOSS": 1,
      "TIMEZONE_SHIFT": 0,
      "WITHIN_TOLERANCE": 0
    },
    "GENUINE_BILLING_ERROR": {
      "DEAL_ID_MISMAPPING": 0,
      "FX_MISMATCH": 0,
      "GENUINE_BILLING_ERROR": 110,
      "IVT_FILTERING": 0,
      "LATE_OR_MISSING_DATA": 0,
      "SSAI_BEACON_LOSS": 0,
      "TIMEZONE_SHIFT": 0,
      "WITHIN_TOLERANCE": 0
    },
    "IVT_FILTERING": {
      "DEAL_ID_MISMAPPING": 0,
      "FX_MISMATCH": 0,
      "GENUINE_BILLING_ERROR": 0,
      "IVT_FILTERING": 218,
      "LATE_OR_MISSING_DATA": 0,
      "SSAI_BEACON_LOSS": 0,
      "TIMEZONE_SHIFT": 0,
      "WITHIN_TOLERANCE": 0
    },
    "LATE_OR_MISSING_DATA": {
      "DEAL_ID_MISMAPPING": 1,
      "FX_MISMATCH": 0,
      "GENUINE_BILLING_ERROR": 0,
      "IVT_FILTERING": 1,
      "LATE_OR_MISSING_DATA": 103,
      "SSAI_BEACON_LOSS": 3,
      "TIMEZONE_SHIFT": 0,
      "WITHIN_TOLERANCE": 19
    },
    "SSAI_BEACON_LOSS": {
      "DEAL_ID_MISMAPPING": 0,
      "FX_MISMATCH": 0,
      "GENUINE_BILLING_ERROR": 0,
      "IVT_FILTERING": 4,
      "LATE_OR_MISSING_DATA": 0,
      "SSAI_BEACON_LOSS": 216,
      "TIMEZONE_SHIFT": 1,
      "WITHIN_TOLERANCE": 1
    },
    "TIMEZONE_SHIFT": {
      "DEAL_ID_MISMAPPING": 0,
      "FX_MISMATCH": 0,
      "GENUINE_BILLING_ERROR": 0,
      "IVT_FILTERING": 0,
      "LATE_OR_MISSING_DATA": 0,
      "SSAI_BEACON_LOSS": 0,
      "TIMEZONE_SHIFT": 181,
      "WITHIN_TOLERANCE": 0
    },
    "WITHIN_TOLERANCE": {
      "DEAL_ID_MISMAPPING": 2,
      "FX_MISMATCH": 0,
      "GENUINE_BILLING_ERROR": 3,
      "IVT_FILTERING": 2,
      "LATE_OR_MISSING_DATA": 5,
      "SSAI_BEACON_LOSS": 0,
      "TIMEZONE_SHIFT": 0,
      "WITHIN_TOLERANCE": 925
    }
  },
  "oot_classification_report": "                       precision    recall  f1-score   support\n\n   DEAL_ID_MISMAPPING      1.000     0.975     0.988       122\n          FX_MISMATCH      0.989     1.000     0.995        94\nGENUINE_BILLING_ERROR      1.000     0.973     0.987       113\n        IVT_FILTERING      1.000     0.969     0.984       225\n LATE_OR_MISSING_DATA      0.811     0.954     0.877       108\n     SSAI_BEACON_LOSS      0.973     0.982     0.977       220\n       TIMEZONE_SHIFT      1.000     0.995     0.997       182\n     WITHIN_TOLERANCE      0.987     0.979     0.983       945\n\n             accuracy                          0.979      2009\n            macro avg      0.970     0.978     0.973      2009\n         weighted avg      0.980     0.979     0.979      2009\n"
}
```

## Task `score_and_draft_disputes`

```
An unexpected error occurred.
Please contact Databricks support and provide the trace ID: 7474652285429726/602392988880313/1002111410920803/858368570545771.
ecutionThreadLocalCaptured.$anonfun$runWith$3(SQLExecution.scala:169)
	at com.databricks.sql.transaction.tahoe.OptimisticTransaction$.withActive(OptimisticTransaction.scala:374)
	at com.databricks.sql.transaction.tahoe.ConcurrencyHelpers$.withOptimisticTransaction(ConcurrencyHelpers.scala:54)
	at org.apache.spark.sql.execution.SQLExecutionThreadLocalCaptured.$anonfun$runWith$2(SQLExecution.scala:168)
	at org.apache.spark.sql.execution.SQLExecution$.withSessionTagsApplied(SQLExecution.scala:1989)
	at org.apache.spark.sql.execution.SQLExecutionThreadLocalCaptured.$anonfun$runWith$1(SQLExecution.scala:159)
	at org.apache.spark.JobArtifactSet$.withActiveJobArtifactState(JobArtifactSet.scala:97)
	at org.apache.spark.sql.execution.SQLExecutionThreadLocalCaptured.runWith(SQLExecution.scala:153)
	at org.apache.spark.sql.execution.SQLExecution$.$anonfun$withThreadLocalCaptured$1(SQLExecution.scala:2169)
	at java.util.concurrent.CompletableFuture$AsyncSupply.run(CompletableFuture.java:1768)
	at org.apache.spark.util.threads.SparkThreadLocalCapturingRunnable.$anonfun$run$1(SparkThreadLocalForwardingThreadPoolExecutor.scala:171)
	at scala.runtime.java8.JFunction0$mcV$sp.apply(JFunction0$mcV$sp.scala:18)
	at com.databricks.spark.util.DBRTracing$.withSpanFromParent(DBRTracing.scala:70)
	at org.apache.spark.util.threads.SparkThreadLocalCapturingHelper.$anonfun$runWithCaptured$7(SparkThreadLocalForwardingThreadPoolExecutor.scala:124)
	at com.databricks.util.LexicalThreadLocal$Handle.runWith(LexicalThreadLocal.scala:63)
	at org.apache.spark.util.threads.SparkThreadLocalCapturingHelper.$anonfun$runWithCaptured$6(SparkThreadLocalForwardingThreadPoolExecutor.scala:123)
	at com.databricks.sql.transaction.tahoe.mst.MSTThreadHelper$.runWithMSTContext(MSTThreadHelper.scala:77)
	at org.apache.spark.util.threads.SparkThreadLocalCapturingHelper.$anonfun$runWithCaptured$5(SparkThreadLocalForwardingThreadPoolExecutor.scala:120)
	at com.databricks.spark.util.IdentityClaim$.withClaim(IdentityClaim.scala:48)
	at org.apache.spark.util.threads.SparkThreadLocalCapturingHelper.$anonfun$runWithCaptured$4(SparkThreadLocalForwardingThreadPoolExecutor.scala:119)
	at com.databricks.unity.UCSEphemeralState$Handle.runWith(UCSEphemeralState.scala:51)
	at org.apache.spark.util.threads.SparkThreadLocalCapturingHelper.runWithCaptured(SparkThreadLocalForwardingThreadPoolExecutor.scala:118)
	at org.apache.spark.util.threads.SparkThreadLocalCapturingHelper.runWithCaptured$(SparkThreadLocalForwardingThreadPoolExecutor.scala:95)
	at org.apache.spark.util.threads.SparkThreadLocalCapturingRunnable.runWithCaptured(SparkThreadLocalForwardingThreadPoolExecutor.scala:168)
	at org.apache.spark.util.threads.SparkThreadLocalCapturingRunnable.run(SparkThreadLocalForwardingThreadPoolExecutor.scala:171)
	at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1136)
	at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:635)
	at java.lang.Thread.run(Thread.java:840)
```

## Task `score_and_draft_disputes`

```
An unexpected error occurred.
Please contact Databricks support and provide the trace ID: 7474652285429726/602392988880313/1002111410920803/775840397533143.
t org.apache.spark.sql.execution.SQLExecution$.withSessionTagsApplied(SQLExecution.scala:1989)
	at org.apache.spark.sql.execution.SQLExecutionThreadLocalCaptured.$anonfun$runWith$1(SQLExecution.scala:159)
	at org.apache.spark.JobArtifactSet$.withActiveJobArtifactState(JobArtifactSet.scala:97)
	at org.apache.spark.sql.execution.SQLExecutionThreadLocalCaptured.runWith(SQLExecution.scala:153)
	at org.apache.spark.sql.execution.SQLExecution$.$anonfun$withThreadLocalCaptured$1(SQLExecution.scala:2169)
	at java.util.concurrent.CompletableFuture$AsyncSupply.run(CompletableFuture.java:1768)
	at org.apache.spark.util.threads.SparkThreadLocalCapturingRunnable.$anonfun$run$1(SparkThreadLocalForwardingThreadPoolExecutor.scala:171)
	at scala.runtime.java8.JFunction0$mcV$sp.apply(JFunction0$mcV$sp.scala:18)
	at com.databricks.logging.AttributionContext$.withValue(AttributionContext.scala:354)
	at com.databricks.spark.util.DatabricksTracingHelper.$anonfun$withSpanFromParent$6(DatabricksSparkTracingHelper.scala:219)
	at com.databricks.util.TracingSpanUtils$.withTracing(TracingSpanUtils.scala:100)
	at com.databricks.spark.util.DatabricksTracingHelper.withSpanFromParent(DatabricksSparkTracingHelper.scala:217)
	at com.databricks.spark.util.DBRTracing$.withSpanFromParent(DBRTracing.scala:68)
	at org.apache.spark.util.threads.SparkThreadLocalCapturingHelper.$anonfun$runWithCaptured$7(SparkThreadLocalForwardingThreadPoolExecutor.scala:124)
	at com.databricks.util.LexicalThreadLocal$Handle.runWith(LexicalThreadLocal.scala:63)
	at org.apache.spark.util.threads.SparkThreadLocalCapturingHelper.$anonfun$runWithCaptured$6(SparkThreadLocalForwardingThreadPoolExecutor.scala:123)
	at com.databricks.sql.transaction.tahoe.mst.MSTThreadHelper$.runWithMSTContext(MSTThreadHelper.scala:77)
	at org.apache.spark.util.threads.SparkThreadLocalCapturingHelper.$anonfun$runWithCaptured$5(SparkThreadLocalForwardingThreadPoolExecutor.scala:120)
	at com.databricks.spark.util.IdentityClaim$.withClaim(IdentityClaim.scala:48)
	at org.apache.spark.util.threads.SparkThreadLocalCapturingHelper.$anonfun$runWithCaptured$4(SparkThreadLocalForwardingThreadPoolExecutor.scala:119)
	at com.databricks.unity.UCSEphemeralState$Handle.runWith(UCSEphemeralState.scala:51)
	at org.apache.spark.util.threads.SparkThreadLocalCapturingHelper.runWithCaptured(SparkThreadLocalForwardingThreadPoolExecutor.scala:118)
	at org.apache.spark.util.threads.SparkThreadLocalCapturingHelper.runWithCaptured$(SparkThreadLocalForwardingThreadPoolExecutor.scala:95)
	at org.apache.spark.util.threads.SparkThreadLocalCapturingRunnable.runWithCaptured(SparkThreadLocalForwardingThreadPoolExecutor.scala:168)
	at org.apache.spark.util.threads.SparkThreadLocalCapturingRunnable.run(SparkThreadLocalForwardingThreadPoolExecutor.scala:171)
	at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1136)
	at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:635)
	at java.lang.Thread.run(Thread.java:840)
```
