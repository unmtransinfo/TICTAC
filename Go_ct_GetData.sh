#!/bin/bash
#############################################################################
### CTTI = Clinical Trials Transformation Initiative
### AACT = Aggregate Analysis of ClinicalTrials.gov
### See https://aact.ctti-clinicaltrials.org/.
### According to website (July 2018), data is refreshed monthly.
#############################################################################
#
set -x
#
DBHOST="aact-db.ctti-clinicaltrials.org"
DBNAME="aact"
#
cwd=$(pwd)
DATADIR="${cwd}/data"
#
ARGS="-Atq -h $DBHOST -d $DBNAME"
###
DRUGFILE="$DATADIR/aact_drugs.tsv"
#Drugs:
printf "itv.id\titv.nct_id\titv.name\n" >$DRUGFILE
psql -F $'\t' $ARGS \
        -c "SELECT itv.id, itv.nct_id, itv.name FROM interventions itv WHERE itv.intervention_type ='Drug'" \
	>>$DRUGFILE
#
###
#Keywords:
KEYWORDFILE="$DATADIR/aact_keywords.tsv"
printf "kwd.id\tkwd.nct_id\tkwd.name\n" >$KEYWORDFILE
psql -F $'\t' $ARGS \
        -c "SELECT kwd.id, kwd.nct_id, kwd.name FROM ctgov.keywords kwd" \
	>>$KEYWORDFILE
#
###
#Conditions:
CONDITIONFILE="$DATADIR/aact_conditions.tsv"
printf "cnd.id\tcnd.nct_id\tcnd.name\n" >$CONDITIONFILE
psql -F $'\t' $ARGS \
        -c "SELECT cnd.id, cnd.nct_id, cnd.name FROM ctgov.conditions cnd" \
	>>$CONDITIONFILE
#
###
#Conditions_MeSH:
MESHCONDITIONFILE="$DATADIR/aact_conditions_mesh.tsv"
printf "bcnd_msh.id\tbcnd_msh.nct_id\tbcnd_msh.mesh_term\n" >$MESHCONDITIONFILE
psql -F $'\t' $ARGS \
        -c "SELECT bcnd_msh.id, bcnd_msh.nct_id, bcnd_msh.mesh_term FROM ctgov.browse_conditions bcnd_msh" \
	>>$MESHCONDITIONFILE
#
###
#Brief Summaries:
SUMMARYFILE=$DATADIR/aact_summaries.tsv
printf "bsumm.id\tbsumm.nct_id\tbsumm.description\n" >$SUMMARYFILE
psql -F $'\t' $ARGS \
        -f sql/summary_list.sql \
	>>$SUMMARYFILE
#
###
#Descriptions:
DESCRIPTIONFILE=$DATADIR/aact_descriptions.tsv
printf "ddesc.id\tddesc.nct_id\tddesc.description\n" 
psql -F $'\t' $ARGS \
        -f sql/description_list.sql \
	>>$DESCRIPTIONFILE
#
