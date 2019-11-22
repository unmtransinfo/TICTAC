SELECT
	ROUND(AVG(LENGTH(description)), 2) AS "summary_len_mean"
FROM brief_summaries ;
SELECT
	ROUND(AVG(LENGTH(description)), 2) AS "description_len_mean"
FROM detailed_descriptions ;
