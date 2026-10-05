# Genie benchmark: space `01f1c0d3f43414638f30fdd1ec386a32`

**Accuracy: 12/12 questions answered correctly.**

## 1. What was the total revenue at risk across all DSPs for the September 2026 close?

- Genie status: COMPLETED  
- Expected (reference SQL): `1.0262008E7`  
- Genie first row: `['1.0262008E7']`  
- **PASS**

Genie SQL:
```sql
SELECT round(sum(`revenue_at_risk_usd`)) AS `total_revenue_at_risk_usd`
FROM `apex_recon`.`gold`.`recon_partner_month`
WHERE `billing_month` = '2026-09'
```
Reference SQL:
```sql
SELECT round(sum(revenue_at_risk_usd)) FROM apex_recon.gold.recon_partner_month WHERE billing_month = '2026-09'
```

Genie text: For the September 2026 close, total revenue at risk across all DSPs was **$10,262,008**. Based on the single result returned for billing_month **2026-09**, the total exposure for that close was **$10.3M**.

## 2. Which DSP had the most revenue at risk in September 2026?

- Genie status: COMPLETED  
- Expected (reference SQL): `Lattice Media`  
- Genie first row: `['Lattice Media', 'Pacific', '2090964.0', '5.4']`  
- **PASS**

Genie SQL:
```sql
WITH ranked_dsps AS (
  SELECT dsp_name, partner_team, round(revenue_at_risk_usd) AS revenue_at_risk_usd, round(revenue_gap_pct, 1) AS revenue_gap_pct,
    RANK() OVER (ORDER BY revenue_at_risk_usd DESC) AS rnk
  FROM apex_recon.gold.recon_partner_month
  WHERE billing_month = '2026-09' AND dsp_name IS NOT NULL AND revenue_at_risk_usd IS NOT NULL
)
SELECT dsp_name, partner_team, revenue_at_risk_usd, revenue_gap_pct
FROM ranked_dsps
WHERE rnk = 1
```
Reference SQL:
```sql
SELECT dsp_name FROM apex_recon.gold.recon_partner_month WHERE billing_month = '2026-09' ORDER BY revenue_at_risk_usd DESC LIMIT 1
```

Genie text: In September 2026, **Lattice Media** had the highest revenue at risk at **$2,090,964**, with a revenue gap of **5.4%** and partner team **Pacific**. Based on the single top-ranked result returned, **Lattice Media** was the DSP with the most revenue at risk for 2026-09.

## 3. How many DSPs were over their contract discrepancy threshold in all three months of Q3 2026?

- Genie status: COMPLETED  
- Expected (reference SQL): `9`  
- Genie first row: `['9']`  
- **PASS**

Genie SQL:
```sql
SELECT COUNT(*) AS `dsps_over_threshold_all_q3_months`
FROM (
  SELECT `dsp_id`
  FROM `apex_recon`.`gold`.`recon_partner_month`
  WHERE `billing_month` IN ('2026-07', '2026-08', '2026-09')
  GROUP BY `dsp_id`
  HAVING COUNT(DISTINCT `billing_month`) = 3
     AND SUM(CASE WHEN `over_threshold` THEN 1 ELSE 0 END) = 3
) q
```
Reference SQL:
```sql
SELECT count(*) FROM (SELECT dsp_id FROM apex_recon.gold.recon_partner_month WHERE billing_month IN ('2026-07','2026-08','2026-09')
         GROUP BY dsp_id HAVING sum(CASE WHEN over_threshold THEN 1 ELSE 0 END) = 3)
```

Genie text: **9 DSPs** were over their contract discrepancy threshold in **all three months of Q3 2026**: **2026-07, 2026-08, and 2026-09**. This means the count includes only DSPs that were over threshold in each of the three Q3 billing months.

## 4. How many open dispute cases are in the Q3 queue in total?

- Genie status: COMPLETED  
- Expected (reference SQL): `955`  
- Genie first row: `['955']`  
- **PASS**

Genie SQL:
```sql
SELECT COUNT(*) AS `open_dispute_cases_q3_total`
FROM `apex_recon`.`gold`.`dispute_queue`
WHERE `billing_month` IN ('2026-07','2026-08','2026-09')
```
Reference SQL:
```sql
SELECT count(*) FROM apex_recon.gold.dispute_queue
```

Genie text: There are **955** dispute cases in the Q3 queue across billing months **2026-07**, **2026-08**, and **2026-09**. Based on the query results, the total Q3 queue size is **955** cases.

## 5. What is the most common predicted root cause among Q3 dispute cases?

- Genie status: COMPLETED  
- Expected (reference SQL): `SSAI_BEACON_LOSS`  
- Genie first row: `['SSAI_BEACON_LOSS', '208']`  
- **PASS**

Genie SQL:
```sql
WITH `root_cause_counts` AS (
  SELECT
    `predicted_root_cause`,
    COUNT(*) AS `cases`
  FROM `apex_recon`.`gold`.`dispute_queue`
  WHERE `billing_month` IN ('2026-07', '2026-08', '2026-09')
    AND `predicted_root_cause` IS NOT NULL
  GROUP BY `predicted_root_cause`
), `ranked_root_causes` AS (
  SELECT
    `predicted_root_cause`,
    `cases`,
    RANK() OVER (ORDER BY `cases` DESC) AS `rnk`
  FROM `root_cause_counts`
)
SELECT
  `predicted_root_cause`,
  `cases`
FROM `ranked_root_causes`
WHERE `rnk` <= 1
ORDER BY `cases` DESC, `predicted_root_cause` ASC;
```
Reference SQL:
```sql
SELECT predicted_root_cause FROM apex_recon.gold.dispute_queue GROUP BY 1 ORDER BY count(*) DESC LIMIT 1
```

Genie text: The most common predicted root cause among Q3 dispute cases is **SSAI beacon loss**, with **208** cases. Based on the Q3 dispute-case counts returned, **SSAI beacon loss** ranks highest among predicted root causes.

## 6. Which predicted root cause accounts for the most revenue at risk in Q3?

- Genie status: COMPLETED  
- Expected (reference SQL): `SSAI_BEACON_LOSS`  
- Genie first row: `['SSAI_BEACON_LOSS', '5748477.0']`  
- **PASS**

Genie SQL:
```sql
WITH root_cause_totals AS (
  SELECT
    `predicted_root_cause`,
    ROUND(SUM(`revenue_at_risk_usd`)) AS `revenue_at_risk_usd`
  FROM `apex_recon`.`gold`.`dispute_queue`
  WHERE `billing_month` IN ('2026-07', '2026-08', '2026-09')
    AND `predicted_root_cause` IS NOT NULL
  GROUP BY `predicted_root_cause`
), ranked AS (
  SELECT
    `predicted_root_cause`,
    `revenue_at_risk_usd`,
    RANK() OVER (ORDER BY `revenue_at_risk_usd` DESC) AS `rnk`
  FROM root_cause_totals
)
SELECT
  `predicted_root_cause`,
  `revenue_at_risk_usd`
FROM ranked
WHERE `rnk` = 1
```
Reference SQL:
```sql
SELECT predicted_root_cause FROM apex_recon.gold.dispute_queue GROUP BY 1 ORDER BY sum(revenue_at_risk_usd) DESC LIMIT 1
```

Genie text: In Q3, **SSAI beacon loss** is the predicted root cause with the most revenue at risk, totaling **$5,748,477**. Based on the Q3 ranking in the result, **SSAI beacon loss** is the top exposure driver.

## 7. How much revenue at risk is attributed to timezone shift cases in Q3?

- Genie status: COMPLETED  
- Expected (reference SQL): `1438589.0`  
- Genie first row: `['1438589.0']`  
- **PASS**

Genie SQL:
```sql
SELECT round(sum(`revenue_at_risk_usd`)) AS `revenue_at_risk_usd`
FROM `apex_recon`.`gold`.`dispute_queue`
WHERE `billing_month` IN ('2026-07', '2026-08', '2026-09')
  AND `predicted_root_cause` ILIKE '%TIMEZONE_SHIFT%'
```
Reference SQL:
```sql
SELECT round(sum(revenue_at_risk_usd)) FROM apex_recon.gold.dispute_queue WHERE predicted_root_cause = 'TIMEZONE_SHIFT'
```

Genie text: In Q3 (billing months **2026-07**, **2026-08**, and **2026-09**), revenue at risk attributed to **timezone shift** cases totals **$1,438,589**. Based on the single result returned, **$1,438,589** is the full Q3 exposure captured by this query for cases with predicted root cause = **timezone shift**.

## 8. Which partner team has the most revenue at risk in Q3?

- Genie status: COMPLETED  
- Expected (reference SQL): `Pacific`  
- Genie first row: `['Pacific', '1.7520585E7']`  
- **PASS**

Genie SQL:
```sql
WITH partner_q3 AS (
  SELECT partner_team, ROUND(SUM(revenue_at_risk_usd)) AS q3_revenue_at_risk_usd
  FROM apex_recon.gold.recon_partner_month
  WHERE billing_month IN ('2026-07','2026-08','2026-09') AND partner_team IS NOT NULL
  GROUP BY partner_team
)
SELECT partner_team, q3_revenue_at_risk_usd
FROM partner_q3
WHERE q3_revenue_at_risk_usd = (SELECT MAX(q3_revenue_at_risk_usd) FROM partner_q3)
ORDER BY partner_team
```
Reference SQL:
```sql
SELECT partner_team FROM apex_recon.gold.dispute_queue GROUP BY 1 ORDER BY sum(revenue_at_risk_usd) DESC LIMIT 1
```

Genie text: The **Pacific** partner team has the most revenue at risk in Q3, with **$17,520,585**. Based on the Q3 totals in the result, **Pacific** is the highest-risk partner team for revenue exposure.

## 9. How many deals needed review in the September 2026 close?

- Genie status: COMPLETED  
- Expected (reference SQL): `276`  
- Genie first row: `['276']`  
- **PASS**

Genie SQL:
```sql
SELECT COUNT(*) AS `deals_needing_review`
FROM `apex_recon`.`gold`.`recon_deal_month`
WHERE `billing_month` = '2026-09'
  AND `needs_review` = TRUE
```
Reference SQL:
```sql
SELECT sum(CAST(needs_review AS INT)) FROM apex_recon.gold.recon_deal_month WHERE billing_month = '2026-09'
```

Genie text: In the September 2026 close, **276 deals** needed review. This means **276 deals** were flagged with `needs_review = true` for billing month **2026-09**.

## 10. Which SSAI vendor has the highest revenue at risk on live content in Q3?

- Genie status: COMPLETED  
- Expected (reference SQL): `PodForge`  
- Genie first row: `['PodForge', '5331074.0']`  
- **PASS**

Genie SQL:
```sql
WITH vendor_risk AS (
  SELECT
    ssai_vendor,
    ROUND(SUM(revenue_at_risk_usd)) AS q3_revenue_at_risk_usd
  FROM apex_recon.gold.recon_deal_month
  WHERE billing_month IN ('2026-07', '2026-08', '2026-09')
    AND is_live = TRUE
    AND ssai_vendor IS NOT NULL
    AND revenue_at_risk_usd IS NOT NULL
  GROUP BY ssai_vendor
)
SELECT ssai_vendor, q3_revenue_at_risk_usd
FROM vendor_risk
WHERE q3_revenue_at_risk_usd = (
  SELECT MAX(q3_revenue_at_risk_usd) FROM vendor_risk
)
ORDER BY ssai_vendor
```
Reference SQL:
```sql
SELECT ssai_vendor FROM apex_recon.gold.dispute_queue WHERE is_live GROUP BY 1 ORDER BY sum(revenue_at_risk_usd) DESC LIMIT 1
```

Genie text: **PodForge** has the highest revenue at risk on live content in Q3, with **$5,331,074** in revenue at risk. Based on the Q3 live-content results returned, **PodForge** is the top SSAI vendor by exposure.

## 11. How many dispute cases have been resolved so far?

- Genie status: COMPLETED  
- Expected (reference SQL): `1`  
- Genie first row: `['1']`  
- **PASS**

Genie SQL:
```sql
SELECT COUNT(*) AS `resolved_cases`
FROM `apex_recon`.`ops`.`dispute_case_status`
WHERE `status` = 'RESOLVED'
```
Reference SQL:
```sql
SELECT count(*) FROM apex_recon.ops.dispute_case_status WHERE status = 'RESOLVED'
```

Genie text: There have been **1** dispute cases with status **RESOLVED** so far. Based on the visible result, the current resolved case count is **1**.

## 12. How much money has been recovered from resolved disputes so far?

- Genie status: COMPLETED  
- Expected (reference SQL): `0.0`  
- Genie first row: `['0.0']`  
- **PASS**

Genie SQL:
```sql
SELECT ROUND(SUM(COALESCE(`recovered_usd`, 0))) AS `recovered_usd`
FROM `apex_recon`.`ops`.`dispute_case_status`
WHERE `status` IS NOT NULL
  AND `status` ILIKE '%RESOLVED%'
```
Reference SQL:
```sql
SELECT round(sum(recovered_usd)) FROM apex_recon.ops.dispute_case_status
```

Genie text: So far, **$0** has been recovered from disputes with status **RESOLVED**. Based on the result shown, there is **1** total aggregated row and the resolved-dispute recovery amount is **$0**.
