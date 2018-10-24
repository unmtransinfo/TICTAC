--
SELECT
	ctgov_group_code,
	COUNT(DISTINCT nct_id) AS "id_unique_count",
	SUM(count) AS "count_total"
FROM
	outcome_counts
GROUP BY
	ctgov_group_code
ORDER BY
	id_unique_count	DESC
	;
--
-- LIMIT 20
