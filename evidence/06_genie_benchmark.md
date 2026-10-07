# Genie benchmark: space `01f1c1a695ce1f47baa2f07ef9f73663`

**Accuracy: 12/12 questions answered correctly.**

## 1. What was the total revenue at risk across all DSPs for the September 2026 close?

- Genie status: COMPLETED  
- Expected (reference SQL): `8918862.0`  
- Genie first row: `['8918862.0']`  
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

Genie text: For the September 2026 close, total revenue at risk across all DSPs was **$8,918,862**. Based on the single result returned for billing month **2026-09**, the full amount of exposure shown is **$8,918,862**.

## 2. Which DSP had the most revenue at risk in September 2026?

- Genie status: COMPLETED  
- Expected (reference SQL): `Lumen Programmatic`  
- Genie first row: `['Lumen Programmatic', 'Central', '763255.0']`  
- **PASS**

Genie SQL:
```sql
SELECT dsp_name, partner_team, ROUND(revenue_at_risk_usd) AS revenue_at_risk_usd
FROM apex_recon.gold.recon_partner_month
WHERE billing_month = '2026-09' AND revenue_at_risk_usd IS NOT NULL AND dsp_name IS NOT NULL
ORDER BY revenue_at_risk_usd DESC
LIMIT 1
```
Reference SQL:
```sql
SELECT dsp_name FROM apex_recon.gold.recon_partner_month WHERE billing_month = '2026-09' ORDER BY revenue_at_risk_usd DESC LIMIT 1
```

Genie text: In September 2026, **Lumen Programmatic** had the highest revenue at risk at **$763,255**, and the partner team was **Central**. Based on the result shown, **Lumen Programmatic** was the top DSP for revenue exposure in that month.

## 3. How many DSPs were over their contract discrepancy threshold in all three months of Q3 2026?

- Genie status: COMPLETED  
- Expected (reference SQL): `2`  
- Genie first row: `['2']`  
- **PASS**

Genie SQL:
```sql
SELECT COUNT(*) AS `dsps_over_threshold_all_q3_months`
FROM (
  SELECT `dsp_id`
  FROM `apex_recon`.`gold`.`recon_partner_month`
  WHERE `billing_month` IN ('2026-07', '2026-08', '2026-09')
  GROUP BY `dsp_id`
  HAVING SUM(CASE WHEN `over_threshold` THEN 1 ELSE 0 END) = 3
) t
```
Reference SQL:
```sql
SELECT count(*) FROM (SELECT dsp_id FROM apex_recon.gold.recon_partner_month WHERE billing_month IN ('2026-07','2026-08','2026-09')
         GROUP BY dsp_id HAVING sum(CASE WHEN over_threshold THEN 1 ELSE 0 END) = 3)
```

Genie text: **2 DSPs** were over their contract discrepancy threshold in **all three months** of Q3 2026: **2026-07, 2026-08, and 2026-09**.

## 4. How many open dispute cases are in the Q3 queue in total?

- Genie status: COMPLETED  
- Expected (reference SQL): `715`  
- Genie first row: `['715']`  
- **PASS**

Genie SQL:
```sql
SELECT COUNT(*) AS `open_dispute_cases_q3`
FROM `apex_recon`.`gold`.`dispute_queue`
WHERE `billing_month` IN ('2026-07', '2026-08', '2026-09')
```
Reference SQL:
```sql
SELECT count(*) FROM apex_recon.gold.dispute_queue
```

Genie text: There are **715** dispute cases in the Q3 queue across billing months **2026-07**, **2026-08**, and **2026-09**. Based on the query results, the total Q3 queue size is **715** cases.

## 5. What is the most common predicted root cause among Q3 dispute cases?

- Genie status: COMPLETED  
- Expected (reference SQL): `IVT_FILTERING`  
- Genie first row: `['IVT_FILTERING', '280']`  
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
    RANK() OVER (ORDER BY `cases` DESC) AS `root_cause_rank`
  FROM `root_cause_counts`
)
SELECT
  `predicted_root_cause`,
  `cases`
FROM `ranked_root_causes`
WHERE `root_cause_rank` <= 1
ORDER BY `cases` DESC, `predicted_root_cause`
```
Reference SQL:
```sql
SELECT predicted_root_cause FROM apex_recon.gold.dispute_queue GROUP BY 1 ORDER BY count(*) DESC LIMIT 1
```

Genie text: The most common predicted root cause among Q3 dispute cases is **invalid traffic filtering**, with **280** cases. Based on the Q3 dispute-case results shown, **invalid traffic filtering** is the top driver by case count.

## 6. Which predicted root cause accounts for the most revenue at risk in Q3?

- Genie status: COMPLETED  
- Expected (reference SQL): `IVT_FILTERING`  
- Genie first row: `['IVT_FILTERING', '8179089.0']`  
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

Genie text: In Q3, **IVT filtering** accounts for the most revenue at risk, with **$8,179,089** in revenue at risk. Based on the top-ranked result returned, **IVT filtering** is the largest exposure among predicted root causes for billing months **2026-07 to 2026-09**.

## 7. How much revenue at risk is attributed to timezone shift cases in Q3?

- Genie status: COMPLETED  
- Expected (reference SQL): `561888.0`  
- Genie first row: `['561888.0']`  
- **PASS**

Genie SQL:
```sql
SELECT round(sum(`revenue_at_risk_usd`)) AS `revenue_at_risk_usd`
FROM `apex_recon`.`gold`.`dispute_queue`
WHERE `billing_month` IN ('2026-07', '2026-08', '2026-09')
  AND `predicted_root_cause` = 'TIMEZONE_SHIFT'
```
Reference SQL:
```sql
SELECT round(sum(revenue_at_risk_usd)) FROM apex_recon.gold.dispute_queue WHERE predicted_root_cause = 'TIMEZONE_SHIFT'
```

Genie text: In Q3 (billing_months **2026-07**, **2026-08**, and **2026-09**), the total revenue at risk for cases with predicted root cause **timezone shift** is **$561,888**. Based on the single result returned, **$561,888** is the full Q3 exposure captured by this query for timezone shift cases.

## 8. Which partner team has the most revenue at risk in Q3?

- Genie status: COMPLETED  
- Expected (reference SQL): `Atlantic`  
- Genie first row: `['Atlantic', '8656616.0']`  
- **PASS**

Genie SQL:
```sql
WITH partner_q3 AS (
  SELECT
    `partner_team`,
    ROUND(SUM(`revenue_at_risk_usd`)) AS `q3_revenue_at_risk_usd`
  FROM `apex_recon`.`gold`.`recon_partner_month`
  WHERE `billing_month` IN ('2026-07', '2026-08', '2026-09')
    AND `partner_team` IS NOT NULL
  GROUP BY `partner_team`
), ranked AS (
  SELECT
    `partner_team`,
    `q3_revenue_at_risk_usd`,
    RANK() OVER (ORDER BY `q3_revenue_at_risk_usd` DESC) AS `rnk`
  FROM partner_q3
)
SELECT
  `partner_team`,
  `q3_revenue_at_risk_usd`
FROM ranked
WHERE `rnk` = 1
```
Reference SQL:
```sql
SELECT partner_team FROM apex_recon.gold.dispute_queue GROUP BY 1 ORDER BY sum(revenue_at_risk_usd) DESC LIMIT 1
```

Genie text: The partner team with the most revenue at risk in Q3 is **Atlantic**, with **$8,656,616** in revenue at risk across billing months **2026-07, 2026-08, and 2026-09**.

## 9. How many deals needed review in the September 2026 close?

- Genie status: COMPLETED  
- Expected (reference SQL): `219`  
- Genie first row: `['219']`  
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

Genie text: In the **September 2026** close, **219 deals** needed review. This means **219 deals** in billing month **2026-09** were flagged with **needs review = true**.

## 10. Which content genre has the highest revenue at risk on live content in Q3?

- Genie status: COMPLETED  
- Expected (reference SQL): `sports`  
- Genie first row: `['sports', '7940256.0']`  
- **PASS**

Genie SQL:
```sql
WITH genre_risk AS (
  SELECT
    `content_genre`,
    ROUND(SUM(`revenue_at_risk_usd`)) AS `revenue_at_risk_usd`
  FROM `apex_recon`.`gold`.`recon_deal_month`
  WHERE `billing_month` IN ('2026-07', '2026-08', '2026-09')
    AND `is_live` = TRUE
    AND `content_genre` IS NOT NULL
  GROUP BY `content_genre`
), ranked AS (
  SELECT
    `content_genre`,
    `revenue_at_risk_usd`,
    RANK() OVER (ORDER BY `revenue_at_risk_usd` DESC) AS `rnk`
  FROM genre_risk
)
SELECT
  `content_genre`,
  `revenue_at_risk_usd`
FROM ranked
WHERE `rnk` = 1
```
Reference SQL:
```sql
SELECT content_genre FROM apex_recon.gold.dispute_queue WHERE is_live GROUP BY 1 ORDER BY sum(revenue_at_risk_usd) DESC LIMIT 1
```

Genie text: In Q3, the **sports** content genre had the highest revenue at risk for live content, at **$7,940,256**. Based on the result shown, **sports** ranked #1 among live content genres for revenue exposure in Q3.

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

Genie text: There have been **1** dispute cases with status **RESOLVED** so far. Based on the visible data, the current resolved case count is **1**.

## 12. How much money has been recovered from resolved disputes so far?

- Genie status: COMPLETED  
- Expected (reference SQL): `0.0`  
- Genie first row: `['0.0']`  
- **PASS**

Genie SQL:
```sql
SELECT round(sum(coalesce(`recovered_usd`, 0))) AS `recovered_usd`
FROM `apex_recon`.`ops`.`dispute_case_status`
WHERE `status` IS NOT NULL
  AND `status` ILIKE '%RESOLVED%'
```
Reference SQL:
```sql
SELECT round(sum(recovered_usd)) FROM apex_recon.ops.dispute_case_status
```

Genie text: So far, **$0** has been recovered from disputes with status **RESOLVED**. Based on the visible result, there is **1** aggregated total and it shows no recovered dollars recorded for resolved disputes.
