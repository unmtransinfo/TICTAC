SELECT
	id,
	nct_id,
	TRIM(BOTH E'\\t' FROM REGEXP_REPLACE(description, E'[\\n\\r] *', ' ', 'g')) AS "description"
FROM
	detailed_descriptions
	;
