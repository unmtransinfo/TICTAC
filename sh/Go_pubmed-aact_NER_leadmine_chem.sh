#!/bin/bash
###
# Text mining PubMed publications referenced by clinical trials.
###
printf "Executing: %s\n" "$(basename $0)"
#
date
#
T0=$(date +%s)
#
cwd=$(pwd)
#
NM_ROOT="$(cd $HOME/../app/nextmove; pwd)"
LIBDIR="$(cd $HOME/../app/lib; pwd)"
#
DATADIR="${cwd}/data"
#
#
#############################################################################
# Chemical NER, with default LeadMine dictionary and resolver. 
java -jar ${LIBDIR}/unm_biocomp_nextmove-0.0.1-SNAPSHOT-jar-with-dependencies.jar \
	-v -textcol 3 -idcol 1 \
	-i $DATADIR/aact_study_refs_pubmed-records.tsv \
	-o $DATADIR/aact_study_refs_pubmed-records_leadmine.tsv
#
#
printf "Elapsed time: %ds\n" "$[$(date +%s) - ${T0}]"
#
