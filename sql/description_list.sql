SELECT
	ddesc.id,
	ddesc.nct_id,
	TRIM(BOTH E'\\t' FROM REGEXP_REPLACE(ddesc.description, E'\\n *', ' ', 'g')) AS "description"
FROM
	ctgov.detailed_descriptions ddesc
	;
