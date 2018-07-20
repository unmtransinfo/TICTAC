SELECT
	itv.intervention_type,
	COUNT(DISTINCT itv.id) AS "id_unique_count",
	COUNT(DISTINCT itv.name) AS "name_unique_count"
FROM
	ctgov.interventions itv
GROUP BY
	itv.intervention_type
ORDER BY
	itv.intervention_type
	;
--
