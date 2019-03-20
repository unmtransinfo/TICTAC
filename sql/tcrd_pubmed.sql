SELECT
	id,
	title,
	journal,
	date,
	authors,
	REPLACE(abstract, '\n', ' ') AS abstract
FROM
	pubmed
	;
