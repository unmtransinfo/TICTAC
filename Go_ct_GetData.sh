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
ARGS="-Atq -h $DBHOST -d $DBNAME"
###
#Drugs:
printf "itv.id\titv.nct_id\titv.name\n" >data/drugs.tsv
psql -F $'\t' $ARGS \
        -c "SELECT itv.id, itv.nct_id, itv.name FROM interventions itv WHERE itv.intervention_type ='Drug'" \
	>> data/drugs.tsv
#
###
#Keywords:
printf "kwd.id\tkwd.nct_id\tkwd.name\n" > data/keywords.tsv
psql -F $'\t' $ARGS \
        -c "SELECT kwd.id, kwd.nct_id, kwd.name FROM ctgov.keywords kwd" \
	>> data/keywords.tsv
#
###
#Conditions:
printf "cnd.id\tcnd.nct_id\tcnd.name\n" > data/conditions.tsv
psql -F $'\t' $ARGS \
        -c "SELECT cnd.id, cnd.nct_id, cnd.name FROM ctgov.conditions cnd" \
	>> data/conditions.tsv
#
###
#Conditions_MeSH:
printf "bcnd_msh.id\tbcnd_msh.nct_id\tbcnd_msh.mesh_term\n" > data/conditions_mesh.tsv
psql -F $'\t' $ARGS \
        -c "SELECT bcnd_msh.id, bcnd_msh.nct_id, bcnd_msh.mesh_term FROM ctgov.browse_conditions bcnd_msh" \
	>> data/conditions_mesh.tsv
#
###
#Brief Summaries:
printf "bsumm.id\tbsumm.nct_id\tbsumm.description\n" > data/summaries.tsv
psql -F $'\t' $ARGS \
        -f sql/summary_list.sql \
	>> data/summaries.tsv
#
###
#Descriptions:
printf "ddesc.id\tddesc.nct_id\tddesc.description\n" > data/descriptions.tsv
psql -F $'\t' $ARGS \
        -f sql/description_list.sql \
	>> data/descriptions.tsv
#
