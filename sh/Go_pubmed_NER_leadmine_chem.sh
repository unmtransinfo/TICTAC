#!/bin/sh
###
#
printf "Executing: %s\n" "$(basename $0)"
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
# Define DBUSR, DBPW:
. $HOME/.tcrd.sh
printf "DBUSR: \"%s\"; DBPW: \"%s\"\n" "${DBUSR}" "${DBPW}"
#
#(2547706 rows in March 2019)
#Some processing errors due to newlines in abstracts(?).
mysql -h juniper.health.unm.edu -u "$DBUSR" -p$DBPW -D tcrd \
	-e "source ${cwd}/sql/tcrd_pubmed.sql" \
	|gzip -c >${DATADIR}/pubmed.tsv.gz
#
#############################################################################
# Chemical NER, with default LeadMine dictionary and resolver. 
# total elapsed time: 02:25:46
# Many "badly formed line" errors to be investigated.
###
java -jar /home/app/lib/unm_biocomp_nextmove-0.0.1-SNAPSHOT-jar-with-dependencies.jar \
	-i ${DATADIR}/pubmed.tsv.gz \
	-textcol 6 -idcol 1 \
	-o ${DATADIR}/pubmed_leadmine.tsv \
	-v
#
#############################################################################
date
#
