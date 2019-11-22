SELECT
	rg.result_type,
	COUNT(DISTINCT rg.nct_id) AS "nct_id_count",
	COUNT(DISTINCT rg.title) AS "title_count"
FROM
	result_groups rg
GROUP BY
	rg.result_type
ORDER BY
	rg.result_type
	;
--
