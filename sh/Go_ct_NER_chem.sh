#!/bin/sh
#############################################################################
#
cwd=$(pwd)
#
NM_ROOT="/home/app/nextmove"
#LEADMINE_JAR="${NM_ROOT}/leadmine-3.12/LeadMine/leadmine-3.12.jar"
LEADMINE_JAR="${NM_ROOT}/leadmine-3.13/bin/leadmine.jar"
#
DATADIR="$cwd/data"
#
#############################################################################
# Chemical NER (drug intervention names), with default LeadMine dictionary
# and resolver. Must identify drugs by intervention ID, since may be multiple
# drugs per trial ID (NCT_ID).
###
${cwd}/sh/leadmine_utils.sh \
	-i ${DATADIR}/aact_drugs.tsv \
	-textcol 3 -unquote -idcol 1 \
	-o ${DATADIR}/aact_drugs_leadmine.tsv \
	-v
#
#
