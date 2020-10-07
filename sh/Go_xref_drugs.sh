#!/bin/bash
###
# Requires https://github.com/jeremyjyang/BioClients
#
#
printf "Executing: %s\n" "$(basename $0)"
#
cwd=$(pwd)
DATADIR="${cwd}/data"
#
date
###
# Remove SMILES with wildcard '*' (not mappable to PubChem CIDs).
${cwd}/R/leadmine2smifile.R $DATADIR/aact_drugs_leadmine.tsv \
	|grep -v '\*' \
	>$DATADIR/aact_drugs_smi.smi
#
python3 -m BioClients.pubchem.Client get_smi2cid \
	--i $DATADIR/aact_drugs_smi.smi \
	--o $DATADIR/aact_drugs_smi_pubchem_cid.tsv
#
#CID\tSMILES\tName
cat $DATADIR/aact_drugs_smi_pubchem_cid.tsv \
	|awk -F '\t' '{print $1}' \
	|sed '1d' \
	|egrep -v '(^$|^0$|^NA$)' \
	|sort -nu \
	>$DATADIR/aact_drugs_smi_pubchem.cid
#
n_smi=$(cat $DATADIR/aact_drugs_smi.smi |wc -l)
printf "SMILES (from LeadMine): %d\n" "${n_smi}"
n_cid=$(cat $DATADIR/aact_drugs_smi_pubchem.cid |wc -l)
printf "CIDs (from PubChem): %d\n" ${n_cid}
printf "SMI2CID hit rate (from PubChem): (%d / %d = %.1f%%)\n" \
	${n_cid} ${n_smi} $(echo "100 * $n_cid / $n_smi" |bc)
###
# Gets both InChI and InChIKey
#TTP Error 400: PUGREST.BadRequest (URL=https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/property/InChIKey,InChI/CSV)
python3 -m BioClients.pubchem.Client get_cid2inchi \
	--i $DATADIR/aact_drugs_smi_pubchem.cid \
	--o $DATADIR/aact_drugs_smi_pubchem_cid2ink.tsv
#
python3 -m BioClients.util.pandas.Utils selectcols --coltags "InChIKey" \
	--i $DATADIR/aact_drugs_smi_pubchem_cid2ink.tsv \
	|sed -e '1d' |sed -e 's/"//g' \
	>$DATADIR/aact_drugs_smi_pubchem.ink
#
n_ink=$(cat $DATADIR/aact_drugs_smi_pubchem.ink |wc -l)
printf "InChIKeys (from PubChem): %d\n" ${n_ink}
###
python3 -m BioClients.chembl.Client get_mol_by_inchikey \
	--i $DATADIR/aact_drugs_smi_pubchem.ink \
	--o $DATADIR/aact_drugs_ink2chembl.tsv
#
python3 -m BioClients.util.pandas.Utils selectcols --coltags "molecule_chembl_id" \
	--i $DATADIR/aact_drugs_ink2chembl.tsv \
	|sed -e '1d' |sort -u \
	>$DATADIR/aact_drugs_ink2chembl.chemblid
#
n_chembl_mol=$(cat $DATADIR/aact_drugs_ink2chembl.chemblid |wc -l)
printf "Mols (from ChEMBL): %d\n" ${n_chembl_mol}
#
###
python3 -m BioClients.chembl.Client get_activity_by_mol \
	--i $DATADIR/aact_drugs_ink2chembl.chemblid \
	--o $DATADIR/aact_drugs_chembl_activity.tsv
#
n_chembl_act=$(cat $DATADIR/aact_drugs_chembl_activity.tsv |sed -e '1d' |wc -l)
printf "Activities (from ChEMBL): %d\n" ${n_chembl_act}
#
python3 -m BioClients.util.pandas.Utils selectcols --coltags "target_chembl_id" \
	--i $DATADIR/aact_drugs_chembl_activity.tsv \
	|sed -e '1d' |sort -u \
	>$DATADIR/aact_drugs_chembl_target.chemblid
#
n_chembl_tgt=$(cat $DATADIR/aact_drugs_chembl_target.chemblid |wc -l)
printf "Targets (from ChEMBL): %d\n" ${n_chembl_tgt}
#
python3 -m BioClients.chembl.Client get_target_components \
	--i $DATADIR/aact_drugs_chembl_target.chemblid \
	--o $DATADIR/aact_drugs_chembl_target_component.tsv
#
n_chembl_tgtc=$(python3 -m BioClients.util.pandas.Utils selectcols --coltags "component_id" \
	--i $DATADIR/aact_drugs_chembl_target_component.tsv \
	|sed -e '1d' |wc -l)
printf "Target components (from ChEMBL): %d\n" ${n_chembl_tgtc}
###
# 
python3 -m BioClients.util.pandas.Utils selectcols --coltags "document_chembl_id" \
	--i $DATADIR/aact_drugs_chembl_activity.tsv \
	|sed -e '1d' |sort -u \
	>$DATADIR/aact_drugs_chembl_document.chemblid
#
n_chembl_doc=$(cat $DATADIR/aact_drugs_chembl_document.chemblid |wc -l)
printf "Documents (from ChEMBL): %d\n" ${n_chembl_doc}
#
python3 -m BioClients.chembl.Client get_document \
	--i $DATADIR/aact_drugs_chembl_document.chemblid \
	--o $DATADIR/aact_drugs_chembl_document.tsv
#
n_chembl_pmid=$(python3 -m BioClients.util.pandas.Utils selectcols --coltags "pubmed_id" \
	--i $DATADIR/aact_drugs_chembl_document.tsv \
	|sed -e '1d' |wc -l)
printf "PubMed IDs (from ChEMBL): %d\n" ${n_chembl_pmid}
#
python3 -m BioClients.pubchem.Client list_sources_assay \
	--o $DATADIR/chembl_sources.tsv
#
date
#
