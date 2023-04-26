#!/bin/bash
###
# Text mining PubMed publications. Of interest are those
# referenced by clinical trials.
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
TCRDDATADIR="$(cd $HOME/../data/TCRD/data; pwd)"
#
pubmedfile="${TCRDDATADIR}/pubmed.tsv.gz"
#
#############################################################################
# Chemical NER, with default LeadMine dictionary and resolver. 
java -jar ${LIBDIR}/unm_biocomp_nextmove-0.0.1-SNAPSHOT-jar-with-dependencies.jar \
	-v -textcol 6 -idcol 1 \
	-i ${pubmedfile} \
	-o ${TCRDDATADIR}/pubmed_leadmine.tsv
#
#
printf "Elapsed time: %ds\n" "$[$(date +%s) - ${T0}]"
#
