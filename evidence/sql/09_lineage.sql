-- Unity Catalog lineage captured automatically for the build (system.access.table_lineage), current tables only
WITH current_tables AS (
  SELECT concat(table_catalog, '.', table_schema, '.', table_name) AS t FROM apex_recon.information_schema.tables
)
SELECT source_table_full_name, target_table_full_name, count(*) AS lineage_events, max(event_time) AS last_seen
FROM system.access.table_lineage
WHERE source_table_full_name IN (SELECT t FROM current_tables) AND target_table_full_name IN (SELECT t FROM current_tables)
GROUP BY 1, 2 ORDER BY 2, 1;
