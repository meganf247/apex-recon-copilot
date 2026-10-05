# Job run evidence: [dev megan_fogal] apex-recon-build

- Run ID: `173832979162606`  
- Result: **SUCCESS**  
- Started: 2026-10-05 15:38:04 UTC  
- Ended: 2026-10-05 15:41:34 UTC  
- Run page: https://fevm-serverless-3dmees.cloud.databricks.com/?o=7474652285429726#job/602392988880313/run/173832979162606

| Task | Result | Duration (min) |
|---|---|---:|
| `generate_data` | DISABLED | 0.0 |
| `ingest_and_reconcile` | DISABLED | 0.0 |
| `train_root_cause_model` | DISABLED | 0.0 |
| `score_and_draft_disputes` | SUCCESS | 3.5 |

## Task `generate_data`


## Task `ingest_and_reconcile`

Pipeline `5d44a671-5813-463d-903e-33ca04bb3376`, update `b22496e9-3dfb-44ba-9e37-b8a8fc495095` → **COMPLETED**

Rows written and expectation results: see `evidence/02_pipeline_evidence.md`.

## Task `train_root_cause_model`


## Task `score_and_draft_disputes`

```json
{
  "model_version": 1,
  "deal_months_scored": 5518,
  "prediction_distribution": {
    "WITHIN_TOLERANCE": 2597,
    "IVT_FILTERING": 604,
    "SSAI_BEACON_LOSS": 597,
    "TIMEZONE_SHIFT": 495,
    "LATE_OR_MISSING_DATA": 353,
    "DEAL_ID_MISMAPPING": 318,
    "GENUINE_BILLING_ERROR": 282,
    "FX_MISMATCH": 272
  },
  "queue": {
    "2026-08": {
      "cases": 292,
      "usd": 6696212.0
    },
    "2026-07": {
      "cases": 342,
      "usd": 8145995.0
    },
    "2026-09": {
      "cases": 287,
      "usd": 7803163.0
    }
  },
  "genai_eval": {
    "drafts": 250,
    "parse_failures": 0,
    "dollars_grounded_rate": 1.0,
    "judge_sample": 30,
    "judge_mean": {
      "accuracy": 5.0,
      "tone": 5.0,
      "actionable": 5.0
    },
    "draft_model": "databricks-claude-sonnet-4-6",
    "judge_model": "databricks-gpt-5-4-mini"
  },
  "judge_issues": [
    {
      "case_id": "CASE-2026-09-D00382",
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
      "issue": "No material issues; email matches the evidence and makes a clear reconciliation request."
    },
    {
      "case_id": "CASE-2026-09-D00331",
      "accuracy": 5,
      "tone": 5,
      "actionable": 5,
      "issue": "Matches evidence closely; clear request to re-attribute impressions to the correct deal ID and confirm updated reporting."
    },
    {
      "case_id": "CASE-2026-09-D00050",
      "accuracy": 5,
      "tone": 5,
      "actionable": 5,
      "issue": "Matches evidence; clear request to re-attribute impressions to D00050 and confirm corrected report."
    },
    {
      "case_id": "CASE-2026-07-D00506",
      "accuracy": 5,
      "tone": 5,
      "actionable": 5,
      "issue": "None"
    },
    {
      "case_id": "CASE-2026-08-D00616",
      "accuracy": 5,
      "tone": 5,
      "actionable": 5,
      "issue": "No material issues; email matches evidence and makes a clear request."
    },
    {
      "case_id": "CASE-2026-08-D00107",
      "accuracy": 5,
      "tone": 5,
      "actionable": 5,
      "issue": "No material issues; matches evidence and asks partner to correct deal ID mapping and resubmit reconciled figures."
    },
    {
      "case_id": "CASE-2026-09-D00510",
      "accuracy": 5,
      "tone": 5,
      "actionable": 5,
      "issue": "No material issues; the email matches the evidence and clearly requests the missing report rows."
    },
    {
      "case_id": "CASE-2026-07-D00668",
      "accuracy": 5,
      "tone": 5,
      "actionable": 5,
      "issue": "No material issue; email matches evidence and asks partner to re-attribute impressions to the correct deal ID."
    },
    {
      "case_id": "CASE-2026-08-D00331",
      "accuracy": 5,
      "tone": 5,
      "actionable": 5,
      "issue": "No material issues; email matches the evidence and clearly requests next steps."
    }
  ],
  "sample_drafts": [
    {
      "case_id": "CASE-2026-07-D00007",
      "case_summary": "CASE-2026-07-D00007: For July 2026, Apex recorded 3,190,373 impressions ($176,119.91) on deal D00007 (Riverbend Sports Network \u00b7 Sports \u00b7 PMP) versus Vantage Demand's 2,551,341 impressions ($140,752.07) \u2014 a gap of 639,032 impressions and $35,367.84 (20.08%), far exceeding the 5.0% contract threshold. Timezone shift analysis shows 0-hour offset; 1 missing reporting day noted. Model classifies root cause as GENUINE_BILLING_ERROR with 1.0 confidence. Dispute recommended with log-level evidence.",
      "email_subject": "Formal Billing Dispute \u2013 Deal D00007 (Riverbend Sports Network \u00b7 Sports \u00b7 PMP) \u2013 July 2026 | CASE-2026-07-D00007",
      "email_body": "Dear Vantage Demand Billing Team,\n\nWe are writing regarding a material discrepancy identified on Deal D00007 (Riverbend Sports Network \u00b7 Sports \u00b7 PMP) for the July 2026 billing period.\n\nOur records show:\n\u2022 Apex impressions: 3,190,373 | Revenue: $176,119.91\n\u2022 Partner impressions: 2,551,341 | Revenue: $140,752.07\n\u2022 Gap: 639,032 impressions / $35,367.84 (20.08%)\n\nThis exceeds our contractual 5.0% discrepancy threshold. Timezone analysis returned a 0-hour offset, and no technical reconciliation factor has been identified. Our systems classify this as a genuine billing error with full model confidence.\n\nPer our agreement, billing is based on the DSP count; however, given the magnitude of this discrepancy, we are invoicing on the Apex count and have attached log-level impression evidence for your review.\n\nPlease confirm receipt and provide your reconciliation position within 5 business days. We are happy to schedule a call to resolve this promptly.\n\nBest regards,\nApex Exchange Billing Operations",
      "proposed_adjustment_usd": 35367.84
    },
    {
      "case_id": "CASE-2026-07-D00013",
      "case_summary": "Case CASE-2026-07-D00013: For billing month 2026-07, Apex Exchange recorded 4,651,844 impressions ($184,388.06) on deal D00013 (Cedar Vision \u00b7 News \u00b7 OPEN) versus Kestrel Demand's 4,021,546 impressions ($159,424.37), producing a $24,963.69 revenue gap (13.54%). This exceeds the 10.0% contractual threshold. No timezone shift or missing report days explain the discrepancy. Root cause is classified as GENUINE_BILLING_ERROR (model confidence: 1.0). Billing basis is SSP per contract. Dispute recommended with log-level evidence.",
      "email_subject": "Billing Dispute \u2013 Deal D00013 (Cedar Vision \u00b7 News \u00b7 OPEN) | July 2026 | $24,963.69 Discrepancy",
      "email_body": "Dear Kestrel Demand Billing Team,\n\nWe are writing regarding a material discrepancy identified on Deal D00013 (Cedar Vision \u00b7 News \u00b7 OPEN) for the July 2026 billing period.\n\nApex Exchange recorded 4,651,844 impressions totaling $184,388.06. Your records reflect 4,021,546 impressions totaling $159,424.37 \u2014 a gap of $24,963.69 (13.54%), which exceeds our contractual variance threshold of 10.0%.\n\nPer our agreement, the SSP count governs billing. We have reviewed all known reconciliation factors (timezone offsets, missing report days) and none account for this variance. Our analysis classifies this as a genuine billing error with full model confidence.\n\nWe respectfully request that Kestrel Demand reprocess the July 2026 invoice based on the Apex impression count of 4,651,844, resulting in a revised invoice of $184,388.06. Log-level impression evidence is attached for your review.\n\nPlease confirm receipt and provide a revised invoice within 10 business days. We are happy to schedule a reconciliation call if helpful.\n\nApex Exchange Billing Operations",
      "proposed_adjustment_usd": 24963.69
    },
    {
      "case_id": "CASE-2026-07-D00050",
      "case_summary": "CASE-2026-07-D00050: For July 2026, Apex recorded 8,713,062 impressions ($388,940.87) on deal D00050 (Cedar Play \u00b7 Sports \u00b7 PMP) versus Reachlytics' 6,975,983 impressions ($311,369.57), a gap of 1,737,079 impressions and $77,571.30 (19.94%). This exceeds the 7.5% contractual threshold. No timezone shift explains the discrepancy; one missing reporting day is noted. Model confidence is 100% GENUINE_BILLING_ERROR. Billing adjustment to Apex count is recommended with log-level evidence.",
      "email_subject": "Billing Dispute \u2013 CASE-2026-07-D00050 | Cedar Play \u00b7 Sports \u00b7 PMP (D00050) | July 2026 | $77,571.30 Discrepancy",
      "email_body": "Dear Reachlytics Billing Team,\n\nWe are writing regarding a material discrepancy identified on deal D00050 (Cedar Play \u00b7 Sports \u00b7 PMP) for the July 2026 billing period.\n\nOur records show:\n\u2022 Apex impressions: 8,713,062 | Revenue: $388,940.87\n\u2022 Reachlytics impressions: 6,975,983 | Revenue: $311,369.57\n\u2022 Gap: 1,737,079 impressions / $77,571.30 (19.94%)\n\nThis exceeds our contractual discrepancy threshold of 7.5%. Per our agreement, billing is based on the DSP count; however, the 19.94% variance cannot be attributed to a timezone offset or a single missing reporting day. Our system has classified this as a GENUINE_BILLING_ERROR with 100% model confidence.\n\nWe are therefore formally disputing the underpayment of $77,571.30 and request that Reachlytics reconcile against the Apex impression count. Log-level evidence is attached for your review.\n\nPlease confirm receipt and provide a revised invoice or written response within 10 business days.\n\nApex Exchange Billing Operations",
      "proposed_adjustment_usd": 77571.3
    }
  ]
}
```
