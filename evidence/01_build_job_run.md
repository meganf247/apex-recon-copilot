# Job run evidence: [dev megan_fogal] apex-recon-build

- Run ID: `903494114793173`  
- Result: **SUCCESS**  
- Started: 2026-10-06 17:05:38 UTC  
- Ended: 2026-10-06 17:19:25 UTC  
- Run page: https://fevm-megant-fevm.cloud.databricks.com/?o=7474649371849429#job/800507315624085/run/903494114793173

| Task | Result | Duration (min) |
|---|---|---:|
| `publish_case_status_view` | SUCCESS | 0.2 |
| `refresh_lakebase_queue` | SUCCESS | 0.5 |
| `generate_data` | SUCCESS | 6.2 |
| `ingest_and_reconcile` | SUCCESS | 2.2 |
| `score_and_draft_disputes` | SUCCESS | 3.4 |
| `apply_governance` | SUCCESS | 0.6 |
| `train_root_cause_model` | SUCCESS | 1.5 |

## Task `publish_case_status_view`


## Task `refresh_lakebase_queue`

Pipeline `e8b6f9fb-9b3b-4a4d-a55b-3372393e5240`, update `d6523e85-0e02-4357-a7d2-93aeb39ee6fc` → **COMPLETED**

Rows written and expectation results: see `evidence/02_pipeline_evidence.md`.

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
  "dsp_report_rows": 157694,
  "publisher_report_rows": 158703,
  "files": {
    "ssp_logs": 273,
    "dsp_reports": 351,
    "publisher_reports": 1336,
    "reference": 6,
    "history": 1
  },
  "dq_defects_injected": {
    "null_deal_id": 604,
    "negative_impressions": 320,
    "bad_date": 324,
    "duplicate_rows": 449,
    "unknown_seat": 32
  },
  "deal_months": 5514,
  "root_cause_distribution_all": {
    "WITHIN_TOLERANCE": 2699,
    "IVT_FILTERING": 628,
    "SSAI_BEACON_LOSS": 575,
    "TIMEZONE_SHIFT": 362,
    "DEAL_ID_MISMAPPING": 348,
    "LATE_OR_MISSING_DATA": 311,
    "GENUINE_BILLING_ERROR": 309,
    "FX_MISMATCH": 282
  },
  "historical_dispute_cases": 2171,
  "history_label_noise_rate": 0.112,
  "deal_months_with_secondary_cause": 937,
  "current_months_revenue_gap_usd_by_cause": {
    "DEAL_ID_MISMAPPING": 318416.0,
    "FX_MISMATCH": 1886663.0,
    "GENUINE_BILLING_ERROR": 3677328.0,
    "IVT_FILTERING": 4705917.0,
    "LATE_OR_MISSING_DATA": 4383260.0,
    "SSAI_BEACON_LOSS": 5655651.0,
    "TIMEZONE_SHIFT": 1165129.0,
    "WITHIN_TOLERANCE": 3482526.0
  },
  "median_abs_gap_pct_by_cause": {
    "DEAL_ID_MISMAPPING": 34.38,
    "FX_MISMATCH": 8.78,
    "GENUINE_BILLING_ERROR": 16.18,
    "IVT_FILTERING": 10.55,
    "LATE_OR_MISSING_DATA": 16.66,
    "SSAI_BEACON_LOSS": 10.45,
    "TIMEZONE_SHIFT": 2.48,
    "WITHIN_TOLERANCE": 1.52
  }
}
```

## Task `ingest_and_reconcile`

Pipeline `7e5bc896-605c-44f6-a2e3-039922e893a9`, update `e3daa7d1-3034-476c-9f45-41080972b882` → **COMPLETED**

Rows written and expectation results: see `evidence/02_pipeline_evidence.md`.

## Task `score_and_draft_disputes`

```json
{
  "model_version": 4,
  "deal_months_scored": 5517,
  "prediction_distribution": {
    "WITHIN_TOLERANCE": 2556,
    "IVT_FILTERING": 659,
    "SSAI_BEACON_LOSS": 590,
    "GENUINE_BILLING_ERROR": 401,
    "LATE_OR_MISSING_DATA": 382,
    "TIMEZONE_SHIFT": 348,
    "DEAL_ID_MISMAPPING": 322,
    "FX_MISMATCH": 259
  },
  "queue": {
    "2026-08": {
      "cases": 335,
      "usd": 9224502.0
    },
    "2026-07": {
      "cases": 344,
      "usd": 9933913.0
    },
    "2026-09": {
      "cases": 276,
      "usd": 8243385.0
    }
  },
  "genai_eval": {
    "drafts": 250,
    "parse_failures": 0,
    "dollars_grounded_rate": 1.0,
    "contract_consistent_rate": 0.992,
    "judge_sample": 30,
    "judge_mean": {
      "accuracy": 4.67,
      "tone": 5.0,
      "actionable": 4.97
    },
    "draft_model": "databricks-claude-sonnet-4-6",
    "judge_model": "databricks-gpt-5-4-mini"
  },
  "judge_issues": [
    {
      "case_id": "CASE-2026-08-D00028",
      "accuracy": 5,
      "tone": 5,
      "actionable": 5,
      "issue": "Matches evidence; asks partner to restate corrected counts for DSP basis."
    },
    {
      "case_id": "CASE-2026-07-D00234",
      "accuracy": 5,
      "tone": 5,
      "actionable": 5,
      "issue": "None"
    },
    {
      "case_id": "CASE-2026-09-D00586",
      "accuracy": 5,
      "tone": 5,
      "actionable": 5,
      "issue": "No issue"
    },
    {
      "case_id": "CASE-2026-09-D00227",
      "accuracy": 5,
      "tone": 5,
      "actionable": 5,
      "issue": "Matches evidence; asks partner to restate corrected DSP counts and re-attribute impressions."
    },
    {
      "case_id": "CASE-2026-07-D00616",
      "accuracy": 5,
      "tone": 5,
      "actionable": 5,
      "issue": "Matches evidence; clear SSP-basis ask and request for missing days' rows."
    },
    {
      "case_id": "CASE-2026-08-D00382",
      "accuracy": 5,
      "tone": 5,
      "actionable": 5,
      "issue": "Matches evidence; clear request to restate at contract FX rate and pay Apex count under SSP basis."
    },
    {
      "case_id": "CASE-2026-07-D00469",
      "accuracy": 5,
      "tone": 5,
      "actionable": 5,
      "issue": "Matches evidence; clear request for missing rows and payment at Apex count under SSP basis."
    },
    {
      "case_id": "CASE-2026-07-D00326",
      "accuracy": 5,
      "tone": 5,
      "actionable": 5,
      "issue": "Matches evidence; asks partner to restate corrected counts consistent with DSP basis."
    },
    {
      "case_id": "CASE-2026-09-D00603",
      "accuracy": 5,
      "tone": 5,
      "actionable": 5,
      "issue": "Matches evidence; asks for missing report rows and payment at Apex count under SSP basis."
    },
    {
      "case_id": "CASE-2026-09-D00528",
      "accuracy": 5,
      "tone": 5,
      "actionable": 5,
      "issue": "No material issues; aligns with SSP basis, cites the missing 6 days, and clearly requests the missing rows while confirming the Apex count governs."
    }
  ],
  "sample_drafts": [
    {
      "case_id": "CASE-2026-07-D00005",
      "case_summary": "Deal D00005 (Clearwater Play \u00b7 Sports \u00b7 OPEN) shows a 10.14% revenue gap for 2026-07: Apex counted 18,495,364 impressions ($855,826.25) vs. Lattice Media's 16,635,061 ($769,065.79), a $86,760.46 shortfall exceeding the 7.5% contract threshold. Billing basis is SSP (Apex governs). Root cause is SSAI beacon loss (model confidence 0.99). No timezone or missing-day issues detected. Apex invoice stands; partner must pay at Apex count.",
      "email_subject": "Billing Dispute \u2013 Deal D00005 Clearwater Play \u00b7 Sports \u00b7 OPEN | July 2026 | Action Required",
      "email_body": "Dear Lattice Media Billing Team,\n\nWe are writing regarding a discrepancy on Deal D00005 (Clearwater Play \u00b7 Sports \u00b7 OPEN) for the July 2026 billing period.\n\nApex recorded 18,495,364 impressions ($855,826.25), while your report reflects 16,635,061 impressions ($769,065.79) \u2014 a gap of $86,760.46 (10.14%), which exceeds the contractual 7.5% threshold.\n\nUnder our agreement, the SSP count governs billing. Our analysis (confidence: 99%) attributes the discrepancy to SSAI beacon loss on your side, with no timezone offsets or missing reporting days identified.\n\nAccordingly, the invoice stands at $855,826.25 and payment is due in full at the Apex count. To support resolution, we will share our SSAI beacon logs and recommend opening a ticket with the SSAI vendor jointly.\n\nPlease confirm acceptance of the invoice and provide your intended payment timeline at your earliest convenience. We are happy to schedule a call to review the beacon data together.\n\nBest regards,\nApex Exchange Billing Operations",
      "proposed_adjustment_usd": 0.0
    },
    {
      "case_id": "CASE-2026-07-D00006",
      "case_summary": "CASE-2026-07-D00006 | Sable Buy | Deal D00006 (Harborview Now \u00b7 News \u00b7 PG) | July 2026. Apex recorded 16,503,726 impressions ($754,371.43); partner reported 12,787,239 impressions ($584,415.42), a gap of 169,956.01 (22.53%), exceeding the 7.5% contract threshold. Root cause: 6 days of data are missing from the partner's report. Billing basis is SSP; Apex count governs. Invoice stands at $754,371.43. Partner must submit missing days and pay in full.",
      "email_subject": "Billing Dispute \u2013 CASE-2026-07-D00006 | Deal D00006 Harborview Now \u00b7 News \u00b7 PG | July 2026 | Missing Reporting Data",
      "email_body": "Dear Sable Buy Billing Team,\n\nWe are writing regarding a discrepancy identified on Deal D00006 (Harborview Now \u00b7 News \u00b7 PG) for the July 2026 billing period.\n\nApex Exchange recorded 16,503,726 impressions totaling $754,371.43. Your report reflects 12,787,239 impressions totaling $584,415.42 \u2014 a variance of $169,956.01 (22.53%), which materially exceeds the contractual 7.5% threshold.\n\nOur analysis indicates the gap is attributable to 6 days of data missing from your report. No timezone discrepancy was identified.\n\nAs this deal is governed by SSP-side counting per our contract, Apex's impression count is the billing basis of record. The invoice of $754,371.43 stands as issued.\n\nWe respectfully request two actions:\n1. Submit the missing 6 days of report rows for reconciliation purposes.\n2. Remit payment in full at the invoiced amount of $754,371.43.\n\nPlease respond within 5 business days. We are happy to assist with any questions.\n\nApex Exchange Billing Operations",
      "proposed_adjustment_usd": 0.0
    },
    {
      "case_id": "CASE-2026-07-D00010",
      "case_summary": "CASE-2026-07-D00010: For deal D00010 (Falcon Box \u00b7 Sports \u00b7 PMP), Willow Demand reported 6,597,508 impressions vs. Apex's 7,444,242 \u2014 a gap of 846,734 impressions (11.4%), exceeding the 5.0% contract threshold. Revenue gap is $33,847.86 ($296,957.71 vs. $263,109.85). Billing basis is DSP. Model confidence 97% points to IVT filtering as root cause. Third-party IVT verification required before any credit is issued.",
      "email_subject": "Billing Dispute \u2013 CASE-2026-07-D00010 | Deal D00010 Falcon Box \u00b7 Sports \u00b7 PMP | July 2026 | IVT Verification Required",
      "email_body": "Dear Willow Demand Billing Team,\n\nWe are writing regarding a discrepancy identified on Deal D00010 (Falcon Box \u00b7 Sports \u00b7 PMP) for the July 2026 billing period.\n\nYour report reflects 6,597,508 impressions and $263,109.85 in revenue, compared to Apex's recorded 7,444,242 impressions and $296,957.71 \u2014 a revenue gap of $33,847.86 (11.4%), which exceeds our contractual 5.0% variance threshold.\n\nOur analysis indicates the most probable root cause is IVT filtering on your side (model confidence: 97%). Under our agreement, billing is governed by the DSP count; however, credits are limited strictly to impressions verified as invalid by a qualified third-party IVT provider.\n\nWe kindly request that you share the third-party IVT report supporting the removed impressions. Only verified invalid traffic will be eligible for credit per contract terms. Please provide the documentation within 10 business days so we may resolve this matter promptly.\n\nThank you for your cooperation.\n\nApex Exchange Billing Operations",
      "proposed_adjustment_usd": 0.0
    }
  ]
}
```

## Task `apply_governance`


## Task `train_root_cause_model`

```json
{
  "mlflow_run_id": "1e36d1b795b94dcab49b94148739b243",
  "registered_model": "apex_recon.ml.discrepancy_root_cause",
  "version": 4,
  "alias": "champion",
  "train_rows": 1628,
  "holdout_rows": 543,
  "oot_rows": 2009,
  "holdout_model": {
    "accuracy": 0.8343,
    "macro_f1": 0.8433,
    "weighted_f1": 0.8329
  },
  "holdout_playbook": {
    "accuracy": 0.4733,
    "macro_f1": 0.4284,
    "weighted_f1": 0.4026
  },
  "oot_model": {
    "accuracy": 0.9487,
    "macro_f1": 0.9396,
    "weighted_f1": 0.9498
  },
  "oot_playbook": {
    "accuracy": 0.6909,
    "macro_f1": 0.4822,
    "weighted_f1": 0.6557
  },
  "oot_confusion_matrix": {
    "DEAL_ID_MISMAPPING": {
      "DEAL_ID_MISMAPPING": 116,
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
      "FX_MISMATCH": 101,
      "GENUINE_BILLING_ERROR": 0,
      "IVT_FILTERING": 0,
      "LATE_OR_MISSING_DATA": 0,
      "SSAI_BEACON_LOSS": 0,
      "TIMEZONE_SHIFT": 0,
      "WITHIN_TOLERANCE": 0
    },
    "GENUINE_BILLING_ERROR": {
      "DEAL_ID_MISMAPPING": 0,
      "FX_MISMATCH": 4,
      "GENUINE_BILLING_ERROR": 116,
      "IVT_FILTERING": 5,
      "LATE_OR_MISSING_DATA": 2,
      "SSAI_BEACON_LOSS": 1,
      "TIMEZONE_SHIFT": 0,
      "WITHIN_TOLERANCE": 9
    },
    "IVT_FILTERING": {
      "DEAL_ID_MISMAPPING": 0,
      "FX_MISMATCH": 0,
      "GENUINE_BILLING_ERROR": 1,
      "IVT_FILTERING": 181,
      "LATE_OR_MISSING_DATA": 0,
      "SSAI_BEACON_LOSS": 6,
      "TIMEZONE_SHIFT": 1,
      "WITHIN_TOLERANCE": 16
    },
    "LATE_OR_MISSING_DATA": {
      "DEAL_ID_MISMAPPING": 2,
      "FX_MISMATCH": 0,
      "GENUINE_BILLING_ERROR": 0,
      "IVT_FILTERING": 1,
      "LATE_OR_MISSING_DATA": 110,
      "SSAI_BEACON_LOSS": 0,
      "TIMEZONE_SHIFT": 0,
      "WITHIN_TOLERANCE": 27
    },
    "SSAI_BEACON_LOSS": {
      "DEAL_ID_MISMAPPING": 0,
      "FX_MISMATCH": 0,
      "GENUINE_BILLING_ERROR": 1,
      "IVT_FILTERING": 10,
      "LATE_OR_MISSING_DATA": 0,
      "SSAI_BEACON_LOSS": 205,
      "TIMEZONE_SHIFT": 1,
      "WITHIN_TOLERANCE": 4
    },
    "TIMEZONE_SHIFT": {
      "DEAL_ID_MISMAPPING": 0,
      "FX_MISMATCH": 0,
      "GENUINE_BILLING_ERROR": 0,
      "IVT_FILTERING": 0,
      "LATE_OR_MISSING_DATA": 0,
      "SSAI_BEACON_LOSS": 0,
      "TIMEZONE_SHIFT": 126,
      "WITHIN_TOLERANCE": 2
    },
    "WITHIN_TOLERANCE": {
      "DEAL_ID_MISMAPPING": 2,
      "FX_MISMATCH": 0,
      "GENUINE_BILLING_ERROR": 0,
      "IVT_FILTERING": 2,
      "LATE_OR_MISSING_DATA": 1,
      "SSAI_BEACON_LOSS": 0,
      "TIMEZONE_SHIFT": 5,
      "WITHIN_TOLERANCE": 951
    }
  },
  "oot_classification_report": "                       precision    recall  f1-score   support\n\n   DEAL_ID_MISMAPPING      1.000     0.967     0.983       120\n          FX_MISMATCH      1.000     0.962     0.981       105\nGENUINE_BILLING_ERROR      0.847     0.983     0.910       118\n        IVT_FILTERING      0.883     0.910     0.896       199\n LATE_OR_MISSING_DATA      0.786     0.973     0.870       113\n     SSAI_BEACON_LOSS      0.928     0.967     0.947       212\n       TIMEZONE_SHIFT      0.984     0.947     0.966       133\n     WITHIN_TOLERANCE      0.990     0.943     0.965      1009\n\n             accuracy                          0.949      2009\n            macro avg      0.927     0.956     0.940      2009\n         weighted avg      0.953     0.949     0.950      2009\n"
}
```
