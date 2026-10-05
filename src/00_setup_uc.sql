-- Apex Exchange CTV Revenue Reconciliation Copilot: Unity Catalog foundation.
-- The apex_recon catalog is pre-provisioned with external S3 storage.

COMMENT ON CATALOG apex_recon IS 'Apex Exchange (fictional CTV SSP) revenue reconciliation: SSP logs vs DSP billing reports vs publisher ad server reports. Synthetic data.';

CREATE SCHEMA IF NOT EXISTS apex_recon.landing COMMENT 'Raw partner and platform files as delivered (UC Volumes).';
CREATE SCHEMA IF NOT EXISTS apex_recon.bronze  COMMENT 'Raw ingested records, one table per source, via Auto Loader.';
CREATE SCHEMA IF NOT EXISTS apex_recon.silver  COMMENT 'Cleaned, normalized records: UTC dates, USD amounts, canonical deal IDs.';
CREATE SCHEMA IF NOT EXISTS apex_recon.gold    COMMENT 'Reconciliation results and business-ready aggregates for Finance and Billing Ops.';
CREATE SCHEMA IF NOT EXISTS apex_recon.ml      COMMENT 'ML features, predictions, models and evaluation artifacts.';
CREATE SCHEMA IF NOT EXISTS apex_recon.ops     COMMENT 'Operational reference data (partner team assignments) and governance helpers.';

CREATE VOLUME IF NOT EXISTS apex_recon.landing.raw
  COMMENT 'Landing zone: ssp_logs (JSON.gz, hourly UTC), dsp_reports (CSV, 3 partner formats), publisher_reports (CSV, ad server exports), reference, history.';

CREATE SCHEMA IF NOT EXISTS apex_recon.serving COMMENT 'Lakebase synced tables: gold data served to the Reconciliation Workbench app from Postgres.';
