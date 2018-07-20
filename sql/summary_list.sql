SELECT
	bsumm.id,
	bsumm.nct_id,
	TRIM(BOTH E' \\t' FROM REGEXP_REPLACE(bsumm.description, E'\\n *', ' ', 'g')) AS "description"
FROM
	ctgov.brief_summaries bsumm
	;
