# Reconciliation Workbench: end-to-end app test

Headless Streamlit AppTest run of `app/app.py` against the live workspace (UC SQL warehouse, Lakebase project `apex-recon-lb`, Genie space). Command: `DATABRICKS_CONFIG_PROFILE=<profile> LAKEBASE_USER=<user> .venv/bin/python tests/app_smoke_test.py`

Run at: 2026-11-02 16:07 UTC

```
[ OK ] Close overview renders
        metrics: ['Gross CTV spend (Apex count) = $153,526,858', 'Billed per DSP reports = $144,607,996', 'Billing shortfall (all deals) = $8,918,862', 'Revenue at risk (review queue) = $6,778,508', 'Apex net exposure = $3,294,686', 'Recovered so far = $0']
[ OK ] Triage queue renders
         ['219 cases · $6,778,508 at risk · sorted by revenue at risk', 'Signed in as billing.analyst@apexexchange.example']
        selected CASE-2026-09-D00422: Ironwood Ads · $349,977 at risk · model=IVT_FILTERING
[ OK ] Case detail renders (case opened -> IN_REVIEW in Lakebase)
         metrics: ['Apex impressions = 35,581,129', 'DSP impressions = 27,479,471', 'Revenue gap = $349,977', 'Contract threshold = 7.5%', 'Apex net exposure = $349,977']
         AI summary: CASE-2026-09-D00422: For deal D00422 (Lakeshore Cast · Sports · PMP), September 2026, Ironwood Ads reported 27,479,471 impressions vs. Apex's 35,581,129 — a 22.8% revenue gap ($349,977.00), well above the 7.5% contract threshold. Billing basis is DSP. Root cause is predicted IVT filtering (confidenc
[ OK ] Send dispute to partner
        verified IVT credit $209,986.20 · recovering the unverified $139,990.80
[ OK ] Resolve case: credit verified IVT, recover the remainder
Lakebase recon.dispute_cases:
             case_id   status    resolution confirmed_root_cause recovered_usd                                owner
CASE-2026-09-D00422 RESOLVED CREDIT_ISSUED        IVT_FILTERING     139990.80 billing.analyst@apexexchange.example
Lakebase recon.case_events:
     event_type                                actor                                                                                                                                                                                   detail
       CREATED billing.analyst@apexexchange.example                                                                                                                                 {'confidence': 1.0, 'model_root_cause': 'IVT_FILTERING'}
    EMAIL_SENT billing.analyst@apexexchange.example                                                       {'edited': False, 'subject': 'Billing Dispute – CASE-2026-09-D00422 | Deal D00422 Lakeshore Cast · Sports · PMP | September 2026'}
STATUS_CHANGED billing.analyst@apexexchange.example {'status': 'RESOLVED', 'resolution': 'CREDIT_ISSUED', 'credited_usd': 209986.2, 'recovered_usd': 139990.8, 'model_root_cause': 'IVT_FILTERING', 'confirmed_root_cause': 'IVT_FILTERING'}
Lakebase recon.credit_approvals:
 amount_usd                          approved_by        reason
 209986.20 billing.analyst@apexexchange.example IVT_FILTERING
[ OK ] Ask Genie answers
         Genie: ['_You want to see the total revenue at risk for each partner team for the September 2026 billing month._\n\nFor the **September 2026** close, total **revenue at risk** by partner team is:\n- **Central:** **$2,880,825**\n- **Pacific:** **$1,790,123**\n- **Atlantic:** **$1,583,516**\n- **EMEA:** **$524,044**\nAcross the 4 teams shown, **Central** has the highest revenue at risk and **EMEA** the lowest.', '### Apex Exchange\n**CTV Reconciliation Workbench**']
RESULT: PASS
```
