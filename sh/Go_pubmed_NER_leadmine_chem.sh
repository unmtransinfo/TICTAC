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
#Some processing errors due to newlines in abstracts(?).
${cwd}/sh/runsql_my.sh -h juniper.health.unm.edu -u $DBUSR -p $DBPW \
	-n tcrd \
	-f ${cwd}/sql/tcrd_pubmed.sql -c \
	|gzip -c \
	>${DATADIR}/pubmed.tsv.gz
#
#############################################################################
# Chemical NER, with default LeadMine dictionary and resolver. 
# total elapsed time: 02:25:46
# Many "badly formed line" errors to be investigated.
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
