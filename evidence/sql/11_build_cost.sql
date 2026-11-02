-- What this build actually costs to run, from system billing tables at list price (this workspace, October 2026).
-- The SQL warehouse is a shared starter warehouse, so its cost isn't attributed here.
SELECT CASE WHEN u.usage_metadata.job_id = '800507315624085' THEN 'build job (notebooks + ai_query drafting)'
            WHEN u.usage_metadata.dlt_pipeline_id = '7e5bc896-605c-44f6-a2e3-039922e893a9' THEN 'Lakeflow pipeline'
            WHEN u.usage_metadata.dlt_pipeline_id IN ('48cbab11-7eab-4c56-90ea-ec35cee07631', '4b1184df-f2c9-46a0-a0aa-9dc08a9f151d') THEN 'Lakebase sync'
            WHEN u.usage_metadata.project_id IS NOT NULL THEN 'Lakebase (Postgres compute + storage)'
            WHEN u.usage_metadata.app_name = 'apex-recon-workbench' THEN 'Databricks App (always on)' END AS component,
       u.billing_origin_product AS product,
       round(sum(u.usage_quantity), 2) AS dbus,
       round(sum(u.usage_quantity * p.pricing.effective_list.default), 2) AS list_usd,
       count(DISTINCT u.usage_date) AS days_with_usage
FROM system.billing.usage u
LEFT JOIN system.billing.list_prices p ON p.sku_name = u.sku_name AND u.usage_start_time >= p.price_start_time
     AND (p.price_end_time IS NULL OR u.usage_start_time < p.price_end_time)
WHERE u.workspace_id = '7474649371849429' AND u.usage_date >= '2026-10-01' AND u.usage_date < '2026-11-01'
  AND (u.usage_metadata.job_id = '800507315624085'
       OR u.usage_metadata.dlt_pipeline_id IN ('7e5bc896-605c-44f6-a2e3-039922e893a9', '48cbab11-7eab-4c56-90ea-ec35cee07631',
                                            '4b1184df-f2c9-46a0-a0aa-9dc08a9f151d')
       OR u.usage_metadata.app_name = 'apex-recon-workbench'
       OR (u.billing_origin_product = 'LAKEBASE' AND u.usage_metadata.project_id IS NOT NULL))
GROUP BY 1, 2 ORDER BY list_usd DESC;

SELECT count(*) AS successful_build_runs, round(avg((end_time - start_time) / 60000), 1) AS avg_minutes
FROM (SELECT run_id, max(period_end_time) AS end_time_ts, min(period_start_time) AS start_time_ts,
             unix_millis(max(period_end_time)) AS end_time, unix_millis(min(period_start_time)) AS start_time
      FROM system.lakeflow.job_run_timeline
      WHERE workspace_id = '7474649371849429' AND job_id = '800507315624085' AND period_start_time >= '2026-10-01' AND period_start_time < '2026-11-01'
      GROUP BY run_id HAVING max_by(result_state, period_end_time) = 'SUCCEEDED');
