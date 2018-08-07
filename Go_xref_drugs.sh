#!/bin/sh
#
pubchem_mols2ids.py \
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
pubchem_query.py \
	--i data/aact_drugs_smi_pubchem.cid \
	--cids2inchi \
	--o data/aact_drugs_smi_pubchem_cid2inchi.csv \
	--v
#
csv_utils.py \
	--csv2tsv \
	--i data/aact_drugs_smi_pubchem_cid2inchi.csv \
	--o data/aact_drugs_smi_pubchem_cid2inchi.tsv
	
#
cat data/aact_drugs_smi_pubchem_cid2inchi.tsv \
	|awk -F '\t' '{print $3}' \
	|sed -e '1d' \
	|sed -e 's/"//g' \
	>data/aact_drugs_smi_pubchem.inchi \
#
chembl_inchi_lookup.py \
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
python/chembl_fetchbyid.py \
	--i data/aact_drugs_inchi2chembl.chemblid \
	--o data/aact_drugs_chembl_activity_pchembl.tsv \
	-v cid2Activity
#
csv_utils.py \
	--i data/aact_drugs_chembl_activity_pchembl.tsv --tsv \
	--coltag "target_chembl_id" \
	--extractcol \
	|sort -u \
	> data/aact_drugs_chembl_target.chemblid \
#
python/chembl_fetchbyid.py \
	--i data/aact_drugs_chembl_target.chemblid \
	--o data/aact_drugs_chembl_target_component.tsv \
	-v tid2Targetcomponents
#
