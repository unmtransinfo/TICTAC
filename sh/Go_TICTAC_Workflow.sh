#!/bin/bash
#############################################################################
# Dependencies:
#   * NextMove LeadMine (3.14.1 ok)
#   * https://github.com/unmtransinfo/nextmove-tools (LeadMine API client)
###
#
set -e
#
function MessageBreak {
  printf "============================================\n"
  printf "=== [%s] %s\n" "$(date +'%Y-%m-%d:%H:%M:%S')" "$1"
}
#
T0=$(date +%s)
#
MessageBreak "Starting: $(basename $0)"
#
DATE=$(date +'%Y%m%d')
#
cwd=$(pwd)
LOGDIR="${cwd}/data/logs"
#
if [ ! -e ${LOGDIR} ]; then
	mkdir -p ${LOGDIR}
fi
###
# Extract selected data from AACT via psql queries.
${cwd}/sh/Go_aact_GetData.sh \
	>& ${LOGDIR}/Go_aact_GetData-${DATE}.log
#
###
# From MeSH disease terms, build NextMove dictionaries.
${cwd}/sh/Go_BuildDicts_MeSH.sh \
	>& ${LOGDIR}/Go_BuildDicts_MeSH-${DATE}.log
#
###
# NextMove Leadmine:
# (1) Chemical NER on AACT drug intervention names.
# (2) Disease/phenotype NER on AACT descriptions, using custom dictionaries.
${cwd}/sh/Go_aact_NER_leadmine_chem.sh \
	>& ${LOGDIR}/Go_aact_NER_leadmine_chem-${DATE}.log
${cwd}/sh/Go_aact_NER_leadmine_disease.sh \
	>& ${LOGDIR}/Go_aact_NER_leadmine_disease-${DATE}.log
#
###
# JensenLab Tagger:
# Disease/phenotype NER on AACT descriptions, using JensenLab dictionary.
${cwd}/sh/Go_aact_NER_tagger_disease.sh
	>& ${LOGDIR}/Go_aact_NER_tagger_disease-${DATE}.log
#
###
# Target NER on AACT descriptions, using JensenLab dictionary.
# Minimal expectation, but need to show lack of NER mentions.
${cwd}/sh/Go_aact_NER_tagger_target.sh \
	>& ${LOGDIR}/Go_aact_NER_tagger_target-${DATE}.log
# Twitter is our arbitrary control:
${cwd}/sh/Go_twitter_GetData.sh \
	>& ${LOGDIR}/Go_twitter_GetData-${DATE}.log
${cwd}/sh/Go_twitter_NER_tagger_target.sh \
	>& ${LOGDIR}/Go_twitter_NER_tagger_target-${DATE}.log
#
###
# Uses (1) PubChem API and (2) ChEMBL API.
# Query using SMILES from LeadMine. InChIkeys from PubChem used for ChEMBL.
${cwd}/sh/Go_pubchem_GetXrefs.sh \
	>& ${LOGDIR}/Go_pubchem_GetXrefs-${DATE}.log
${cwd}/sh/Go_chembl_GetXrefs.sh \
	>& ${LOGDIR}/Go_chembl_GetXrefs-${DATE}.log
#
###
# Chemical NER on PubMed abstracts, with default LeadMine dictionary and resolver.
# PMIDs from ChEMBL activities.
${cwd}/sh/Go_pubmed-chembl_GetData.sh \
	>& ${LOGDIR}/Go_pubmed-chembl_GetData-${DATE}.log
${cwd}/sh/Go_pubmed-chembl_NER_leadmine_chem.sh \
	>& ${LOGDIR}/Go_pubmed-chembl_NER_leadmine_chem-${DATE}.log
#
###
# Target metadata from TCRD:
#mysql -h tcrd.kmc.io -D tcrd -u tcrd -c "source tcrd_targets.sql" \
python3 -m BioClients.idg.tcrd.Client listTargets --o ${cwd}/data/tcrd_targets.tsv
###
# Describe datasets; analyze results.
#Rscript -e "rmarkdown::render('${cwd}/R/aact_drugtargets.Rmd', knit_root_dir='${cwd}', output_dir='${cwd}/data', output_file='aact_drugtargets.html', clean=T)"
#
#
printf "Elapsed time: %ds\n" "$[$(date +%s) - ${T0}]"
#
