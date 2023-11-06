#!/bin/bash
###

cwd="$(pwd)"

DATADIR="${cwd}/data"

###
# List conditions (N=1312 on 06-Nov-2023)
python3 -m BioClients.medline.genetics.Client list_conditions \
	--o $DATADIR/medline_genetics_conditions.tsv
#
###
# Extract IDs (names with hyphens instead of spaces, etc.)
cat $DATADIR/medline_genetics_conditions.tsv \
	|sed '1d' |awk -F '\t' '{print $2}' |sed '/^.*\///' \
	>$DATADIR/medline_genetics_conditions.id
###
# All associations for all conditions.
# (N=4264 on 06-Nov-2023)
#
python3 -m BioClients.medline.genetics.Client get_condition_genes \
	--i $DATADIR/medline_genetics_conditions.id \
	--o $DATADIR/medline_genetics_condition-gene_associations.tsv
###
# Associations include more condition xrefs than the conditions file. 
# So we extract a better conditions file, for xref-ing.
# Xrefs: ICD-10-CM, MeSH, OMIM, SNOMED_CT, GTR
# GTR = Genetics Testing Registry, but the IDs are UMLS CUIs.
# (N=1273 on 06-Nov-2023)
cat $DATADIR/medline_genetics_condition-gene_associations.tsv \
	|head -1 \
	|awk -F '\t' '{print $1 "\t" $2 "\t" $3 "\t" $4 "\t" $5 "\t" $6 "\t" $7}' \
	>$DATADIR/medline_genetics_conditions_xrefs.tsv
cat $DATADIR/medline_genetics_condition-gene_associations.tsv \
	|sed '1d' \
	|awk -F '\t' '{print $1 "\t" $2 "\t" $3 "\t" $4 "\t" $5 "\t" $6 "\t" $7}'  \
	|sort -u \
	>>$DATADIR/medline_genetics_conditions_xrefs.tsv
#
###
# For each condition, each xref type may include multiple IDs, comma-separated.
# Focus on SNOMED_CT (field #6).
#
cat $DATADIR/medline_genetics_conditions_xrefs.tsv \
	|sed '1d' \
        |awk -F '\t' '{print $6}' \
	|grep -v '^$' \
	|perl -pe 's/,/\n/g;' \
	|sort -nu \
	>$DATADIR/medline_genetics_conditions_xrefs_snomed.id
#
printf "Unique SNOMED_CT IDs: %d\n" "$(cat $DATADIR/medline_genetics_conditions_xrefs_snomed.id |wc -l)"
#
