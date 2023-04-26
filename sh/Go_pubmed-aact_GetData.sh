#!/bin/bash
###
#
T0=$(date +%s)
#
printf "Executing: $(basename $0)\n"
#
cwd=$(pwd)
DATADIR="${cwd}/data"
#
date
###
# 
cat $DATADIR/aact_study_refs.tsv |sed -e '1d' \
	|awk -F '\t' '{print $4}' \
	|sort -nu \
	>$DATADIR/aact_study_refs.pmid
# 
printf "PubMed IDs (from AACT): $(cat $DATADIR/aact_study_refs.pmid |wc -l)\n"
###
# Slow
python3 -m BioClients.pubmed.Client get_record \
	--i $DATADIR/aact_study_refs.pmid \
	--o $DATADIR/aact_study_refs_pubmed-records.tsv
#
printf "Elapsed time: %ds\n" "$[$(date +%s) - ${T0}]"
#
