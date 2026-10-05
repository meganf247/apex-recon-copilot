# Genie benchmark: space `01f1c0d3f43414638f30fdd1ec386a32`

**Accuracy: 12/12 questions answered correctly.**

## 1. What was the total revenue at risk across all DSPs for the September 2026 close?

- Genie status: COMPLETED  
- Expected (reference SQL): `9641795.0`  
- Genie first row: `['9641795.0']`  
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

Genie text: For the September 2026 close, total revenue at risk across all DSPs was **$9,641,795**. Based on the single result returned for billing month **2026-09**, the total exposure is **$9.6M**.

## 2. Which DSP had the most revenue at risk in September 2026?

- Genie status: COMPLETED  
- Expected (reference SQL): `Lattice Media`  
- Genie first row: `['Lattice Media', 'Pacific', '1988054.0']`  
- **PASS**

Genie SQL:
```sql
SELECT dsp_name, partner_team, round(revenue_at_risk_usd) AS revenue_at_risk_usd
FROM apex_recon.gold.recon_partner_month
WHERE billing_month = '2026-09' AND dsp_name IS NOT NULL AND revenue_at_risk_usd IS NOT NULL
ORDER BY revenue_at_risk_usd DESC
LIMIT 1
```
Reference SQL:
```sql
SELECT dsp_name FROM apex_recon.gold.recon_partner_month WHERE billing_month = '2026-09' ORDER BY revenue_at_risk_usd DESC LIMIT 1
```

Genie text: In **September 2026**, **Lattice Media** had the highest revenue at risk at **$1,988,054**, and the assigned partner team was **Pacific**. Based on the top-ranked result returned, **Lattice Media** was the DSP with the most revenue at risk for that month.

## 3. How many DSPs were over their contract discrepancy threshold in all three months of Q3 2026?

- Genie status: COMPLETED  
- Expected (reference SQL): `5`  
- Genie first row: `['5']`  
- **PASS**

Genie SQL:
```sql
SELECT COUNT(*) AS `dsps_over_threshold_all_q3_months`
FROM (
  SELECT `dsp_id`
  FROM `apex_recon`.`gold`.`recon_partner_month`
  WHERE `billing_month` IN ('2026-07', '2026-08', '2026-09')
    AND `dsp_id` IS NOT NULL
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

Genie text: **5 DSPs** were over their contract discrepancy threshold in **all three months of Q3 2026**: **2026-07, 2026-08, and 2026-09**. This means the count includes only DSPs that were over threshold in each of the three Q3 billing months.

## 4. How many open dispute cases are in the Q3 queue in total?

- Genie status: COMPLETED  
- Expected (reference SQL): `921`  
- Genie first row: `['921']`  
- **PASS**

Genie SQL:
```sql
SELECT COUNT(*) AS `open_dispute_cases_q3_total`
FROM `apex_recon`.`gold`.`dispute_queue`
WHERE `billing_month` IN ('2026-07', '2026-08', '2026-09')
```
Reference SQL:
```sql
SELECT count(*) FROM apex_recon.gold.dispute_queue
```

Genie text: There are **921** dispute cases in the Q3 queue across billing months **2026-07**, **2026-08**, and **2026-09**. Based on the query, the total reflects all rows in `gold.dispute_queue` for Q3, not a separate filter on dispute status.

## 5. What is the most common predicted root cause among Q3 dispute cases?

- Genie status: COMPLETED  
- Expected (reference SQL): `IVT_FILTERING`  
- Genie first row: `['IVT_FILTERING', '191']`  
- **PASS**

Genie SQL:
```sql
WITH `root_cause_counts` AS (
  SELECT
    `predicted_root_cause`,
    COUNT(*) AS `case_count`
  FROM `apex_recon`.`gold`.`dispute_queue`
  WHERE `billing_month` IN ('2026-07', '2026-08', '2026-09')
    AND `predicted_root_cause` IS NOT NULL
  GROUP BY `predicted_root_cause`
), `ranked_root_causes` AS (
  SELECT
    `predicted_root_cause`,
    `case_count`,
    RANK() OVER (ORDER BY `case_count` DESC) AS `root_cause_rank`
  FROM `root_cause_counts`
)
SELECT
  `predicted_root_cause`,
  `case_count`
FROM `ranked_root_causes`
WHERE `root_cause_rank` <= 1
ORDER BY `case_count` DESC, `predicted_root_cause`
```
Reference SQL:
```sql
SELECT predicted_root_cause FROM apex_recon.gold.dispute_queue GROUP BY 1 ORDER BY count(*) DESC LIMIT 1
```

Genie text: The most common predicted root cause among Q3 dispute cases is **IVT filtering**, with **191** cases. Based on the Q3 dispute-case results returned, **IVT filtering** is the top driver by case volume.

## 6. Which predicted root cause accounts for the most revenue at risk in Q3?

- Genie status: COMPLETED  
- Expected (reference SQL): `SSAI_BEACON_LOSS`  
- Genie first row: `['SSAI_BEACON_LOSS', '5032434.0']`  
- **PASS**

Genie SQL:
```sql
WITH `root_cause_totals` AS (
  SELECT
    `predicted_root_cause`,
    ROUND(SUM(`revenue_at_risk_usd`)) AS `revenue_at_risk_usd`
  FROM `apex_recon`.`gold`.`dispute_queue`
  WHERE `billing_month` IN ('2026-07', '2026-08', '2026-09')
    AND `predicted_root_cause` IS NOT NULL
  GROUP BY `predicted_root_cause`
), `ranked` AS (
  SELECT
    `predicted_root_cause`,
    `revenue_at_risk_usd`,
    RANK() OVER (ORDER BY `revenue_at_risk_usd` DESC) AS `rnk`
  FROM `root_cause_totals`
)
SELECT
  `predicted_root_cause`,
  `revenue_at_risk_usd`
FROM `ranked`
WHERE `rnk` = 1
ORDER BY `revenue_at_risk_usd` DESC
```
Reference SQL:
```sql
SELECT predicted_root_cause FROM apex_recon.gold.dispute_queue GROUP BY 1 ORDER BY sum(revenue_at_risk_usd) DESC LIMIT 1
```

Genie text: In Q3, **SSAI beacon loss** accounts for the most revenue at risk, with **$5,032,434**. Based on the single top-ranked result returned, **SSAI beacon loss** is the leading predicted root cause for exposure in Q3.

## 7. How much revenue at risk is attributed to timezone shift cases in Q3?

- Genie status: COMPLETED  
- Expected (reference SQL): `928902.0`  
- Genie first row: `['928902.0']`  
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

Genie text: In Q3, revenue at risk attributed to **timezone shift** cases is **$928,902**.

## 8. Which partner team has the most revenue at risk in Q3?

- Genie status: COMPLETED  
- Expected (reference SQL): `Pacific`  
- Genie first row: `['Pacific', '1.4993249E7']`  
- **PASS**

Genie SQL:
```sql
WITH team_q3 AS (
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
  FROM team_q3
)
SELECT `partner_team`, `q3_revenue_at_risk_usd`
FROM ranked
WHERE `rnk` <= 1
```
Reference SQL:
```sql
SELECT partner_team FROM apex_recon.gold.dispute_queue GROUP BY 1 ORDER BY sum(revenue_at_risk_usd) DESC LIMIT 1
```

Genie text: The **Pacific** partner team has the most revenue at risk in Q3, with **$14,993,249** across billing months **2026-07, 2026-08, and 2026-09**. In the returned result, **Pacific** is the top-ranked partner team for Q3 revenue exposure.

## 9. How many deals needed review in the September 2026 close?

- Genie status: COMPLETED  
- Expected (reference SQL): `287`  
- Genie first row: `['287']`  
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

Genie text: In the **September 2026** close, **287 deals** needed review. Based on the result shown, the total count of deals flagged with **needs review = true** for billing month **2026-09** is **287**.

## 10. Which SSAI vendor has the highest revenue at risk on live content in Q3?

- Genie status: COMPLETED  
- Expected (reference SQL): `PodForge`  
- Genie first row: `['PodForge', '5265204.0']`  
- **PASS**

Genie SQL:
```sql
WITH vendor_risk AS (
  SELECT
    `ssai_vendor`,
    ROUND(SUM(`revenue_at_risk_usd`)) AS `q3_revenue_at_risk_usd`
  FROM `apex_recon`.`gold`.`recon_deal_month`
  WHERE `billing_month` IN ('2026-07', '2026-08', '2026-09')
    AND `is_live` = TRUE
    AND `ssai_vendor` IS NOT NULL
  GROUP BY `ssai_vendor`
), ranked AS (
  SELECT
    `ssai_vendor`,
    `q3_revenue_at_risk_usd`,
    RANK() OVER (ORDER BY `q3_revenue_at_risk_usd` DESC) AS `risk_rank`
  FROM vendor_risk
)
SELECT
  `ssai_vendor`,
  `q3_revenue_at_risk_usd`
FROM ranked
WHERE `risk_rank` = 1
ORDER BY `q3_revenue_at_risk_usd` DESC, `ssai_vendor`
```
Reference SQL:
```sql
SELECT ssai_vendor FROM apex_recon.gold.dispute_queue WHERE is_live GROUP BY 1 ORDER BY sum(revenue_at_risk_usd) DESC LIMIT 1
```

Genie text: **PodForge** has the highest revenue at risk on live content in Q3, with **$5,265,204** in revenue at risk. In the returned result set, **PodForge** is the top-ranked SSAI vendor for Q3 live-content exposure.

## 11. How many dispute cases have been resolved so far?

- Genie status: COMPLETED  
- Expected (reference SQL): `2`  
- Genie first row: `['2']`  
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

Genie text: There are **2** dispute cases with status **RESOLVED** so far. Based on the visible data, the resolved case count is **2**.

## 12. How much money has been recovered from resolved disputes so far?

- Genie status: COMPLETED  
- Expected (reference SQL): `423608.0`  
- Genie first row: `['423608.0']`  
- **PASS**

Genie SQL:
```sql
SELECT ROUND(SUM(COALESCE(`recovered_usd`, 0))) AS `recovered_usd`
FROM `apex_recon`.`ops`.`dispute_case_status`
WHERE `status` = 'RESOLVED'
```
Reference SQL:
```sql
SELECT round(sum(recovered_usd)) FROM apex_recon.ops.dispute_case_status
```

Genie text: A total of **$423,608** has been recovered from disputes with status **RESOLVED** so far. Based on the single result returned, the recovered amount across all resolved disputes is **$423,608**.
