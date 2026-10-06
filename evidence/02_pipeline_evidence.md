
```sql
SELECT origin.flow_name AS dataset,
       max(details:flow_progress.metrics.num_output_rows::BIGINT) AS output_rows,
       max(details:flow_progress.data_quality.dropped_records::BIGINT) AS dropped_by_expectations
FROM event_log('7e5bc896-605c-44f6-a2e3-039922e893a9')
WHERE event_type = 'flow_progress' AND details:flow_progress.status = 'COMPLETED'
  AND origin.update_id = (SELECT origin.update_id FROM event_log('7e5bc896-605c-44f6-a2e3-039922e893a9')
                          WHERE event_type = 'create_update' ORDER BY timestamp DESC LIMIT 1)
GROUP BY 1 ORDER BY 1
```
| dataset | output_rows | dropped_by_expectations |
|---|---|---|
| apex_recon.bronze.dispute_resolutions |  |  |
| apex_recon.bronze.dsp_reports_format_a |  |  |
| apex_recon.bronze.dsp_reports_format_b |  |  |
| apex_recon.bronze.dsp_reports_format_c |  |  |
| apex_recon.bronze.publisher_adserver_reports |  |  |
| apex_recon.bronze.ssp_auction_logs |  |  |
| apex_recon.gold.publisher_recon_month | 1336 | 0 |
| apex_recon.gold.recon_deal_daily | 158959 | 0 |
| apex_recon.gold.recon_deal_month | 5517 | 0 |
| apex_recon.gold.recon_partner_month | 351 | 0 |
| apex_recon.ml.discrepancy_features | 5517 | 0 |
| apex_recon.silver.dim_deals | 800 | 0 |
| apex_recon.silver.dim_dsps | 40 | 0 |
| apex_recon.silver.dim_publishers | 150 | 0 |
| apex_recon.silver.dispute_history | 2171 | 0 |
| apex_recon.silver.dsp_daily_reports | 156418 | 1725 |
| apex_recon.silver.dsp_reports_quarantine | 1725 | 0 |
| apex_recon.silver.fx_rates | 546 | 0 |
| apex_recon.silver.publisher_daily_reports | 158703 | 0 |
| apex_recon.silver.ssp_hourly |  |  |

```sql
SELECT origin.flow_name AS dataset, e.name AS expectation,
       sum(e.passed_records) AS passed_records, sum(e.failed_records) AS failed_records
FROM event_log('7e5bc896-605c-44f6-a2e3-039922e893a9'),
     LATERAL explode(from_json(details:flow_progress.data_quality.expectations,
                     'array<struct<name:string,dataset:string,passed_records:bigint,failed_records:bigint>>')) AS t(e)
WHERE event_type = 'flow_progress' AND details:flow_progress.data_quality.expectations IS NOT NULL
  AND origin.update_id = (SELECT origin.update_id FROM event_log('7e5bc896-605c-44f6-a2e3-039922e893a9')
                          WHERE event_type = 'create_update' ORDER BY timestamp DESC LIMIT 1)
GROUP BY 1, 2 ORDER BY 1, 2
```
| dataset | expectation | passed_records | failed_records |
|---|---|---|---|
| apex_recon.silver.dispute_history | has_label | 2171 | 0 |
| apex_recon.silver.dsp_daily_reports | known_deal | 157538 | 605 |
| apex_recon.silver.dsp_daily_reports | non_negative_impressions | 157822 | 321 |
| apex_recon.silver.dsp_daily_reports | not_duplicate | 157694 | 449 |
| apex_recon.silver.dsp_daily_reports | seat_matches_partner | 158111 | 32 |
| apex_recon.silver.dsp_daily_reports | valid_amount | 158143 | 0 |
| apex_recon.silver.dsp_daily_reports | valid_report_date | 157819 | 324 |
| apex_recon.silver.publisher_daily_reports | non_negative_impressions | 158703 | 0 |
| apex_recon.silver.publisher_daily_reports | valid_report_date | 158703 | 0 |
| apex_recon.silver.ssp_hourly | has_deal | 3541306 | 0 |
| apex_recon.silver.ssp_hourly | valid_impressions | 3541306 | 0 |

```sql
SELECT r AS failed_rule, count(*) AS rows
FROM apex_recon.silver.dsp_reports_quarantine LATERAL VIEW explode(failed_rules) x AS r
GROUP BY r ORDER BY rows DESC
```
| failed_rule | rows |
|---|---|
| known_deal | 605 |
| not_duplicate | 449 |
| valid_report_date | 324 |
| non_negative_impressions | 321 |
| seat_matches_partner | 32 |

```sql
SELECT dsp_id, source_format, report_date, deal_id, impressions, amount_native, failed_rules, _source_file
FROM apex_recon.silver.dsp_reports_quarantine ORDER BY dsp_id, _source_file LIMIT 10
```
| dsp_id | source_format | report_date | deal_id | impressions | amount_native | failed_rules | _source_file |
|---|---|---|---|---|---|---|---|
| DSP001 | A | 2026-01-20 | D00510 | 423394 | 17037.28 | ["not_duplicate"] | /Volumes/apex_recon/landing/raw/dsp_reports/DSP001/DSP001_billing_2026-01.csv |
| DSP001 | A | 2026-01-03 |  | 373859 | 11778.51 | ["known_deal"] | /Volumes/apex_recon/landing/raw/dsp_reports/DSP001/DSP001_billing_2026-01.csv |
| DSP001 | A | 2026-02-24 | D00325 | 66832 | 2403.16 | ["not_duplicate"] | /Volumes/apex_recon/landing/raw/dsp_reports/DSP001/DSP001_billing_2026-02.csv |
| DSP001 | A | 2026-02-08 | D00185 | -136485 | 7902.87 | ["non_negative_impressions"] | /Volumes/apex_recon/landing/raw/dsp_reports/DSP001/DSP001_billing_2026-02.csv |
| DSP001 | A |  | D00185 | 104900 | 6058.92 | ["valid_report_date"] | /Volumes/apex_recon/landing/raw/dsp_reports/DSP001/DSP001_billing_2026-02.csv |
| DSP001 | A | 2026-03-19 | D00749 | 56376 | 2189.88 | ["not_duplicate"] | /Volumes/apex_recon/landing/raw/dsp_reports/DSP001/DSP001_billing_2026-03.csv |
| DSP001 | A | 2026-04-16 |  | 50664 | 1791.45 | ["known_deal"] | /Volumes/apex_recon/landing/raw/dsp_reports/DSP001/DSP001_billing_2026-04.csv |
| DSP001 | A | 2026-04-19 | D00185 | 107463 | 6208.6 | ["not_duplicate"] | /Volumes/apex_recon/landing/raw/dsp_reports/DSP001/DSP001_billing_2026-04.csv |
| DSP001 | A |  | D00185 | 92030 | 5271.02 | ["valid_report_date"] | /Volumes/apex_recon/landing/raw/dsp_reports/DSP001/DSP001_billing_2026-05.csv |
| DSP001 | A | 2026-05-27 | D00090 | 65665 | 2197.51 | ["not_duplicate"] | /Volumes/apex_recon/landing/raw/dsp_reports/DSP001/DSP001_billing_2026-05.csv |

```sql
SELECT source_format, currency, count(*) AS rows, count(DISTINCT dsp_id) AS dsps,
       round(sum(amount_native), 2) AS amount_native, round(sum(amount_usd), 2) AS amount_usd
FROM apex_recon.silver.dsp_daily_reports GROUP BY 1, 2 ORDER BY 1, 2
```
| source_format | currency | rows | dsps | amount_native | amount_usd |
|---|---|---|---|---|---|
| A | USD | 98123 | 19 | 6.402110199E8 | 6.402110199E8 |
| B | EUR | 20380 | 4 | 1.1778840049E8 | 1.2310293093E8 |
| B | GBP | 4582 | 2 | 2.002070145E7 | 2.481683502E7 |
| B | USD | 19906 | 7 | 1.4081890771E8 | 1.4081890771E8 |
| C | USD | 13427 | 7 | 1.102215722E8 | 1.102215722E8 |

```sql
SELECT dsp_name, partner_team, active_deals, deals_needing_review, ssp_revenue_usd, dsp_revenue_usd,
       revenue_gap_pct, discrepancy_threshold_pct, over_threshold, revenue_at_risk_usd
FROM apex_recon.gold.recon_partner_month WHERE billing_month = '2026-09'
ORDER BY revenue_at_risk_usd DESC LIMIT 10
```
| dsp_name | partner_team | active_deals | deals_needing_review | ssp_revenue_usd | dsp_revenue_usd | revenue_gap_pct | discrepancy_threshold_pct | over_threshold | revenue_at_risk_usd |
|---|---|---|---|---|---|---|---|---|---|
| Lattice Media | Pacific | 141 | 56 | 3.31845132E7 | 3.138343326E7 | 5.427 | 7.5 | false | 2090964.19 |
| Sable Buy | Pacific | 34 | 23 | 9922770.65 | 8829309.66 | 11.02 | 7.5 | true | 1093460.99 |
| Mosaic Bid | EMEA | 68 | 30 | 1.596595355E7 | 1.514741239E7 | 5.127 | 7.5 | false | 818541.16 |
| Onyx Programmatic | Pacific | 9 | 8 | 3769469.58 | 3396589.27 | 9.892 | 10.0 | false | 475464.08 |
| Willow Demand | Central | 10 | 4 | 2623124.28 | 2513108.93 | 4.194 | 5.0 | false | 445669.45 |
| Kestrel Demand | Atlantic | 18 | 15 | 3324111.65 | 2926576.48 | 11.959 | 10.0 | true | 426625.68 |
| Cobalt Ads | Pacific | 27 | 7 | 7109842.38 | 6686294.32 | 5.957 | 10.0 | false | 423548.06 |
| Summit Audience | Pacific | 32 | 8 | 7526808.52 | 7193304.55 | 4.431 | 10.0 | false | 405327.63 |
| Redwood Demand | Central | 14 | 3 | 5338174.36 | 4945092.28 | 7.364 | 5.0 | true | 393082.08 |
| Bluefin Media | Central | 29 | 8 | 7080772.11 | 6833545.03 | 3.492 | 7.5 | false | 370831.64 |

```sql
SELECT billing_month, count(*) AS deal_months, sum(CAST(needs_review AS INT)) AS needs_review,
       round(sum(ssp_revenue_usd), 0) AS ssp_revenue_usd, round(sum(dsp_revenue_usd), 0) AS dsp_revenue_usd,
       round(sum(revenue_at_risk_usd), 0) AS revenue_at_risk_usd
FROM apex_recon.gold.recon_deal_month GROUP BY 1 ORDER BY 1
```
| billing_month | deal_months | needs_review | ssp_revenue_usd | dsp_revenue_usd | revenue_at_risk_usd |
|---|---|---|---|---|---|
| 2026-01 | 443 | 215 | 9.326348E7 | 8.6741096E7 | 7030514.0 |
| 2026-02 | 503 | 235 | 9.5305412E7 | 8.9020868E7 | 6969334.0 |
| 2026-03 | 563 | 256 | 1.1214089E8 | 1.05726001E8 | 6950589.0 |
| 2026-04 | 622 | 311 | 1.16826282E8 | 1.08527048E8 | 9554368.0 |
| 2026-05 | 670 | 338 | 1.31422117E8 | 1.23088817E8 | 9278477.0 |
| 2026-06 | 707 | 351 | 1.34363363E8 | 1.26248076E8 | 9986325.0 |
| 2026-07 | 714 | 344 | 1.43153611E8 | 1.33173391E8 | 1.1691834E7 |
| 2026-08 | 674 | 335 | 1.38541327E8 | 1.29129087E8 | 1.079644E7 |
| 2026-09 | 621 | 276 | 1.467845E8 | 1.37516882E8 | 1.0262008E7 |

```sql
SELECT publisher_type, count(*) AS publishers, round(sum(apex_payout_due_usd), 0) AS apex_payout_due_usd,
       round(sum(publisher_estimated_payout_usd), 0) AS publisher_estimated_payout_usd,
       round(sum(apex_take_usd), 0) AS apex_take_usd,
       round(100 * sum(apex_take_usd) / sum(ssp_revenue_usd), 2) AS take_rate_pct
FROM apex_recon.gold.publisher_recon_month WHERE billing_month = '2026-09' GROUP BY 1 ORDER BY 1
```
| publisher_type | publishers | apex_payout_due_usd | publisher_estimated_payout_usd | apex_take_usd | take_rate_pct |
|---|---|---|---|---|---|
| device_platform | 41 | 3.7085662E7 | 3.633114E7 | 7403127.0 | 16.64 |
| fast_channel | 70 | 5.3715645E7 | 5.2573238E7 | 1.0013195E7 | 15.71 |
| streaming_service | 39 | 3.2411138E7 | 3.1808236E7 | 6155733.0 | 15.96 |

```sql
SELECT g.root_cause, count(*) AS deal_months, round(avg(f.tz_shift_gain), 2) AS avg_tz_shift_gain,
       round(avg(f.sibling_offset_match), 2) AS avg_sibling_offset, round(avg(f.missing_day_share), 3) AS avg_missing_day_share,
       round(avg(abs(f.rev_minus_imp_gap_pct)), 2) AS avg_abs_rev_minus_imp, round(avg(f.large_gap_day_share), 2) AS avg_large_gap_days
FROM apex_recon.ml.discrepancy_features f JOIN apex_recon.ml.ground_truth_root_causes g USING (deal_id, billing_month)
GROUP BY 1 ORDER BY 1
```
| root_cause | deal_months | avg_tz_shift_gain | avg_sibling_offset | avg_missing_day_share | avg_abs_rev_minus_imp | avg_large_gap_days |
|---|---|---|---|---|---|---|
| DEAL_ID_MISMAPPING | 348 | 0.91 | 0.85 | 0.007 | 15.02 | 0.87 |
| FX_MISMATCH | 282 | 0.01 | 0.09 | 0.008 | 6.35 | 0.02 |
| GENUINE_BILLING_ERROR | 309 | 0.08 | 0.36 | 0.008 | 0.03 | 0.47 |
| IVT_FILTERING | 628 | 0.17 | 0.32 | 0.009 | 0.01 | 0.71 |
| LATE_OR_MISSING_DATA | 311 | 0.02 | 0.34 | 0.184 | 0.05 | 0.03 |
| SSAI_BEACON_LOSS | 575 | 0.19 | 0.35 | 0.007 | 0.07 | 0.78 |
| TIMEZONE_SHIFT | 362 | 7.17 | 0.13 | 0.009 | 0.06 | 0.48 |
| WITHIN_TOLERANCE | 2699 | 0.01 | 0.18 | 0.008 | 0.01 | 0.01 |
