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
cat $DATADIR/aact_drugs_chembl_document.tsv |sed -e '1d' \
	|awk -F '\t' '{print $13}' \
	|sort -nu \
	>$DATADIR/aact_drugs_chembl_document.pmid
# 
printf "PubMed IDs (from ChEMBL): $(cat $DATADIR/aact_drugs_chembl_document.pmid |wc -l)\n"
###
# Slow
python3 -m BioClients.pubmed.Client get_record \
	--i $DATADIR/aact_drugs_chembl_document.pmid \
	--o $DATADIR/aact_drugs_chembl_document_pubmed-records.tsv
#
printf "Elapsed time: %ds\n" "$[$(date +%s) - ${T0}]"
#
