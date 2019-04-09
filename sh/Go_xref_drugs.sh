#!/bin/bash
#############################################################################
### Mappings:
###  (PubChem)	SMILES	-->	CID
###  (PubChem)	CID	-->	INCHIKEY
###  (ChEMBL)	INCHIKEY	-->	MOLECULE_CHEMBL_ID
###  (ChEMBL)	MOLECULE_CHEMBL_ID	-->	ACTIVITY_ID
###  (ChEMBL)	ACTIVITY_ID	-->	TARGET_CHEMBL_ID
###  (ChEMBL)	TARGET_CHEMBL_ID	-->	COMPONENT_ID
###  (ChEMBL)	COMPONENT_ID	-->	ACCESSION
###  (ChEMBL)	ACTIVITY_ID	-->	DOCUMENT_CHEMBL_ID
###  (ChEMBL)	DOCUMENT_CHEMBL_ID	-->	PUBMED_ID
#############################################################################
cwd=$(pwd)
#
set -x
#
date
###
# Remove SMILES with wildcard '*' (not mappable to PubChem CIDs).
${cwd}/R/leadmine2smifile.R data/aact_drugs_leadmine.tsv \
	|grep -v '\*' \
	>data/aact_drugs_smi.smi
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
n_smi=$(cat data/aact_drugs_smi.smi |wc -l)
printf "SMILES (from LeadMine): %d\n" "${n_smi}"
n_cid=$(cat data/aact_drugs_smi_pubchem.cid |wc -l)
printf "CIDs (from PubChem): %d\n" ${n_cid}
printf "SMI2CID hit rate (from PubChem): (%d / %d = %.1f%%)\n" \
	${n_cid} ${n_smi} $(echo "100 * $n_cid / $n_smi" |bc)
###
# --cids2inchi gets both InChI and InChIKey
${cwd}/python/pubchem_query.py \
	--i data/aact_drugs_smi_pubchem.cid \
	--cids2inchi \
	--o data/aact_drugs_smi_pubchem_cid2ink.csv \
	--v
#
${cwd}/python/pandas_utils.py \
	--i data/aact_drugs_smi_pubchem_cid2ink.csv \
	--o data/aact_drugs_smi_pubchem_cid2ink.tsv \
	csv2tsv
#
${cwd}/python/pandas_utils.py \
	--i data/aact_drugs_smi_pubchem_cid2ink.tsv \
	--coltags "InChIKey" \
	|sed -e '1d' |sed -e 's/"//g' \
	>data/aact_drugs_smi_pubchem.ink
#
n_cid=$(cat data/aact_drugs_smi_pubchem.ink |wc -l)
printf "InChIKeys (from PubChem): %d\n" ${n_ink}
###
# 3334/3801 found
${cwd}/python/chembl_fetchbyid.py \
	--i data/aact_drugs_smi_pubchem.ink \
	--o data/aact_drugs_ink2chembl.tsv \
	inchikey2Mol
#
${cwd}/python/pandas_utils.py \
	--i data/aact_drugs_ink2chembl.tsv \
	--coltags "molecule_chembl_id" \
	selectcols \
	|sed -e '1d' |sort -u \
	>data/aact_drugs_ink2chembl.chemblid
#
n_chembl_mol=$(cat data/aact_drugs_ink2chembl.chemblid |wc -l)
printf "Mols (from ChEMBL): %d\n" ${n_chembl_mol}
#
###
#This takes several hours.
if [ "" ]; then
	${cwd}/python/chembl_fetchbyid.py -v \
		--i data/aact_drugs_ink2chembl.chemblid \
		--o data/aact_drugs_chembl_activity_pchembl.tsv \
		cid2Activity
fi
#
n_chembl_act=$(cat data/data/aact_drugs_chembl_activity_pchembl.tsv |sed -e '1d' |wc -l)
printf "Activities (from ChEMBL): %d\n" ${n_chembl_act}
#
${cwd}/python/pandas_utils.py \
	--i data/aact_drugs_chembl_activity_pchembl.tsv \
	--coltags "activity_id,target_chembl_id" \
	--o data/aact_drugs_chembl_act2tgt.tsv \
	selectcols
#
${cwd}/python/pandas_utils.py \
	--i data/aact_drugs_chembl_activity_pchembl.tsv \
	--coltags "target_chembl_id" \
	selectcols \
	|sed -e '1d' |sort -u \
	>data/aact_drugs_chembl_target.chemblid
#
n_chembl_tgt=$(cat data/data/aact_drugs_chembl_target.chemblid |wc -l)
printf "Targets (from ChEMBL): %d\n" ${n_chembl_tgt}
#
${cwd}/python/chembl_fetchbyid.py -v \
	--i data/aact_drugs_chembl_target.chemblid \
	--o data/aact_drugs_chembl_target_component.tsv \
	tid2Targetcomponents
#
n_chembl_tgtc=$(${cwd}/python/pandas_utils.py \
	--i data/data/aact_drugs_chembl_target_component.tsv \
	--coltags "component_id" \
	selectcols \
	|sed -e '1d' |wc -l)
printf "Target components (from ChEMBL): %d\n" ${n_chembl_tgtc}
###
# 
${cwd}/python/pandas_utils.py \
	--i data/aact_drugs_chembl_activity_pchembl.tsv \
	--coltags "document_chembl_id" \
	selectcols \
	|sed -e '1d' |sort -u \
	>data/aact_drugs_chembl_document.chemblid
#
n_chembl_doc=$(cat data/data/aact_drugs_chembl_document.chemblid |wc -l)
printf "Documents (from ChEMBL): %d\n" ${n_chembl_doc}
#
${cwd}/python/chembl_fetchbyid.py -v \
	--i data/aact_drugs_chembl_document.chemblid \
	--o data/aact_drugs_chembl_document.tsv \
	did2Documents
#
n_chembl_pmid=$(${cwd}/python/pandas_utils.py \
	--i data/data/aact_drugs_chembl_document.tsv \
	--coltags "pubmed_id" \
	selectcols \
	|sed -e '1d' |wc -l)
printf "PubMed IDs (from ChEMBL): %d\n" ${n_chembl_pmid}
#
date
#
