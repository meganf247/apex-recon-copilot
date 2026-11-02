-- Apex Exchange CTV Revenue Reconciliation Copilot: Unity Catalog foundation.
-- The apex_recon catalog is pre-provisioned with external S3 storage.

COMMENT ON CATALOG apex_recon IS 'Apex Exchange (fictional CTV SSP) revenue reconciliation: SSP auction logs vs DSP billing reports. Synthetic data.';

CREATE SCHEMA IF NOT EXISTS apex_recon.landing COMMENT 'Raw partner and platform files as delivered (UC Volumes).';
CREATE SCHEMA IF NOT EXISTS apex_recon.bronze  COMMENT 'Raw ingested records, one table per source, via Auto Loader.';
CREATE SCHEMA IF NOT EXISTS apex_recon.silver  COMMENT 'Cleaned daily records (bad rows dropped by data-quality rules) plus deal and DSP reference tables.';
CREATE SCHEMA IF NOT EXISTS apex_recon.gold    COMMENT 'Reconciliation results and business-ready aggregates for Finance and Billing Ops.';
CREATE SCHEMA IF NOT EXISTS apex_recon.ml      COMMENT 'ML features, predictions, models and evaluation artifacts.';
CREATE SCHEMA IF NOT EXISTS apex_recon.ops     COMMENT 'Governance (access table, row filter and mask functions) and the live case-status view over Lakebase.';

CREATE VOLUME IF NOT EXISTS apex_recon.landing.raw
  COMMENT 'Landing zone: ssp_logs (JSON.gz, hourly UTC) and dsp_reports/<dsp> (CSV, daily).';
COMMENT ON VOLUME apex_recon.landing.raw IS 'Landing zone: ssp_logs (JSON.gz, hourly UTC) and dsp_reports/<dsp> (CSV, daily).';

CREATE SCHEMA IF NOT EXISTS apex_recon.serving COMMENT 'Lakebase synced tables: gold data served to the Reconciliation Workbench app from Postgres.';

-- Governance objects used by the pipeline (src/02_pipeline.py) and the publish step (src/04_publish.sql).
CREATE TABLE IF NOT EXISTS apex_recon.ops.recon_access (
  principal        STRING  COMMENT 'User email or service principal application ID',
  partner_team     STRING  COMMENT 'Partner team whose DSPs this principal may see (Atlantic, Pacific, Central, EMEA), or * for all',
  can_see_revenue  BOOLEAN COMMENT 'TRUE for Finance: may see USD amounts; FALSE: USD columns are masked'
) COMMENT 'Access entitlements for reconciliation data. Drives the partner row filter and the revenue column mask.';

-- Seed entitlements (idempotent; other principals such as the app service principal are added by their own grants file)
MERGE INTO apex_recon.ops.recon_access t
USING (SELECT 'megan.fogal@databricks.com' AS principal, '*' AS partner_team, TRUE AS can_see_revenue  -- Finance lead (build owner)
       UNION ALL SELECT 'pm.atlantic@apexexchange.example', 'Atlantic', FALSE                          -- partner manager, Atlantic team
       UNION ALL SELECT 'pm.emea@apexexchange.example', 'EMEA', FALSE) s                               -- partner manager, EMEA team
ON t.principal = s.principal
WHEN MATCHED THEN UPDATE SET * WHEN NOT MATCHED THEN INSERT *;

CREATE OR REPLACE FUNCTION apex_recon.ops.partner_access_filter(team STRING)
RETURNS BOOLEAN
COMMENT 'Row filter: a principal sees a row only if ops.recon_access grants them that partner team (or * for all teams).'
RETURN EXISTS (SELECT 1 FROM apex_recon.ops.recon_access a
               WHERE a.principal = current_user() AND (a.partner_team = '*' OR a.partner_team = team));

CREATE OR REPLACE FUNCTION apex_recon.ops.finance_only_usd(amount DOUBLE)
RETURNS DOUBLE
COMMENT 'Column mask: USD amounts are visible only to principals with can_see_revenue in ops.recon_access; others see NULL.'
RETURN CASE WHEN EXISTS (SELECT 1 FROM apex_recon.ops.recon_access a
                         WHERE a.principal = current_user() AND a.can_see_revenue) THEN amount ELSE NULL END;
