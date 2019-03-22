#!/bin/bash
#
cwd=$(pwd)
#
set -x
#
date
#
${cwd}/python/pubchem_mols2ids.py \
	--v \
	--i data/aact_drugs_smi.smi \
	--o data/aact_drugs_smi_pubchem_cid.tsv
#
cat data/aact_drugs_smi_pubchem_cid.tsv \
	|awk -F '\t' '{print $2}' \
	|egrep -v '(^$|^0$|^NA$)' \
	|sort -nu \
	>data/aact_drugs_smi_pubchem.cid
#
${cwd}/python/pubchem_query.py \
	--i data/aact_drugs_smi_pubchem.cid \
	--cids2inchi \
	--o data/aact_drugs_smi_pubchem_cid2inchi.csv \
	--v
#
${cwd}/python/pandas_utils.py \
	--i data/aact_drugs_smi_pubchem_cid2inchi.csv \
	--o data/aact_drugs_smi_pubchem_cid2inchi.tsv \
	csv2tsv
#
cat data/aact_drugs_smi_pubchem_cid2inchi.tsv \
	|awk -F '\t' '{print $3}' \
	|sed -e '1d' |sed -e 's/"//g' \
	>data/aact_drugs_smi_pubchem.inchi
#
${cwd}/python/chembl_fetchbyid.py \
	--i data/aact_drugs_smi_pubchem.inchi \
	--o data/aact_drugs_inchi2chembl.tsv \
	inchi2Mol
#
cat data/aact_drugs_inchi2chembl.tsv \
	|awk -F '\t' '{print $13}' \
	|sed -e '1d' |sort -u \
	>data/aact_drugs_inchi2chembl.chemblid
#
###
#This takes several hours.
${cwd}/python/chembl_fetchbyid.py -v \
	--i data/aact_drugs_inchi2chembl.chemblid \
	--o data/aact_drugs_chembl_activity_pchembl.tsv \
	cid2Activity
#
#Extract "target_chembl_id"
cat data/aact_drugs_chembl_activity_pchembl.tsv \
	|awk -F '\t' '{print $20}' \
	|sed -e '1d' |sort -u \
	>data/aact_drugs_chembl_target.chemblid
#
${cwd}/python/chembl_fetchbyid.py -v \
	--i data/aact_drugs_chembl_target.chemblid \
	--o data/aact_drugs_chembl_target_component.tsv \
	tid2Targetcomponents
#
###
# Extract "document_chembl_id"
cat data/aact_drugs_chembl_activity_pchembl.tsv \
	|awk -F '\t' '{print $4}' \
	|sed -e '1d' |sort -u \
	>data/aact_drugs_chembl_document.chemblid
#
${cwd}/python/chembl_fetchbyid.py -v \
	--i data/aact_drugs_chembl_document.chemblid \
	--o data/aact_drugs_chembl_document.tsv \
	did2Documents
#
date
#
