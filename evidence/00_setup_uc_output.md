
```sql
COMMENT ON CATALOG apex_recon IS 'Apex Exchange (fictional CTV SSP) revenue reconciliation: SSP auction logs vs DSP billing reports. Synthetic data.'
```
  -> OK

```sql
CREATE SCHEMA IF NOT EXISTS apex_recon.landing COMMENT 'Raw partner and platform files as delivered (UC Volumes).'
```
  -> OK

```sql
CREATE SCHEMA IF NOT EXISTS apex_recon.bronze  COMMENT 'Raw ingested records, one table per source, via Auto Loader.'
```
  -> OK

```sql
CREATE SCHEMA IF NOT EXISTS apex_recon.silver  COMMENT 'Cleaned daily records (bad rows dropped by data-quality rules) plus deal and DSP reference tables.'
```
  -> OK

```sql
CREATE SCHEMA IF NOT EXISTS apex_recon.gold    COMMENT 'Reconciliation results and business-ready aggregates for Finance and Billing Ops.'
```
  -> OK

```sql
CREATE SCHEMA IF NOT EXISTS apex_recon.ml      COMMENT 'ML features, predictions, models and evaluation artifacts.'
```
  -> OK

```sql
CREATE SCHEMA IF NOT EXISTS apex_recon.ops     COMMENT 'Governance (access table, row filter and mask functions) and the live case-status view over Lakebase.'
```
  -> OK

```sql
CREATE VOLUME IF NOT EXISTS apex_recon.landing.raw
  COMMENT 'Landing zone: ssp_logs (JSON.gz, hourly UTC) and dsp_reports/<dsp> (CSV, daily).'
```
  -> OK

```sql
COMMENT ON VOLUME apex_recon.landing.raw IS 'Landing zone: ssp_logs (JSON.gz, hourly UTC) and dsp_reports/<dsp> (CSV, daily).'
```
  -> OK

```sql
CREATE SCHEMA IF NOT EXISTS apex_recon.serving COMMENT 'Lakebase synced tables: gold data served to the Reconciliation Workbench app from Postgres.'
```
  -> OK
