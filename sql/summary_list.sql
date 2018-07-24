SELECT
	id,
	nct_id,
	TRIM(BOTH E'\\t' FROM REGEXP_REPLACE(description, E'\\n *', ' ', 'g')) AS "description"
FROM
	brief_summaries 
	;
