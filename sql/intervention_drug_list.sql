SELECT
	itv.id,
	itv.nct_id,
	itv.name
FROM
	ctgov.interventions itv
WHERE
	itv.intervention_type = 'Drug'
ORDER BY
	itv.name
	;
--
