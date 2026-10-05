# Reconciliation Workbench: end-to-end app test

Headless Streamlit AppTest run of `app/app.py` against the live workspace (UC SQL warehouse, Lakebase `apex_ops`, Genie space). Command: `DATABRICKS_CONFIG_PROFILE=megan-fevm LAKEBASE_USER=<user> .venv/bin/python tests/app_smoke_test.py`

Run at: 2026-10-05 15:59 UTC

```
[ OK ] Close overview renders
        metrics: ['Gross CTV revenue (Apex) = $146,784,500', 'Billed per DSP reports = $138,522,816', 'Revenue at risk = $9,641,795', 'Cases open = 286', 'Recovered so far = $0']
[ OK ] Triage queue renders
         ['286 cases · $7,379,555 at risk · sorted by revenue at risk', 'Signed in as billing.analyst@apexexchange.example']
        selected CASE-2026-09-D00734: Onyx Programmatic · $139,101 at risk · model=IVT_FILTERING
[ OK ] Case detail renders (case opened -> IN_REVIEW in Lakebase)
         metrics: ['Apex impressions = 28,985,870', 'DSP impressions = 26,246,920', 'Revenue gap = $139,101', 'Contract threshold = 10.0%', 'Model root cause = Ivt Filtering']
         AI summary: For billing month 2026-09, Deal D00734 ('Beacon Classics · Sports · OPEN') shows a $139,101.47 (9.45%) revenue gap between Apex-recorded $1,472,061.42 and Onyx Programmatic's $1,332,959.95. The gap falls below the 10.0% contractual threshold. Model confidence is 1.0; predicted root cause is IVT filt
[ OK ] Send dispute to partner
[ OK ] Resolve case with credit

Lakebase recon.dispute_cases:
             case_id   status    resolution confirmed_root_cause recovered_usd                                owner
CASE-2026-09-D00734 RESOLVED CREDIT_ISSUED        IVT_FILTERING          0.00 billing.analyst@apexexchange.example

Lakebase recon.case_events:
     event_type                                actor                                                                                                                                   detail
       CREATED billing.analyst@apexexchange.example                                                                                 {'confidence': 1.0, 'model_root_cause': 'IVT_FILTERING'}
    EMAIL_SENT billing.analyst@apexexchange.example {'edited': False, 'subject': 'CASE-2026-09-D00734 | Revenue Discrepancy – Deal D00734 Beacon Classics · Sports · OPEN | September 2026'}
STATUS_CHANGED billing.analyst@apexexchange.example      {'status': 'RESOLVED', 'resolution': 'CREDIT_ISSUED', 'model_root_cause': 'IVT_FILTERING', 'confirmed_root_cause': 'IVT_FILTERING'}

Lakebase recon.credit_approvals:
 amount_usd                          approved_by        reason
 139101.47 billing.analyst@apexexchange.example IVT_FILTERING
[ OK ] Ask Genie answers
         Genie: ['_You want to see the total revenue at risk for each partner team for the September 2026 billing month._\n\nFor the **2026-09** close, total revenue at risk by partner team is **Pacific: $5,262,297**, **EMEA: $1,735,947**, **Central: $1,486,534**, and **Atlantic: $1,157,016**. **Pacific** has the highest exposure, and its revenue at risk is more than **3x** **Atlantic**, the lowest of the four teams.', '### Apex Exchange\n**CTV Reconciliation Workbench**']

RESULT: PASS
```
