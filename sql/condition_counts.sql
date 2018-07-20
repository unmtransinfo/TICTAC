SELECT
	COUNT(DISTINCT c.id) AS "id_unique_count",
	COUNT(DISTINCT c.nct_id) AS "nct_id_unique_count",
	COUNT(DISTINCT c.name) AS "name_unique_count"
FROM
	ctgov.conditions c
	;
--
SELECT
	COUNT(DISTINCT bc.id) AS "id_unique_count",
	COUNT(DISTINCT bc.nct_id) AS "nct_id_unique_count",
	COUNT(DISTINCT bc.mesh_term) AS "mesh_term_unique_count"
FROM
	ctgov.browse_conditions bc
	;
--
