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
#DATADIR="$cwd/data"
DATADIR="$(cd $HOME/../data/TCRD/data; pwd)"
#
date
#
#############################################################################
# TCRD "pubmed" table:
#(3879431 rows in May 2021)
python3 -m BioClients.idg.tcrd.Client listPublications -q \
	|gzip -c >${DATADIR}/pubmed.tsv.gz
#
#############################################################################
# Chemical NER, with default LeadMine dictionary and resolver. 
# total elapsed time: 02:25:46
# Missing (NULL) abstracts could be filtered to avoid error messages.
###
java -jar ${LIBDIR}/unm_biocomp_nextmove-0.0.1-SNAPSHOT-jar-with-dependencies.jar \
	-i ${DATADIR}/pubmed.tsv.gz \
	-textcol 6 -idcol 1 \
	-o ${DATADIR}/pubmed_leadmine.tsv \
	-v
#
#############################################################################
#
