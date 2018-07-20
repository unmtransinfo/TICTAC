SELECT
	s.study_type,
	COUNT(DISTINCT s.nct_id) AS "id_unique_count",
	COUNT(DISTINCT s.brief_title) AS "brief_title_unique_count"
FROM
	ctgov.studies s
GROUP BY
	s.study_type
ORDER BY
	s.study_type
	;
--
