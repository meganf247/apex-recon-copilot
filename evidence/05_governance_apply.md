
```sql
DROP FUNCTION IF EXISTS apex_recon.ops.partner_team_filter
```
  -> OK

```sql
DROP TABLE IF EXISTS apex_recon.ops.partner_team_access
```
  -> OK

```sql
CREATE TABLE IF NOT EXISTS apex_recon.ops.recon_access (
  principal        STRING  COMMENT 'User email or service principal application ID',
  partner_team     STRING  COMMENT 'Partner team whose DSPs this principal may see (Atlantic, Pacific, Central, EMEA), or * for all',
  can_see_revenue  BOOLEAN COMMENT 'TRUE for Finance: may see USD amounts; FALSE: USD columns are masked'
) COMMENT 'Access entitlements for reconciliation data. Drives the partner row filter and the revenue column mask.'
```
  -> OK

```sql
INSERT OVERWRITE apex_recon.ops.recon_access VALUES
  ('megan.fogal@databricks.com',            '*',        TRUE),   
  ('pm.atlantic@apexexchange.example',      'Atlantic', FALSE),  
  ('pm.emea@apexexchange.example',          'EMEA',     FALSE)
```
| num_affected_rows | num_inserted_rows |
|---|---|
| 3 | 3 |

```sql
CREATE OR REPLACE FUNCTION apex_recon.ops.partner_access_filter(team STRING)
RETURNS BOOLEAN
COMMENT 'Row filter: a principal sees a row only if ops.recon_access grants them that partner team (or * for all teams).'
RETURN EXISTS (SELECT 1 FROM apex_recon.ops.recon_access a
               WHERE a.principal = current_user() AND (a.partner_team = '*' OR a.partner_team = team))
```
  -> OK

```sql
CREATE OR REPLACE FUNCTION apex_recon.ops.finance_only_usd(amount DOUBLE)
RETURNS DOUBLE
COMMENT 'Column mask: USD amounts are visible only to principals with can_see_revenue in ops.recon_access; others see NULL.'
RETURN CASE WHEN EXISTS (SELECT 1 FROM apex_recon.ops.recon_access a
                         WHERE a.principal = current_user() AND a.can_see_revenue) THEN amount ELSE NULL END
```
  -> OK

```sql
ALTER TABLE apex_recon.gold.dispute_queue SET ROW FILTER apex_recon.ops.partner_access_filter ON (partner_team)
```
  -> OK

```sql
ALTER TABLE apex_recon.gold.dispute_queue ALTER COLUMN ssp_revenue_usd     SET MASK apex_recon.ops.finance_only_usd
```
  -> OK

```sql
ALTER TABLE apex_recon.gold.dispute_queue ALTER COLUMN dsp_revenue_usd     SET MASK apex_recon.ops.finance_only_usd
```
  -> OK

```sql
ALTER TABLE apex_recon.gold.dispute_queue ALTER COLUMN revenue_gap_usd     SET MASK apex_recon.ops.finance_only_usd
```
  -> OK

```sql
ALTER TABLE apex_recon.gold.dispute_queue ALTER COLUMN revenue_at_risk_usd SET MASK apex_recon.ops.finance_only_usd
```
  -> OK

```sql
ALTER TABLE apex_recon.gold.dispute_queue          SET TAGS ('domain' = 'finance')
```
  -> OK

```sql
ALTER TABLE apex_recon.gold.case_workbench         SET TAGS ('domain' = 'finance')
```
  -> OK

```sql
ALTER TABLE apex_recon.gold.dispute_drafts         SET TAGS ('domain' = 'finance', 'contains' = 'genai_generated_text')
```
  -> OK

```sql
ALTER TABLE apex_recon.gold.recon_deal_month       SET TAGS ('domain' = 'finance')
```
  -> OK

```sql
ALTER TABLE apex_recon.gold.recon_partner_month    SET TAGS ('domain' = 'finance')
```
  -> OK

```sql
ALTER TABLE apex_recon.ml.ground_truth_root_causes SET TAGS ('usage' = 'evaluation_only')
```
  -> OK

```sql
ALTER TABLE apex_recon.gold.dispute_queue ALTER COLUMN ssp_revenue_usd     SET TAGS ('sensitivity' = 'internal')
```
  -> OK

```sql
ALTER TABLE apex_recon.gold.dispute_queue ALTER COLUMN dsp_revenue_usd     SET TAGS ('sensitivity' = 'internal')
```
  -> OK

```sql
ALTER TABLE apex_recon.gold.dispute_queue ALTER COLUMN revenue_gap_usd     SET TAGS ('sensitivity' = 'internal')
```
  -> OK

```sql
ALTER TABLE apex_recon.gold.dispute_queue ALTER COLUMN revenue_at_risk_usd SET TAGS ('sensitivity' = 'internal')
```
  -> OK
