#!/bin/sh
#############################################################################
# We use the "pubmed" table from TCRD.
#############################################################################
#
cwd=$(pwd)
#
NM_ROOT="/home/app/nextmove"
#
#DATADIR="$cwd/data"
DATADIR="/home/data/TCRD/data"
#
#
#############################################################################
# Chemical NER, with default LeadMine dictionary and resolver. 
###
${cwd}/sh/leadmine_utils.sh \
	-i ${DATADIR}/pubmed.tsv.gz \
	-textcol 6 -idcol 1 \
	-o ${DATADIR}/pubmed_leadmine.tsv \
	-v
#
#############################################################################
#
