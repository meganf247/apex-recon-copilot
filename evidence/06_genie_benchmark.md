# Genie benchmark: space `01f1c1a695ce1f47baa2f07ef9f73663`

**Accuracy: 14/14 questions answered correctly.**

## 1. What was the total revenue at risk across all DSPs for the September 2026 close?

- Genie status: COMPLETED  
- Expected (reference SQL): `6778508.0`  
- Genie first row: `['6778508.0']`  
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

Genie text: For the September 2026 close, total **revenue at risk** across all DSPs was **$6,778,508**. Based on the result shown, the September 2026 dispute queue totals **$6.8M** in revenue at risk.

## 2. Which DSP had the most revenue at risk in September 2026?

- Genie status: COMPLETED  
- Expected (reference SQL): `Lumen Programmatic`  
- Genie first row: `['Lumen Programmatic', 'Central', '743460.0']`  
- **PASS**

Genie SQL:
```sql
WITH ranked AS (
  SELECT
    `dsp_name`,
    `partner_team`,
    ROUND(`revenue_at_risk_usd`) AS `revenue_at_risk_usd`,
    RANK() OVER (ORDER BY `revenue_at_risk_usd` DESC) AS `rnk`
  FROM `apex_recon`.`gold`.`recon_partner_month`
  WHERE `billing_month` = '2026-09'
    AND `dsp_name` IS NOT NULL
    AND `revenue_at_risk_usd` IS NOT NULL
)
SELECT `dsp_name`, `partner_team`, `revenue_at_risk_usd`
FROM ranked
WHERE `rnk` <= 1
ORDER BY `revenue_at_risk_usd` DESC, `dsp_name`
```
Reference SQL:
```sql
SELECT dsp_name FROM apex_recon.gold.recon_partner_month WHERE billing_month = '2026-09' ORDER BY revenue_at_risk_usd DESC LIMIT 1
```

Genie text: In September 2026, **Lumen Programmatic** had the highest revenue at risk at **$743,460**, and the assigned partner team was **Central**. Based on the top-ranked result returned, **Lumen Programmatic** was the DSP with the most money in dispute for that month.

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

Genie text: Would you like me to count only cases explicitly marked as open, excluding those with other statuses like resolved or in review? There are **715** dispute cases in the Q3 queue across billing months **2026-07**, **2026-08**, and **2026-09**. Based on the query result, the total Q3 queue size is **715 cases**.

## 5. What is the most common predicted root cause among Q3 dispute cases?

- Genie status: COMPLETED  
- Expected (reference SQL): `IVT_FILTERING`  
- Genie first row: `['IVT_FILTERING', '269']`  
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
WHERE `rnk` = 1
ORDER BY `predicted_root_cause` ASC;
```
Reference SQL:
```sql
SELECT predicted_root_cause FROM apex_recon.gold.dispute_queue GROUP BY 1 ORDER BY count(*) DESC LIMIT 1
```

Genie text: The most common predicted root cause among Q3 dispute cases is **IVT filtering**, with **269** cases. Based on the Q3 dispute queue results, **IVT filtering** is the top driver of disputes in the quarter.

## 6. Which predicted root cause accounts for the most revenue at risk in Q3?

- Genie status: COMPLETED  
- Expected (reference SQL): `IVT_FILTERING`  
- Genie first row: `['IVT_FILTERING', '7945604.0']`  
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
), ranked_root_causes AS (
  SELECT
    `predicted_root_cause`,
    `revenue_at_risk_usd`,
    RANK() OVER (ORDER BY `revenue_at_risk_usd` DESC) AS `rnk`
  FROM root_cause_totals
)
SELECT
  `predicted_root_cause`,
  `revenue_at_risk_usd`
FROM ranked_root_causes
WHERE `rnk` <= 1
ORDER BY `revenue_at_risk_usd` DESC
```
Reference SQL:
```sql
SELECT predicted_root_cause FROM apex_recon.gold.dispute_queue GROUP BY 1 ORDER BY sum(revenue_at_risk_usd) DESC LIMIT 1
```

Genie text: In Q3, **IVT filtering** accounts for the most revenue at risk, with **$7,945,604** in revenue at risk. Based on the top-ranked result, **IVT filtering** is the largest driver of the dispute queue in Q3.

## 7. How much revenue at risk is attributed to timezone shift cases in Q3?

- Genie status: COMPLETED  
- Expected (reference SQL): `596244.0`  
- Genie first row: `['596244.0']`  
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

Genie text: In Q3 (billing months **2026-07** to **2026-09**), revenue at risk attributed to **timezone shift** cases is **$596,244**. Based on the single result returned, the total Q3 amount for timezone shift cases is **$596,244**.

## 8. Which partner team has the most revenue at risk in Q3?

- Genie status: COMPLETED  
- Expected (reference SQL): `Atlantic`  
- Genie first row: `['Atlantic', '6281762.0']`  
- **PASS**

Genie SQL:
```sql
WITH team_totals AS (
  SELECT
    `partner_team`,
    ROUND(SUM(`revenue_at_risk_usd`)) AS `q3_revenue_at_risk_usd`
  FROM `apex_recon`.`gold`.`recon_partner_month`
  WHERE `billing_month` IN ('2026-07', '2026-08', '2026-09')
    AND `partner_team` IS NOT NULL
    AND `revenue_at_risk_usd` IS NOT NULL
  GROUP BY `partner_team`
), ranked AS (
  SELECT
    `partner_team`,
    `q3_revenue_at_risk_usd`,
    RANK() OVER (ORDER BY `q3_revenue_at_risk_usd` DESC) AS `rnk`
  FROM team_totals
)
SELECT
  `partner_team`,
  `q3_revenue_at_risk_usd`
FROM ranked
WHERE `rnk` <= 1
ORDER BY `q3_revenue_at_risk_usd` DESC, `partner_team`
```
Reference SQL:
```sql
SELECT partner_team FROM apex_recon.gold.dispute_queue GROUP BY 1 ORDER BY sum(revenue_at_risk_usd) DESC LIMIT 1
```

Genie text: The **Atlantic** partner team has the most revenue at risk in Q3, with **$6,281,762** in revenue at risk. Based on the result shown, **Atlantic** is the top-ranked team for Q3 revenue at risk.

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

Genie text: In the September 2026 close, **219 deals** needed review. This means the dispute review queue for billing_month **2026-09** included **219 deals**.

## 10. Which content genre has the highest revenue at risk on live content in Q3?

- Genie status: COMPLETED  
- Expected (reference SQL): `sports`  
- Genie first row: `['sports', '6024339.0']`  
- **PASS**

Genie SQL:
```sql
WITH genre_totals AS (
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
  FROM genre_totals
)
SELECT
  `content_genre`,
  `revenue_at_risk_usd`
FROM ranked
WHERE `rnk` <= 1
ORDER BY `revenue_at_risk_usd` DESC, `content_genre` ASC;
```
Reference SQL:
```sql
SELECT content_genre FROM apex_recon.gold.dispute_queue WHERE is_live GROUP BY 1 ORDER BY sum(revenue_at_risk_usd) DESC LIMIT 1
```

Genie text: The content genre with the **highest** revenue at risk on live content in Q3 is **sports**, with **$6,024,339** in revenue at risk. Based on the Q3 live-content ranking shown, **sports** is the top exposure area.

## 11. How many dispute cases have been resolved so far?

- Genie status: COMPLETED  
- Expected (reference SQL): `1`  
- Genie first row: `['1']`  
- **PASS**

Genie SQL:
```sql
SELECT COUNT(DISTINCT `case_id`) AS `resolved_cases`
FROM `apex_recon`.`ops`.`dispute_case_status`
WHERE `status` = 'RESOLVED'
```
Reference SQL:
```sql
SELECT count(*) FROM apex_recon.ops.dispute_case_status WHERE status = 'RESOLVED'
```

Genie text: There have been **1** resolved dispute case so far. Based on the current status records, the total count of distinct resolved case IDs is **1**.

## 12. How much money has been recovered from resolved disputes so far?

- Genie status: COMPLETED  
- Expected (reference SQL): `139991.0`  
- Genie first row: `['139991.0']`  
- **PASS**

Genie SQL:
```sql
SELECT round(sum(coalesce(`recovered_usd`, 0))) AS `recovered_usd`
FROM `apex_recon`.`ops`.`dispute_case_status`
WHERE `status` = 'RESOLVED'
```
Reference SQL:
```sql
SELECT round(sum(recovered_usd)) FROM apex_recon.ops.dispute_case_status
```

Genie text: A total of **$139,991** has been recovered from disputes with status **RESOLVED** so far. Based on the single result returned, the recovered amount currently stands at **$139,991**.

## 13. What was the total billing shortfall across all deals in Q3 2026, including deals within tolerance?

- Genie status: COMPLETED  
- Expected (reference SQL): `2.4428097E7`  
- Genie first row: `['2.4428097E7']`  
- **PASS**

Genie SQL:
```sql
SELECT round(sum(`billing_shortfall_usd`)) AS `billing_shortfall_usd`
FROM `apex_recon`.`gold`.`recon_partner_month`
WHERE `billing_month` IN ('2026-07', '2026-08', '2026-09')
```
Reference SQL:
```sql
SELECT round(sum(billing_shortfall_usd)) FROM apex_recon.gold.recon_partner_month WHERE billing_month IN ('2026-07','2026-08','2026-09')
```

Genie text: The total **billing shortfall** across all deals in **Q3 2026** was **$24,428,097**. This amount includes deals **within tolerance**, because it comes from the **billing_shortfall_usd** total for billing months **2026-07, 2026-08, and 2026-09**.

## 14. What is Apex's own net exposure, after publisher pass-through, on the Q3 dispute queue?

- Genie status: COMPLETED  
- Expected (reference SQL): `8924095.0`  
- Genie first row: `['8924095.0']`  
- **PASS**

Genie SQL:
```sql
SELECT round(sum(`apex_exposure_usd`)) AS `apex_exposure_usd`
FROM `apex_recon`.`gold`.`dispute_queue`
WHERE `billing_month` IN ('2026-07', '2026-08', '2026-09')
```
Reference SQL:
```sql
SELECT round(sum(apex_exposure_usd)) FROM apex_recon.gold.dispute_queue
```

Genie text: Apex's own **net exposure** on the Q3 dispute queue is **$8,924,095**. Based on the Q3 dispute queue total shown for billing months **2026-07, 2026-08, and 2026-09**, Apex's P&L exposure is **$8.9M**.
