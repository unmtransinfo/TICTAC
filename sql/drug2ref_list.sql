SELECT
	itv.id,
	itv.nct_id,
	itv.name,
	sref.pmid,
	sref.reference_type,
	sref.citation
FROM
	interventions itv
LEFT OUTER JOIN
	study_references sref ON sref.nct_id = itv.nct_id
WHERE
	itv.intervention_type = 'Drug'
AND
	sref.pmid IS NOT NULL
ORDER BY
	itv.name
	;
--
