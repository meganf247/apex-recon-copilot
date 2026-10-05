
```sql
SELECT origin.flow_name AS dataset,
       max(details:flow_progress.metrics.num_output_rows::BIGINT) AS output_rows,
       max(details:flow_progress.data_quality.dropped_records::BIGINT) AS dropped_by_expectations
FROM event_log('5d44a671-5813-463d-903e-33ca04bb3376')
WHERE event_type = 'flow_progress' AND details:flow_progress.status = 'COMPLETED'
  AND origin.update_id = (SELECT origin.update_id FROM event_log('5d44a671-5813-463d-903e-33ca04bb3376')
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
| apex_recon.gold.recon_deal_daily | 158886 | 0 |
| apex_recon.gold.recon_deal_month | 5518 | 0 |
| apex_recon.gold.recon_partner_month | 351 | 0 |
| apex_recon.ml.discrepancy_features | 5518 | 0 |
| apex_recon.silver.dim_deals | 800 | 0 |
| apex_recon.silver.dim_dsps | 40 | 0 |
| apex_recon.silver.dim_publishers | 150 | 0 |
| apex_recon.silver.dispute_history | 2152 | 0 |
| apex_recon.silver.dsp_daily_reports | 156404 | 1718 |
| apex_recon.silver.dsp_reports_quarantine | 1718 | 0 |
| apex_recon.silver.fx_rates | 546 | 0 |
| apex_recon.silver.publisher_daily_reports | 158703 | 0 |
| apex_recon.silver.ssp_hourly |  |  |

```sql
SELECT origin.flow_name AS dataset, e.name AS expectation,
       sum(e.passed_records) AS passed_records, sum(e.failed_records) AS failed_records
FROM event_log('5d44a671-5813-463d-903e-33ca04bb3376'),
     LATERAL explode(from_json(details:flow_progress.data_quality.expectations,
                     'array<struct<name:string,dataset:string,passed_records:bigint,failed_records:bigint>>')) AS t(e)
WHERE event_type = 'flow_progress' AND details:flow_progress.data_quality.expectations IS NOT NULL
  AND origin.update_id = (SELECT origin.update_id FROM event_log('5d44a671-5813-463d-903e-33ca04bb3376')
                          WHERE event_type = 'create_update' ORDER BY timestamp DESC LIMIT 1)
GROUP BY 1, 2 ORDER BY 1, 2
```
| dataset | expectation | passed_records | failed_records |
|---|---|---|---|
| apex_recon.silver.dispute_history | has_label | 2152 | 0 |
| apex_recon.silver.dsp_daily_reports | known_deal | 157506 | 616 |
| apex_recon.silver.dsp_daily_reports | non_negative_impressions | 157819 | 303 |
| apex_recon.silver.dsp_daily_reports | not_duplicate | 157672 | 450 |
| apex_recon.silver.dsp_daily_reports | seat_matches_partner | 158076 | 46 |
| apex_recon.silver.dsp_daily_reports | valid_amount | 158122 | 0 |
| apex_recon.silver.dsp_daily_reports | valid_report_date | 157813 | 309 |
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
| known_deal | 616 |
| not_duplicate | 450 |
| valid_report_date | 309 |
| non_negative_impressions | 303 |
| seat_matches_partner | 46 |

```sql
SELECT dsp_id, source_format, report_date, deal_id, impressions, amount_native, failed_rules, _source_file
FROM apex_recon.silver.dsp_reports_quarantine ORDER BY dsp_id, _source_file LIMIT 10
```
| dsp_id | source_format | report_date | deal_id | impressions | amount_native | failed_rules | _source_file |
|---|---|---|---|---|---|---|---|
| DSP001 | A |  | D00671 | 239848 | 7567.27 | ["valid_report_date"] | /Volumes/apex_recon/landing/raw/dsp_reports/DSP001/DSP001_billing_2026-01.csv |
| DSP001 | A |  | D00185 | 115859 | 6667.1 | ["valid_report_date"] | /Volumes/apex_recon/landing/raw/dsp_reports/DSP001/DSP001_billing_2026-01.csv |
| DSP001 | A | 2026-01-07 | D00713 | 106167 | 4259.53 | ["not_duplicate"] | /Volumes/apex_recon/landing/raw/dsp_reports/DSP001/DSP001_billing_2026-01.csv |
| DSP001 | A | 2026-02-27 | D00510 | -545910 | 22225.56 | ["non_negative_impressions"] | /Volumes/apex_recon/landing/raw/dsp_reports/DSP001/DSP001_billing_2026-02.csv |
| DSP001 | A | 2026-02-12 | D00510 | 430473 | 17443.72 | ["not_duplicate"] | /Volumes/apex_recon/landing/raw/dsp_reports/DSP001/DSP001_billing_2026-02.csv |
| DSP001 | A | 2026-03-26 | D00376 | 57893 | 1696.92 | ["not_duplicate"] | /Volumes/apex_recon/landing/raw/dsp_reports/DSP001/DSP001_billing_2026-03.csv |
| DSP001 | A | 2026-03-18 |  | 44596 | 2606.92 | ["known_deal"] | /Volumes/apex_recon/landing/raw/dsp_reports/DSP001/DSP001_billing_2026-03.csv |
| DSP001 | A |  | D00749 | 49186 | 1882.46 | ["valid_report_date"] | /Volumes/apex_recon/landing/raw/dsp_reports/DSP001/DSP001_billing_2026-03.csv |
| DSP001 | A |  | D00185 | 83477 | 4950.98 | ["valid_report_date"] | /Volumes/apex_recon/landing/raw/dsp_reports/DSP001/DSP001_billing_2026-03.csv |
| DSP001 | A | 2026-03-11 |  | 46875 | 1675.61 | ["known_deal"] | /Volumes/apex_recon/landing/raw/dsp_reports/DSP001/DSP001_billing_2026-03.csv |

```sql
SELECT source_format, currency, count(*) AS rows, count(DISTINCT dsp_id) AS dsps,
       round(sum(amount_native), 2) AS amount_native, round(sum(amount_usd), 2) AS amount_usd
FROM apex_recon.silver.dsp_daily_reports GROUP BY 1, 2 ORDER BY 1, 2
```
| source_format | currency | rows | dsps | amount_native | amount_usd |
|---|---|---|---|---|---|
| A | USD | 98099 | 19 | 6.4532868147E8 | 6.4532868147E8 |
| B | EUR | 20361 | 4 | 1.1839155466E8 | 1.2373985049E8 |
| B | GBP | 4567 | 2 | 2.018688259E7 | 2.5017806E7 |
| B | USD | 19880 | 7 | 1.4347307263E8 | 1.4347307263E8 |
| C | USD | 13497 | 7 | 1.1079650553E8 | 1.1079650553E8 |

```sql
SELECT dsp_name, partner_team, active_deals, deals_needing_review, ssp_revenue_usd, dsp_revenue_usd,
       revenue_gap_pct, discrepancy_threshold_pct, over_threshold, revenue_at_risk_usd
FROM apex_recon.gold.recon_partner_month WHERE billing_month = '2026-09'
ORDER BY revenue_at_risk_usd DESC LIMIT 10
```
| dsp_name | partner_team | active_deals | deals_needing_review | ssp_revenue_usd | dsp_revenue_usd | revenue_gap_pct | discrepancy_threshold_pct | over_threshold | revenue_at_risk_usd |
|---|---|---|---|---|---|---|---|---|---|
| Lattice Media | Pacific | 141 | 58 | 3.31845132E7 | 3.163846182E7 | 4.659 | 7.5 | false | 1988054.12 |
| Mosaic Bid | EMEA | 68 | 27 | 1.596595355E7 | 1.485907551E7 | 6.933 | 7.5 | false | 1187349.77 |
| Sable Buy | Pacific | 34 | 25 | 9922770.65 | 9065386.77 | 8.641 | 7.5 | true | 1042337.08 |
| Reachlytics | Pacific | 17 | 5 | 2534517.97 | 2395354.55 | 5.491 | 7.5 | false | 465768.75 |
| Kestrel Demand | Atlantic | 18 | 12 | 3324111.65 | 2974608.14 | 10.514 | 10.0 | true | 408867.31 |
| Bluefin Media | Central | 29 | 13 | 7080772.11 | 6724352.35 | 5.034 | 7.5 | false | 384540.09 |
| Cobalt Ads | Pacific | 27 | 8 | 7109842.38 | 6745740.51 | 5.121 | 10.0 | false | 364101.87 |
| Summit Audience | Pacific | 32 | 11 | 7526808.52 | 7176488.3 | 4.654 | 10.0 | false | 359913.07 |
| Onyx Programmatic | Pacific | 9 | 8 | 3769469.58 | 3523933.5 | 6.514 | 10.0 | false | 355382.51 |
| Redwood Demand | Central | 14 | 7 | 5338174.36 | 5053030.68 | 5.342 | 5.0 | true | 343205.74 |

```sql
SELECT billing_month, count(*) AS deal_months, sum(CAST(needs_review AS INT)) AS needs_review,
       round(sum(ssp_revenue_usd), 0) AS ssp_revenue_usd, round(sum(dsp_revenue_usd), 0) AS dsp_revenue_usd,
       round(sum(revenue_at_risk_usd), 0) AS revenue_at_risk_usd
FROM apex_recon.gold.recon_deal_month GROUP BY 1 ORDER BY 1
```
| billing_month | deal_months | needs_review | ssp_revenue_usd | dsp_revenue_usd | revenue_at_risk_usd |
|---|---|---|---|---|---|
| 2026-01 | 443 | 223 | 9.326348E7 | 8.7433483E7 | 6571125.0 |
| 2026-02 | 503 | 219 | 9.5305412E7 | 9.0184859E7 | 6275363.0 |
| 2026-03 | 563 | 246 | 1.1214089E8 | 1.05859109E8 | 8411518.0 |
| 2026-04 | 622 | 278 | 1.16826282E8 | 1.10184141E8 | 7706276.0 |
| 2026-05 | 671 | 293 | 1.31422117E8 | 1.2383997E8 | 9149018.0 |
| 2026-06 | 707 | 333 | 1.34363363E8 | 1.26701581E8 | 8864437.0 |
| 2026-07 | 714 | 342 | 1.43153611E8 | 1.34620706E8 | 9908480.0 |
| 2026-08 | 674 | 292 | 1.38541327E8 | 1.31009252E8 | 8377026.0 |
| 2026-09 | 621 | 287 | 1.467845E8 | 1.38522816E8 | 9641795.0 |

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
| DEAL_ID_MISMAPPING | 318 | 1.0 | 0.88 | 0.008 | 17.68 | 0.9 |
| FX_MISMATCH | 268 | 0.0 | 0.07 | 0.008 | 6.28 | 0.0 |
| GENUINE_BILLING_ERROR | 286 | 0.05 | 0.28 | 0.007 | 0.03 | 0.46 |
| IVT_FILTERING | 620 | 0.22 | 0.29 | 0.008 | 0.01 | 0.79 |
| LATE_OR_MISSING_DATA | 304 | 0.0 | 0.33 | 0.149 | 0.05 | 0.0 |
| SSAI_BEACON_LOSS | 592 | 0.19 | 0.32 | 0.009 | 0.12 | 0.71 |
| TIMEZONE_SHIFT | 502 | 8.13 | 0.16 | 0.008 | 0.05 | 0.46 |
| WITHIN_TOLERANCE | 2624 | 0.0 | 0.12 | 0.008 | 0.01 | 0.0 |
