# Job run evidence: [dev megan_fogal] apex-recon-build

- Run ID: `352850418484417`  
- Result: **SUCCESS**  
- Started: 2026-10-05 17:26:10 UTC  
- Ended: 2026-10-05 17:27:06 UTC  
- Run page: https://fevm-serverless-3dmees.cloud.databricks.com/?o=7474652285429726#job/602392988880313/run/352850418484417

| Task | Result | Duration (min) |
|---|---|---:|
| `generate_data` | DISABLED | 0.0 |
| `ingest_and_reconcile` | DISABLED | 0.0 |
| `apply_governance` | DISABLED | 0.0 |
| `sync_case_status_to_uc` | SUCCESS | 0.9 |
| `refresh_lakebase_queue` | DISABLED | 0.0 |
| `train_root_cause_model` | DISABLED | 0.0 |
| `score_and_draft_disputes` | DISABLED | 0.0 |

## Task `generate_data`


## Task `ingest_and_reconcile`

Pipeline `5d44a671-5813-463d-903e-33ca04bb3376`, update `308849b7-1c8c-4722-ac18-8aa501d96148` → **COMPLETED**

Rows written and expectation results: see `evidence/02_pipeline_evidence.md`.

## Task `apply_governance`


## Task `sync_case_status_to_uc`

```json
{
  "rows_snapshotted": {
    "dispute_cases": 1,
    "case_events": 3,
    "credit_approvals": 1
  },
  "status_summary": [
    {
      "status": "OPEN",
      "cases": 954,
      "revenue_at_risk_usd": 27186795.0,
      "recovered_usd": 0.0,
      "credited_usd": 0.0
    },
    {
      "status": "RESOLVED",
      "cases": 1,
      "revenue_at_risk_usd": 215006.0,
      "recovered_usd": 0.0,
      "credited_usd": 215006.0
    }
  ]
}
```

## Task `refresh_lakebase_queue`

Pipeline `248ca05a-ee23-46ed-a2c0-0e442bd0434b`, update `e44e1cbe-9fd8-40eb-8ab3-f5d77e9e8c59` → **COMPLETED**

Rows written and expectation results: see `evidence/02_pipeline_evidence.md`.

## Task `train_root_cause_model`


## Task `score_and_draft_disputes`

