#!/bin/bash
#############################################################################
### CTTI = Clinical Trials Transformation Initiative
### AACT = Aggregate Analysis of ClinicalTrials.gov
### See https://aact.ctti-clinicaltrials.org/.
### According to website (July 2018), data is refreshed monthly.
#############################################################################
### Identify drugs by intervention ID, since may be multiple
### drugs per trial (NCT_ID).
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
ARGS="-h $DBHOST -d $DBNAME"
###
STUDYFILE="$DATADIR/aact_studies.tsv"
psql $ARGS -c "COPY (SELECT nct_id,study_type,source,phase,overall_status,start_date,completion_date,enrollment,official_title FROM studies) TO STDOUT WITH (FORMAT CSV,HEADER,DELIMITER E'\t')" >$STUDYFILE
###
###
DRUGFILE="$DATADIR/aact_drugs.tsv"
#Drugs:
psql $ARGS -c "COPY (SELECT id, nct_id, name FROM interventions WHERE intervention_type ='Drug') TO STDOUT WITH (FORMAT CSV,HEADER,DELIMITER E'\t')" >$DRUGFILE
###
#Keywords:
KEYWORDFILE="$DATADIR/aact_keywords.tsv"
psql $ARGS -c "COPY (SELECT id, nct_id, name FROM keywords) TO STDOUT WITH (FORMAT CSV,HEADER,DELIMITER E'\t')" >$KEYWORDFILE
#
###
#Conditions:
CONDITIONFILE="$DATADIR/aact_conditions.tsv"
psql $ARGS -c "COPY (SELECT id, nct_id, name FROM conditions) TO STDOUT WITH (FORMAT CSV,HEADER,DELIMITER E'\t')" >$CONDITIONFILE
#
###
#Conditions_MeSH:
MESHCONDITIONFILE="$DATADIR/aact_conditions_mesh.tsv"
psql $ARGS -c "COPY (SELECT id, nct_id, mesh_term FROM browse_conditions) TO STDOUT WITH (FORMAT CSV,HEADER,DELIMITER E'\t')" >$MESHCONDITIONFILE
#
###
#Special handling required to clean newlines and tabs.
###
ARGS="-Atq -h $DBHOST -d $DBNAME"
#Brief Summaries:
SUMMARYFILE=$DATADIR/aact_summaries.tsv
printf "id\tnct_id\tdescription\n" >$SUMMARYFILE
psql -F $'\t' $ARGS -f sql/summary_list.sql >>$SUMMARYFILE
#
###
#Descriptions:
DESCRIPTIONFILE=$DATADIR/aact_descriptions.tsv
printf "id\tnct_id\tdescription\n" >$DESCRIPTIONFILE
psql -F $'\t' $ARGS -f sql/description_list.sql >>$DESCRIPTIONFILE
#
