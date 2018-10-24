--
SELECT
	d.primary_purpose,
	d.intervention_model,
	COUNT(DISTINCT d.nct_id) AS "id_unique_count"
FROM
	ctgov.designs d
WHERE
	d.intervention_model IS NOT NULL
GROUP BY
	d.primary_purpose, d.intervention_model
ORDER BY
	id_unique_count	DESC
LIMIT 20
	;
--
SELECT
	d.observational_model,
	d.time_perspective,
	COUNT(DISTINCT d.nct_id) AS "id_unique_count"
FROM
	ctgov.designs d
WHERE
	d.observational_model IS NOT NULL
GROUP BY
	d.observational_model, d.time_perspective
ORDER BY
	id_unique_count	DESC
LIMIT 20
	;
--
