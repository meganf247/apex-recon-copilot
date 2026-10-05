
```sql
COMMENT ON CATALOG apex_recon IS 'Apex Exchange (fictional CTV SSP) revenue reconciliation: SSP logs vs DSP billing reports vs publisher ad server reports. Synthetic data.'
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
CREATE SCHEMA IF NOT EXISTS apex_recon.silver  COMMENT 'Cleaned, normalized records: UTC dates, USD amounts, canonical deal IDs.'
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
CREATE SCHEMA IF NOT EXISTS apex_recon.ops     COMMENT 'Operational reference data (partner team assignments) and governance helpers.'
```
  -> OK

```sql
CREATE VOLUME IF NOT EXISTS apex_recon.landing.raw
  COMMENT 'Landing zone: ssp_logs (JSON.gz, hourly UTC), dsp_reports (CSV, 3 partner formats), publisher_reports (CSV, ad server exports), reference, history.'
```
  -> OK
