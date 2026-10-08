# Job run evidence: [dev megan_fogal] apex-recon-build

- Run ID: `600343157910371`  
- Result: **SUCCESS**  
- Started: 2026-10-07 15:23:59 UTC  
- Ended: 2026-10-07 15:32:51 UTC  
- Run page: https://fevm-megant-fevm.cloud.databricks.com/?o=7474649371849429#job/800507315624085/run/600343157910371

| Task | Result | Duration (min) |
|---|---|---:|
| `ml_and_disputes` | SUCCESS | 4.2 |
| `generate_data` | SUCCESS | 2.9 |
| `pipeline` | SUCCESS | 1.4 |
| `publish` | SUCCESS | 0.3 |

Each notebook task's full cell-by-cell output is in `evidence/notebook_runs/`.

## Task `ml_and_disputes`

```json
{
  "model_version": 6,
  "model_results": {
    "holdout_vs_analyst_labels": {
      "model": {
        "accuracy": 0.8317,
        "macro_f1": 0.8239
      },
      "playbook": {
        "accuracy": 0.651,
        "macro_f1": 0.5572
      }
    },
    "jul_sep_vs_true_cause": {
      "model": {
        "accuracy": 0.9481,
        "macro_f1": 0.9184
      },
      "playbook": {
        "accuracy": 0.8212,
        "macro_f1": 0.5797
      }
    }
  },
  "queue": {
    "2026-08": {
      "cases": 257,
      "usd": 6698764.0
    },
    "2026-07": {
      "cases": 239,
      "usd": 4636200.0
    },
    "2026-09": {
      "cases": 219,
      "usd": 6778508.0
    }
  },
  "genai": {
    "drafts": 250,
    "parse_failures": 0,
    "dollars_grounded_rate": 1.0,
    "contract_consistent_rate": 1.0,
    "judge_mean_n30": {
      "accuracy": 4.8,
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
      "case_summary": "CASE-2026-07-D00015: Ember Ads (Deal D00015, Summit News Live \u00b7 Sports \u00b7 OPEN) shows a $34,563.45 (9.33%) revenue gap for July 2026, exceeding the 7.5% contract threshold. Apex recorded 7,886,882 impressions vs. Ember Ads' 7,153,576. Billing basis is DSP. Root cause is predicted as late/missing data (0.93 confidence) with 2 days absent from the partner report. No adjustment is proposed pending receipt of the missing report days.",
      "email_body": "Dear Ember Ads Billing Team,\n\nWe are writing regarding a discrepancy identified for Deal D00015 (Summit News Live \u00b7 Sports \u00b7 OPEN) for the billing period July 2026.\n\nOur review shows the following:\n\u2022 Apex impressions: 7,886,882\n\u2022 Ember Ads reported impressions: 7,153,576\n\u2022 Apex revenue: $370,386.36\n\u2022 Ember Ads reported revenue: $335,822.91\n\u2022 Revenue gap: $34,563.45 (9.33%), exceeding the contractual 7.5% threshold\n\nOur analysis indicates that 2 days are missing from your submitted report, which we believe accounts for the discrepancy. As billing is governed by DSP counts under our agreement, we require your complete and corrected report before the invoice can be finalized.\n\nPlease provide the missing 2 report days at your earliest convenience so we can reconcile and close this billing period promptly.\n\nThank you for your cooperation. Please do not hesitate to contact us with any questions.\n\nApex Exchange Billing Operations"
    },
    {
      "case_id": "CASE-2026-07-D00017",
      "case_summary": "CASE-2026-07-D00017: For deal D00017 (Lakeshore Stream \u00b7 Entertainment \u00b7 PG), Kestrel Demand reported 4,431,012 impressions vs. Apex's 5,199,466\u2014a gap of 768,454 impressions (14.78%), exceeding the 10.0% contract threshold. Revenue gap is $27,869.76 ($188,572.42 vs. $160,702.66). Billing basis is DSP; predicted root cause is IVT filtering (confidence: 100%). Partner must provide third-party IVT documentation before any credit is considered.",
      "email_body": "Dear Kestrel Demand Billing Team,\n\nWe are writing regarding a discrepancy identified for Deal D00017 (Lakeshore Stream \u00b7 Entertainment \u00b7 PG) for the billing period July 2026.\n\nApex recorded 5,199,466 impressions ($188,572.42), while your report reflects 4,431,012 impressions ($160,702.66), producing a revenue gap of $27,869.76 (14.78%). This exceeds our contractual variance threshold of 10.0%.\n\nOur analysis indicates the likely root cause is IVT filtering applied on your side. As this deal is governed by DSP-side counts, we require your corrected report and the supporting third-party IVT verification documentation for all removed impressions. Only impressions confirmed as invalid via a recognized third-party IVT provider will be eligible for credit consideration.\n\nPlease provide the third-party IVT report within 10 business days. We will review the documentation and determine the verified credit amount accordingly. No adjustment will be applied absent this supporting evidence.\n\nThank you for your prompt attention.\n\nApex Exchange Billing Operations"
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

Pipeline `7e5bc896-605c-44f6-a2e3-039922e893a9`, update `c768f685-57f4-4a94-b96b-5c32d8a87357` → **COMPLETED**

Rows written and expectation results: see `evidence/02_pipeline_evidence.md`.

## Task `publish`

SQL file `/Workspace/Users/megan.fogal@databricks.com/apex-recon-copilot/src/04_publish.sql` ran on warehouse `93d767746e247a90` (SQL tasks return no notebook output).

What it applied, queried after the run: `evidence/04_publish_check.md` (row filter, masks, tags, view); `evidence/05_governance_demo.md` (the filter and masks in action); `evidence/08_lakebase_live_status.md` (the live view over Lakebase).
