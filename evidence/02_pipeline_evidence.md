
```sql
SELECT origin.flow_name AS dataset,
       max(details:flow_progress.metrics.num_output_rows::BIGINT) AS output_rows,
       max(details:flow_progress.data_quality.dropped_records::BIGINT) AS dropped_by_expectations
FROM event_log('7e5bc896-605c-44f6-a2e3-039922e893a9')
WHERE event_type = 'flow_progress' AND origin.flow_name LIKE 'apex_recon.%'
  AND origin.update_id = (SELECT origin.update_id FROM event_log('7e5bc896-605c-44f6-a2e3-039922e893a9')
                          WHERE event_type = 'create_update' ORDER BY timestamp DESC LIMIT 1)
GROUP BY 1 ORDER BY 1
```
| dataset | output_rows | dropped_by_expectations |
|---|---|---|
| apex_recon.bronze.dsp_reports | 158723 | 0 |
| apex_recon.bronze.ssp_logs | 3565876 | 0 |
| apex_recon.gold.recon_deal_month | 5562 | 0 |
| apex_recon.gold.recon_partner_month | 360 | 0 |
| apex_recon.silver.dsp_daily | 156995 | 1728 |
| apex_recon.silver.ssp_daily | 159781 | 0 |

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
| apex_recon.silver.dsp_daily | has_deal_id | 158090 | 633 |
| apex_recon.silver.dsp_daily | non_negative_impressions | 158433 | 290 |
| apex_recon.silver.dsp_daily | not_duplicate | 158242 | 481 |
| apex_recon.silver.dsp_daily | valid_date | 158392 | 331 |

```sql
SELECT count(*) AS bronze_dsp_rows FROM apex_recon.bronze.dsp_reports
```
| bronze_dsp_rows |
|---|
| 158723 |

```sql
SELECT count(*) AS silver_dsp_rows, count(DISTINCT dsp_id) AS dsps, min(report_date) AS first_day, max(report_date) AS last_day
FROM apex_recon.silver.dsp_daily
```
| silver_dsp_rows | dsps | first_day | last_day |
|---|---|---|---|
| 156995 | 40 | 2026-01-01 | 2026-09-30 |

```sql
SELECT dsp_name, partner_team, active_deals, deals_needing_review, ssp_revenue_usd, dsp_revenue_usd,
       revenue_gap_pct, discrepancy_threshold_pct, over_threshold, billing_shortfall_usd, revenue_at_risk_usd, apex_exposure_usd
FROM apex_recon.gold.recon_partner_month WHERE billing_month = '2026-09'
ORDER BY revenue_at_risk_usd DESC LIMIT 10
```
| dsp_name | partner_team | active_deals | deals_needing_review | ssp_revenue_usd | dsp_revenue_usd | revenue_gap_pct | discrepancy_threshold_pct | over_threshold | billing_shortfall_usd | revenue_at_risk_usd | apex_exposure_usd |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Lumen Programmatic | Central | 27 | 17 | 6614533.04 | 5851277.99 | 11.54 | 7.5 | true | 763255.05 | 743459.7 | 255469.33 |
| Mosaic Bid | Central | 29 | 11 | 8486053.05 | 7773376.48 | 8.4 | 5.0 | true | 712676.57 | 606388.07 | 258494.77 |
| Xenon Media | Atlantic | 60 | 14 | 1.133887509E7 | 1.07733603E7 | 4.99 | 5.0 | false | 565514.79 | 426911.08 | 232632.08 |
| Reachlytics | Atlantic | 44 | 18 | 8813786.09 | 8343765.11 | 5.33 | 5.0 | true | 470020.98 | 367092.21 | 165438.23 |
| Ironwood Ads | Central | 13 | 4 | 3961678.97 | 3545878.5 | 10.5 | 7.5 | true | 415800.47 | 363471.06 | 360485.6 |
| Umbra Ads | Pacific | 22 | 6 | 6783044.3 | 6387398.37 | 5.83 | 5.0 | true | 395645.93 | 303167.82 | 279590.79 |
| BidSphere | Pacific | 12 | 7 | 2780676.5 | 2481045.14 | 10.78 | 5.0 | true | 299631.36 | 290169.06 | 55227.52 |
| Lattice Media | Pacific | 23 | 8 | 5240342.03 | 4845878.77 | 7.53 | 10.0 | false | 394463.26 | 280307.99 | 57336.1 |
| Kestrel Demand | Pacific | 14 | 8 | 2955525.7 | 2661940.62 | 9.93 | 10.0 | false | 293585.08 | 277039.03 | 153263.34 |
| TradeNova | Central | 28 | 8 | 5338989.74 | 4996449.08 | 6.42 | 5.0 | true | 342540.66 | 268935.28 | 182787.75 |

```sql
SELECT billing_month, count(*) AS deal_months, sum(CAST(needs_review AS INT)) AS needs_review,
       round(sum(ssp_revenue_usd), 0) AS ssp_revenue_usd, round(sum(dsp_revenue_usd), 0) AS dsp_revenue_usd,
       round(sum(billing_shortfall_usd), 0) AS billing_shortfall_usd, round(sum(revenue_at_risk_usd), 0) AS revenue_at_risk_usd,
       round(sum(apex_net_revenue_usd), 0) AS apex_net_revenue_usd, round(sum(apex_exposure_usd), 0) AS apex_exposure_usd
FROM apex_recon.gold.recon_deal_month GROUP BY 1 ORDER BY 1
```
| billing_month | deal_months | needs_review | ssp_revenue_usd | dsp_revenue_usd | billing_shortfall_usd | revenue_at_risk_usd | apex_net_revenue_usd | apex_exposure_usd |
|---|---|---|---|---|---|---|---|---|
| 2026-01 | 453 | 168 | 9.4198077E7 | 8.7995038E7 | 6210038.0 | 4951780.0 | 1.351366E7 | 2565206.0 |
| 2026-02 | 512 | 186 | 9.6699829E7 | 9.0676983E7 | 6070810.0 | 4740264.0 | 1.3840395E7 | 2456879.0 |
| 2026-03 | 573 | 192 | 1.16074726E8 | 1.08998294E8 | 7077885.0 | 5483144.0 | 1.6596256E7 | 3167834.0 |
| 2026-04 | 623 | 235 | 1.20024942E8 | 1.12382497E8 | 7652692.0 | 5890555.0 | 1.7080243E7 | 3160370.0 |
| 2026-05 | 668 | 232 | 1.37614016E8 | 1.28355445E8 | 9260813.0 | 7271144.0 | 1.9558212E7 | 3610760.0 |
| 2026-06 | 708 | 254 | 1.35878494E8 | 1.27711103E8 | 8170078.0 | 6184592.0 | 1.9338798E7 | 3362224.0 |
| 2026-07 | 715 | 239 | 1.38427181E8 | 1.31580407E8 | 6850060.0 | 4636200.0 | 1.9839357E7 | 2262746.0 |
| 2026-08 | 680 | 257 | 1.4018683E8 | 1.31547539E8 | 8659175.0 | 6698764.0 | 2.0062522E7 | 3366663.0 |
| 2026-09 | 630 | 219 | 1.53526858E8 | 1.44607996E8 | 8918862.0 | 6778508.0 | 2.2016257E7 | 3294686.0 |
