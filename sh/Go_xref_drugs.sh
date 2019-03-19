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
${cwd}/python/csv_utils.py \
	--csv2tsv \
	--i data/aact_drugs_smi_pubchem_cid2inchi.csv \
	--o data/aact_drugs_smi_pubchem_cid2inchi.tsv
	
#
cat data/aact_drugs_smi_pubchem_cid2inchi.tsv \
	|awk -F '\t' '{print $3}' \
	|sed -e '1d' \
	|sed -e 's/"//g' \
	>data/aact_drugs_smi_pubchem.inchi
#
${cwd}/python/chembl_inchi_lookup.py \
	--i data/aact_drugs_smi_pubchem.inchi \
	--o data/aact_drugs_inchi2chembl.tsv \
	--v
#
cat data/aact_drugs_inchi2chembl.tsv \
	|awk -F '\t' '{print $1}' \
	|sed -e '1d' \
	|sort -u \
	>data/aact_drugs_inchi2chembl.chemblid
#
###
#
${cwd}/python/chembl_fetchbyid.py -v \
	--i data/aact_drugs_inchi2chembl.chemblid \
	--o data/aact_drugs_chembl_activity_pchembl.tsv \
	cid2Activity
#
${cwd}/python/csv_utils.py \
	--i data/aact_drugs_chembl_activity_pchembl.tsv --tsv \
	--coltag "target_chembl_id" \
	--extractcol \
	|sort -u \
	>data/aact_drugs_chembl_target.chemblid
#
${cwd}/python/chembl_fetchbyid.py -v \
	--i data/aact_drugs_chembl_target.chemblid \
	--o data/aact_drugs_chembl_target_component.tsv \
	tid2Targetcomponents
#
###
#
${cwd}/python/csv_utils.py \
	--i data/aact_drugs_chembl_activity_pchembl.tsv --tsv \
	--coltag "document_chembl_id" \
	--extractcol \
	|sort -u \
	>data/aact_drugs_chembl_document.chemblid
#
${cwd}/python/chembl_fetchbyid.py -v \
	--i data/aact_drugs_chembl_document.chemblid \
	--o data/aact_drugs_chembl_document.tsv \
	did2Documents
#
date
#
