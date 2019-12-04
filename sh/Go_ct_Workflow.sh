#!/bin/bash
#############################################################################
# Dependencies:
#   * NextMove LeadMine (3.14.1 ok)
#   * https://github.com/unmtransinfo/nextmove-tools (LeadMine API client)
###
#
set -e
set -x
#
DATE=$(date +'%Y%M%d')
#
cwd=$(pwd)
#
###
# Extract selected data from AACT via psql queries.
${cwd}/sh/Go_ct_GetData.sh \
	>& ${cwd}/data/Go_ct_GetData-${DATE}.log
#
###
# From MeSH disease terms, build NextMove dictionaries.
${cwd}/sh/Go_BuildDicts_MeSH.sh \
	>& ${cwd}/data/Go_BuildDicts_MeSH-${DATE}.log
#
###
# Chemical NER on PubMed abstracts, with default LeadMine dictionary and resolver.
# We use the "pubmed" table from TCRD, which includes references with targets or
# diseases according to JensenLab.
${cwd}/sh/Go_pubmed_NER_leadmine_chem.sh \
	>& ${cwd}/data/Go_pubmed_NER_leadmine_chem-${DATE}.log
#
###
# NextMove Leadmine:
# (1) Chemical NER on AACT drug intervention names.
# (2) Disease/phenotype NER on AACT descriptions, using custom dictionaries.
${cwd}/sh/Go_ct_NER_leadmine_chem.sh \
	>& ${cwd}/data/Go_ct_NER_leadmine_chem-${DATE}.log
${cwd}/sh/Go_ct_NER_leadmine_disease.sh \
	>& ${cwd}/data/Go_ct_NER_leadmine_disease-${DATE}.log
#
###
# JensenLab Tagger:
# Disease/phenotype NER on AACT descriptions, using JensenLab dictionary.
${cwd}/sh/Go_ct_NER_tagger_disease.sh
	>& ${cwd}/data/Go_ct_NER_tagger_disease-${DATE}.log
#
###
# Target NER on AACT descriptions, using JensenLab dictionary.
# Minimal expectation, but need to show lack of NER mentions.
${cwd}/sh/Go_ct_NER_tagger_target.sh \
	>& ${cwd}/data/Go_ct_NER_tagger_target-${DATE}.log
# Twitter is our arbitrary control:
${cwd}/sh/Go_twitter_NER_tagger_target.sh \
	>& ${cwd}/data/Go_twitter_NER_tagger_target-${DATE}.log
#
###
# Uses (1) PubChem API and (2) ChEMBL API.
# Query using SMILES from LeadMine.
${cwd}/sh/Go_xref_drugs.sh \
	>& ${cwd}/data/Go_xref_drugs-${DATE}.log
###
# Describe datasets; analyze results.
#Rscript -e "rmarkdown::render('${cwd}/R/aact_drugtargets.Rmd', knit_root_dir='${cwd}', output_dir='${cwd}/data', output_file='aact_drugtargets.html', clean=T)"
#
#
