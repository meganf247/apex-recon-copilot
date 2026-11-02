# Job run evidence: [dev megan_fogal] apex-recon-build

- Run ID: `542978415804640`  
- Result: **SUCCESS**  
- Started: 2026-11-02 15:48:50 UTC  
- Ended: 2026-11-02 15:56:39 UTC  
- Run page: https://fevm-megant-fevm.cloud.databricks.com/?o=7474649371849429#job/800507315624085/run/542978415804640

| Task | Result | Duration (min) |
|---|---|---:|
| `ml_and_disputes` | SUCCESS | 3.7 |
| `generate_data` | SUCCESS | 2.4 |
| `pipeline` | SUCCESS | 1.4 |
| `publish` | SUCCESS | 0.3 |

Each notebook task's full cell-by-cell output is in `evidence/notebook_runs/`.

## Task `ml_and_disputes`

```json
{
  "model_version": 10,
  "model_results": {
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
  },
  "queue": {
    "2026-08": {
      "cases": 257,
      "usd": 6698764.0,
      "apex_exposure_usd": 3366663.0
    },
    "2026-07": {
      "cases": 239,
      "usd": 4636200.0,
      "apex_exposure_usd": 2262746.0
    },
    "2026-09": {
      "cases": 219,
      "usd": 6778508.0,
      "apex_exposure_usd": 3294686.0
    }
  },
  "genai": {
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
  },
  "lakebase_sync": "refresh started (pipeline 48cbab11-7eab-4c56-90ea-ec35cee07631)",
  "sample_drafts": [
    {
      "case_id": "CASE-2026-07-D00015",
      "case_summary": "CASE-2026-07-D00015: Ember Ads (Deal D00015, Summit News Live \u00b7 Sports \u00b7 OPEN) shows a $34,563.45 (9.33%) revenue gap for July 2026, exceeding the 7.5% contract threshold. Apex recorded 7,886,882 impressions vs. Ember Ads' 7,153,576. Billing basis is DSP. Predicted root cause is late/missing data; partner report is missing 2 days. Resolution requires Ember Ads to submit the missing report days for full reconciliation.",
      "email_body": "Dear Ember Ads Billing Team,\n\nWe are writing regarding a discrepancy identified for Deal D00015 (Summit News Live \u00b7 Sports \u00b7 OPEN) for the billing period July 2026.\n\nOur review shows the following:\n- Apex Impressions: 7,886,882\n- Ember Ads Reported Impressions: 7,153,576\n- Apex Revenue: $370,386.36\n- Ember Ads Reported Revenue: $335,822.91\n- Revenue Gap: $34,563.45 (9.33%)\n\nThis gap exceeds the contractual threshold of 7.5%. As billing is governed by DSP counts, we have identified that your report appears to be missing 2 days of data, which we believe is the primary driver of this discrepancy.\n\nWe kindly ask that you submit the missing report days so that we can complete reconciliation and finalize the invoice accordingly.\n\nPlease respond at your earliest convenience. We are happy to assist in resolving this promptly.\n\nBest regards,\nApex Exchange Billing Operations"
    },
    {
      "case_id": "CASE-2026-07-D00017",
      "case_summary": "CASE-2026-07-D00017: For deal D00017 (Lakeshore Stream \u00b7 Entertainment \u00b7 PG), Kestrel Demand reported 4,431,012 impressions vs. Apex's 5,199,466\u2014a gap of 768,454 impressions driving a $27,869.76 (14.78%) revenue shortfall against a 10.0% contract threshold. Billing basis is DSP. Predicted root cause is IVT filtering (confidence: 100%). No missing report days. Partner must provide third-party IVT documentation; only verified IVT will be credited.",
      "email_body": "Dear Kestrel Demand Billing Team,\n\nWe are writing regarding a discrepancy identified for Deal D00017 (Lakeshore Stream \u00b7 Entertainment \u00b7 PG) for the billing period July 2026.\n\nApex recorded 5,199,466 impressions ($188,572.42), while your report reflects 4,431,012 impressions ($160,702.66)\u2014a revenue gap of $27,869.76 (14.78%), which exceeds our contractual threshold of 10.0%.\n\nOur analysis indicates the likely root cause is IVT filtering applied on your side. As billing is governed by DSP count, we require supporting documentation to evaluate any adjustment.\n\nAction Required: Please share the third-party IVT report substantiating the impressions removed from your count. Only impressions verified as IVT through a recognized third-party provider will be eligible for credit.\n\nKindly provide the documentation within 5 business days. We are happy to discuss further if needed.\n\nBest regards,\nApex Exchange Billing Operations"
    }
  ]
}
```

## Task `generate_data`

```json
{
  "ssp_log_rows": 3565876,
  "impressions": 31506213513,
  "gross_revenue_usd": 1132630952.61,
  "dsp_report_rows": 158242,
  "dsp_report_files": 360,
  "bad_rows_injected": {
    "missing_deal_id": 631,
    "negative_impressions": 290,
    "bad_date": 330,
    "duplicate_rows": 481
  },
  "deal_months": 5562,
  "root_causes": {
    "WITHIN_TOLERANCE": 3723,
    "IVT_FILTERING": 737,
    "LATE_OR_MISSING_DATA": 398,
    "GENUINE_BILLING_ERROR": 392,
    "TIMEZONE_SHIFT": 312
  },
  "with_secondary_cause": 779,
  "history_cases": 1615,
  "history_label_noise": 0.11
}
```

## Task `pipeline`

Pipeline `7e5bc896-605c-44f6-a2e3-039922e893a9`, update `90e3d1f4-9919-4d1e-88ab-395affd8f930` → **COMPLETED**

Rows written and expectation results: see `evidence/02_pipeline_evidence.md`.

## Task `publish`

SQL file `/Workspace/Users/megan.fogal@databricks.com/apex-recon-copilot/src/04_publish.sql` ran on warehouse `93d767746e247a90` (SQL tasks return no notebook output).

What it applied, queried after the run: `evidence/04_publish_check.md` (row filter, masks, tags, view); `evidence/05_governance_demo.md` (the filter and masks in action); `evidence/08_lakebase_live_status.md` (the live view over Lakebase).
