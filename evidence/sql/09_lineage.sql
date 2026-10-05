-- Unity Catalog lineage captured automatically for the build (system.access.table_lineage)
SELECT source_table_full_name, target_table_full_name, count(*) AS lineage_events, max(event_time) AS last_seen
FROM system.access.table_lineage
WHERE (target_table_full_name LIKE 'apex_recon.%' OR source_table_full_name LIKE 'apex_recon.%')
  AND source_table_full_name IS NOT NULL AND target_table_full_name IS NOT NULL
GROUP BY 1, 2 ORDER BY 2, 1;
