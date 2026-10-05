# Job run evidence: [dev megan_fogal] apex-recon-build

- Run ID: `543640873218992`  
- Result: **FAILED**  
- Started: 2026-10-05 17:08:42 UTC  
- Ended: 2026-10-05 17:23:06 UTC  
- Run page: https://fevm-serverless-3dmees.cloud.databricks.com/?o=7474652285429726#job/602392988880313/run/543640873218992

| Task | Result | Duration (min) |
|---|---|---:|
| `generate_data` | SUCCESS | 6.3 |
| `ingest_and_reconcile` | SUCCESS | 2.1 |
| `apply_governance` | FAILED | 0.1 |
| `sync_case_status_to_uc` | SUCCESS | 0.9 |
| `refresh_lakebase_queue` | SUCCESS | 0.5 |
| `train_root_cause_model` | SUCCESS | 1.2 |
| `score_and_draft_disputes` | SUCCESS | 3.4 |

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

Pipeline `5d44a671-5813-463d-903e-33ca04bb3376`, update `308849b7-1c8c-4722-ac18-8aa501d96148` → **COMPLETED**

Rows written and expectation results: see `evidence/02_pipeline_evidence.md`.

## Task `apply_governance`

```

[COLUMN_ALIASES_NOT_ALLOWED] Column aliases are not allowed in MERGE. SQLSTATE: 42601
== SQL (line 2, position 1) ==
MERGE INTO apex_recon.ops.recon_access t
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
USING (VALUES ('megan.fogal@databricks.com',       '*',        TRUE),    -- Finance lead (build owner)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
              ('pm.atlantic@apexexchange.example', 'Atlantic', FALSE),   -- partner manager, Atlantic team
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
              ('pm.emea@apexexchange.example',     'EMEA',     FALSE)    -- partner manager, EMEA team
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      ) AS s(principal, partner_team, can_see_revenue)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ON t.principal = s.principal
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
WHEN MATCHED THEN UPDATE SET * WHEN NOT MATCHED THEN INSERT *
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


```

## Task `sync_case_status_to_uc`

```json
{
  "rows_snapshotted": {
    "dispute_cases": 0,
    "case_events": 0,
    "credit_approvals": 0
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
      "credited_usd": 139101.0
    }
  ]
}
```

## Task `refresh_lakebase_queue`

Pipeline `248ca05a-ee23-46ed-a2c0-0e442bd0434b`, update `e44e1cbe-9fd8-40eb-8ab3-f5d77e9e8c59` → **COMPLETED**

Rows written and expectation results: see `evidence/02_pipeline_evidence.md`.

## Task `train_root_cause_model`

```json
{
  "mlflow_run_id": "a4f76315034c4865926697bd6b1e7922",
  "registered_model": "apex_recon.ml.discrepancy_root_cause",
  "version": 2,
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

## Task `score_and_draft_disputes`

```json
{
  "model_version": 2,
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
    "contract_consistent_rate": 0.988,
    "judge_sample": 30,
    "judge_mean": {
      "accuracy": 4.9,
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
      "issue": "Matches evidence; clear DSP restatement request and professional tone."
    },
    {
      "case_id": "CASE-2026-07-D00234",
      "accuracy": 5,
      "tone": 5,
      "actionable": 5,
      "issue": "Matches evidence; clear request to restate corrected counts under DSP basis."
    },
    {
      "case_id": "CASE-2026-09-D00227",
      "accuracy": 5,
      "tone": 5,
      "actionable": 5,
      "issue": "None"
    },
    {
      "case_id": "CASE-2026-07-D00616",
      "accuracy": 5,
      "tone": 5,
      "actionable": 5,
      "issue": "None"
    },
    {
      "case_id": "CASE-2026-08-D00382",
      "accuracy": 5,
      "tone": 5,
      "actionable": 5,
      "issue": "Matches evidence; asks for restatement at contract FX rate and payment at Apex count under SSP basis."
    },
    {
      "case_id": "CASE-2026-09-D00586",
      "accuracy": 5,
      "tone": 5,
      "actionable": 5,
      "issue": "No material issues; matches SSP basis and evidence."
    },
    {
      "case_id": "CASE-2026-09-D00528",
      "accuracy": 5,
      "tone": 5,
      "actionable": 5,
      "issue": "Matches evidence; asks for missing rows and payment at Apex count under SSP basis."
    },
    {
      "case_id": "CASE-2026-08-D00616",
      "accuracy": 5,
      "tone": 5,
      "actionable": 5,
      "issue": "Matches evidence; clear SSP-basis ask and proposed next steps."
    },
    {
      "case_id": "CASE-2026-08-D00613",
      "accuracy": 2,
      "tone": 5,
      "actionable": 4,
      "issue": "Conflicts with SSP basis by asking for a split of the gap instead of stating Apex count stands and requesting payment at Apex count"
    },
    {
      "case_id": "CASE-2026-07-D00538",
      "accuracy": 5,
      "tone": 5,
      "actionable": 5,
      "issue": "No material issues; aligns with evidence and correctly asks the partner to restate the report for a DSP-billed deal."
    }
  ],
  "sample_drafts": [
    {
      "case_id": "CASE-2026-07-D00005",
      "case_summary": "Deal D00005 (Clearwater Play \u00b7 Sports \u00b7 OPEN) shows a 10.14% revenue gap for July 2026: Apex counted 18,495,364 impressions ($855,826.25) vs. Lattice Media's 16,635,061 ($769,065.79), a $86,760.46 shortfall exceeding the 7.5% contract threshold. Root cause is SSAI beacon loss (model confidence 99%). Billing basis is SSP; Apex count governs. Lattice Media must pay the full Apex invoice.",
      "email_subject": "Billing Dispute \u2013 Deal D00005 Clearwater Play \u00b7 Sports \u00b7 OPEN | July 2026 | Action Required",
      "email_body": "Dear Lattice Media Team,\n\nWe are writing regarding a discrepancy identified on Deal D00005 (Clearwater Play \u00b7 Sports \u00b7 OPEN) for the July 2026 billing period.\n\nApex recorded 18,495,364 impressions ($855,826.25), while your report reflects 16,635,061 impressions ($769,065.79) \u2014 a gap of $86,760.46 (10.14%), which exceeds the contractual 7.5% threshold.\n\nOur analysis indicates the root cause is SSAI beacon loss (model confidence: 99%). Under our agreement, the SSP count governs billing; accordingly, the invoice stands at $855,826.25.\n\nTo resolve this, we ask that you:\n1. Pay the invoice at the Apex-counted amount of $855,826.25.\n2. Review the attached Apex SSAI beacon logs.\n3. Open a ticket with your SSAI vendor to remediate the beacon loss going forward.\n\nPlease confirm receipt and your intended payment timeline at your earliest convenience. We are happy to schedule a call to walk through the logs.\n\nApex Exchange Billing Operations",
      "proposed_adjustment_usd": 0.0
    },
    {
      "case_id": "CASE-2026-07-D00006",
      "case_summary": "CASE-2026-07-D00006 | Sable Buy | Deal D00006 (Harborview Now \u00b7 News \u00b7 PG) | July 2026. Apex recorded 16,503,726 impressions ($754,371.43); partner reported 12,787,239 impressions ($584,415.42), a gap of 169,956.01 (22.53%), exceeding the 7.5% contract threshold. Root cause: 6 days of data are missing from the partner's report. Billing basis is SSP; Apex count governs. No invoice adjustment warranted. Partner must pay the Apex-counted invoice in full.",
      "email_subject": "Billing Dispute \u2013 CASE-2026-07-D00006 | Deal D00006 Harborview Now \u00b7 News \u00b7 PG | July 2026 | Missing Reporting Days",
      "email_body": "Dear Sable Buy Billing Team,\n\nWe are writing regarding a discrepancy identified on Deal D00006 (Harborview Now \u00b7 News \u00b7 PG) for the July 2026 billing period.\n\nApex Exchange recorded 16,503,726 impressions totaling $754,371.43. Your report reflects 12,787,239 impressions totaling $584,415.42 \u2014 a gap of $169,956.01 (22.53%), which materially exceeds the contractual 7.5% variance threshold.\n\nOur analysis indicates that 6 days of data are absent from your submission. As this deal operates on an SSP billing-count basis, Apex's impression count governs under the contract. Accordingly, the invoice stands at $754,371.43 and no adjustment will be applied.\n\nWe kindly request that you:\n1. Submit the missing 6 days' report rows for reconciliation purposes.\n2. Remit payment in full at the invoiced amount of $754,371.43.\n\nPlease respond within 5 business days. We are happy to provide our impression-level logs to assist your review.\n\nBest regards,\nApex Exchange Billing Operations",
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
