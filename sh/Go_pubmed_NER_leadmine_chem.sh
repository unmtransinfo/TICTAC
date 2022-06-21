#!/bin/sh
###
#
printf "Executing: %s\n" "$(basename $0)"
#
cwd=$(pwd)
#
NM_ROOT="$(cd $HOME/../app/nextmove; pwd)"
LIBDIR="$(cd $HOME/../app/lib; pwd)"
#
TCRDDATADIR="$(cd $HOME/../data/TCRD/data; pwd)"
#
date
#
#############################################################################
# Chemical NER, with default LeadMine dictionary and resolver. 
java -jar ${LIBDIR}/unm_biocomp_nextmove-0.0.1-SNAPSHOT-jar-with-dependencies.jar \
	-v -textcol 6 -idcol 1 \
	-i ${TCRDDATADIR}/pubmed.tsv.gz \
	-o ${TCRDDATADIR}/pubmed_leadmine.tsv
#
#############################################################################
#
