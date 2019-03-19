#!/bin/sh
#############################################################################
#############################################################################
#
cwd=$(pwd)
#
NM_ROOT="/home/app/nextmove"
#
#DATADIR="$cwd/data"
DATADIR="/home/data/TCRD/data"
#
date
#
#############################################################################
# Use "pubmed" table from TCRD:
#(2547706 rows in March 2019)
runsql_my.sh -h juniper.health.unm.edu -n tcrd -q 'SELECT * FROM PUBMED' -c \
	|gzip -c \
	>${DATADIR}/pubmed.tsv.gz
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
date
#
