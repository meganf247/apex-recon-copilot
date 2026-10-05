# Reconciliation Workbench: end-to-end app test

Headless Streamlit AppTest run of `app/app.py` against the live workspace (UC SQL warehouse, Lakebase `apex_ops`, Genie space). Command: `DATABRICKS_CONFIG_PROFILE=megan-fevm LAKEBASE_USER=<user> .venv/bin/python tests/app_smoke_test.py`

Run at: 2026-10-05 17:26 UTC

```
[ OK ] Close overview renders
        metrics: ['Gross CTV revenue (Apex) = $146,784,500', 'Billed per DSP reports = $137,516,882', 'Revenue at risk = $10,262,008', 'Cases open = 276', 'Recovered so far = $0']
[ OK ] Triage queue renders
         ['276 cases · $8,243,385 at risk · sorted by revenue at risk', 'Signed in as billing.analyst@apexexchange.example']
        selected CASE-2026-09-D00734: Onyx Programmatic · $215,006 at risk · model=IVT_FILTERING
[ OK ] Case detail renders (case opened -> IN_REVIEW in Lakebase)
         metrics: ['Apex impressions = 28,985,870', 'DSP impressions = 24,752,904', 'Revenue gap = $215,006', 'Contract threshold = 10.0%', 'Model root cause = Ivt Filtering']
         AI summary: CASE-2026-09-D00734: For deal D00734 (Beacon Classics · Sports · OPEN), September 2026, Apex recorded 28,985,870 impressions ($1,472,061.42) versus Onyx Programmatic's 24,752,904 impressions ($1,257,055.60)—a gap of 215,005.82 USD (14.61%), exceeding the 10% contract threshold. Billing basis is SSP;
[ OK ] Send dispute to partner
[ OK ] Resolve case with credit

Lakebase recon.dispute_cases:
             case_id   status    resolution confirmed_root_cause recovered_usd                                owner
CASE-2026-09-D00734 RESOLVED CREDIT_ISSUED        IVT_FILTERING          0.00 billing.analyst@apexexchange.example

Lakebase recon.case_events:
     event_type                                actor                                                                                                                               detail
       CREATED billing.analyst@apexexchange.example                                                                          {'confidence': 0.9997, 'model_root_cause': 'IVT_FILTERING'}
    EMAIL_SENT billing.analyst@apexexchange.example {'edited': False, 'subject': 'Billing Dispute – CASE-2026-09-D00734 | Deal D00734 Beacon Classics · Sports · OPEN | September 2026'}
STATUS_CHANGED billing.analyst@apexexchange.example  {'status': 'RESOLVED', 'resolution': 'CREDIT_ISSUED', 'model_root_cause': 'IVT_FILTERING', 'confirmed_root_cause': 'IVT_FILTERING'}

Lakebase recon.credit_approvals:
 amount_usd                          approved_by        reason
 215005.82 billing.analyst@apexexchange.example IVT_FILTERING
[ OK ] Ask Genie answers
         Genie: ['_You want to see the total revenue at risk for each partner team for the September 2026 billing month._\n\nFor the **September 2026 close**, total revenue at risk is highest for **Pacific** at **$5,279,803**, followed by **Central** at **$1,957,712**, **Atlantic** at **$1,624,705**, and **EMEA** at **$1,399,788**. Across the 4 partner teams shown, **Pacific** has the largest exposure and **EMEA** the smallest.', '### Apex Exchange\n**CTV Reconciliation Workbench**']

RESULT: PASS
```
