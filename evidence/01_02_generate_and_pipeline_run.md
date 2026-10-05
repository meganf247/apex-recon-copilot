# Job run evidence: [dev megan_fogal] apex-recon-build

- Run ID: `34956105474106`  
- Result: **SUCCESS**  
- Started: 2026-10-05 15:24:44 UTC  
- Ended: 2026-10-05 15:33:15 UTC  
- Run page: https://fevm-serverless-3dmees.cloud.databricks.com/?o=7474652285429726#job/602392988880313/run/34956105474106

| Task | Result | Duration (min) |
|---|---|---:|
| `generate_data` | SUCCESS | 5.9 |
| `ingest_and_reconcile` | SUCCESS | 2.6 |

## Task `generate_data`

```json
{
  "seed": 42,
  "window": "2026-01-01..2026-09-30",
  "entities": {
    "dsps": 40,
    "ctv_publishers": 150,
    "deals": 800
  },
  "ssp_log_rows": 3541306,
  "total_impressions": 29786455231,
  "gross_revenue_usd": 1111800983.5,
  "dsp_report_rows": 157672,
  "publisher_report_rows": 158703,
  "files": {
    "ssp_logs": 273,
    "dsp_reports": 351,
    "publisher_reports": 1336,
    "reference": 6,
    "history": 1
  },
  "dq_defects_injected": {
    "null_deal_id": 615,
    "negative_impressions": 303,
    "bad_date": 308,
    "duplicate_rows": 450,
    "unknown_seat": 46
  },
  "deal_months": 5514,
  "root_cause_distribution_all": {
    "WITHIN_TOLERANCE": 2624,
    "IVT_FILTERING": 620,
    "SSAI_BEACON_LOSS": 592,
    "TIMEZONE_SHIFT": 502,
    "DEAL_ID_MISMAPPING": 318,
    "LATE_OR_MISSING_DATA": 304,
    "GENUINE_BILLING_ERROR": 286,
    "FX_MISMATCH": 268
  },
  "historical_dispute_cases": 2152,
  "current_months_revenue_gap_usd_by_cause": {
    "DEAL_ID_MISMAPPING": 288305.0,
    "FX_MISMATCH": 1589374.0,
    "GENUINE_BILLING_ERROR": 3335932.0,
    "IVT_FILTERING": 4779046.0,
    "LATE_OR_MISSING_DATA": 2590975.0,
    "SSAI_BEACON_LOSS": 5223083.0,
    "TIMEZONE_SHIFT": 767425.0,
    "WITHIN_TOLERANCE": 2335998.0
  },
  "median_abs_gap_pct_by_cause": {
    "DEAL_ID_MISMAPPING": 34.52,
    "FX_MISMATCH": 7.52,
    "GENUINE_BILLING_ERROR": 14.97,
    "IVT_FILTERING": 9.77,
    "LATE_OR_MISSING_DATA": 15.02,
    "SSAI_BEACON_LOSS": 9.21,
    "TIMEZONE_SHIFT": 1.26,
    "WITHIN_TOLERANCE": 1.2
  }
}
```

## Task `ingest_and_reconcile`

Pipeline `5d44a671-5813-463d-903e-33ca04bb3376`, update `b22496e9-3dfb-44ba-9e37-b8a8fc495095` → **COMPLETED**

| Dataset | Output rows | Dropped by expectations |
|---|---:|---:|
