SELECT
	document_type,
	COUNT(DISTINCT nct_id) AS "id_unique_count",
	COUNT(DISTINCT document_id) AS "document_id_count"
FROM
	documents
GROUP BY
	document_type
ORDER BY
	document_id_count DESC
LIMIT 10
	;
--
