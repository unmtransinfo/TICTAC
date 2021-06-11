#!/bin/bash
###
#
printf "Executing: $(basename $0)\n"
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
	|sed '1d' |awk -F '\t' '{print $1}' \
	|egrep -v '(^$|^0$|^NA$)' \
	|sort -nu \
	>$DATADIR/aact_drugs_smi_pubchem.cid
#
# Although SMILES not canonical, we preserve their precise text, to
# allow AACT to PubChem mapping.
#
n_smi=$(cat $DATADIR/aact_drugs_smi.smi |wc -l)
printf "SMILES (from LeadMine): ${n_smi}\n"
n_cid=$(cat $DATADIR/aact_drugs_smi_pubchem.cid |wc -l)
printf "CIDs (from PubChem): ${n_cid}\n"
printf "SMI2CID hit rate (from PubChem): (${n_cid} / ${n_smi} = %.1f%%)\n" $(echo "100 * $n_cid / $n_smi" |bc)
###
# Gets both InChI and InChIKey
#HTTP Error 400: PUGREST.BadRequest (URL=https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/property/InChIKey,InChI/CSV)
python3 -m BioClients.pubchem.Client get_cid2inchi \
	--i $DATADIR/aact_drugs_smi_pubchem.cid \
	--o $DATADIR/aact_drugs_smi_pubchem_cid2ink.tsv
#
python3 -m BioClients.util.pandas.Utils selectcols --coltags "InChIKey" \
	--i $DATADIR/aact_drugs_smi_pubchem_cid2ink.tsv \
	|sed -e '1d' |sed -e 's/"//g' \
	>$DATADIR/aact_drugs_smi_pubchem.ink
#
printf "InChIKeys (from PubChem): $(cat $DATADIR/aact_drugs_smi_pubchem.ink |wc -l)\n"
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
printf "Mols (from ChEMBL): $(cat $DATADIR/aact_drugs_ink2chembl.chemblid |wc -l)\n"
#
###
# ~12hr for 3711 mols, 2021-06-09
python3 -m BioClients.chembl.Client get_activity_by_mol \
	--i $DATADIR/aact_drugs_ink2chembl.chemblid \
	--o $DATADIR/aact_drugs_chembl_activity.tsv
#
printf "Activities (from ChEMBL): $(cat $DATADIR/aact_drugs_chembl_activity.tsv |sed -e '1d' |wc -l)\n"
#
python3 -m BioClients.util.pandas.Utils selectcols --coltags "target_chembl_id" \
	--i $DATADIR/aact_drugs_chembl_activity.tsv \
	|sed -e '1d' |sort -u \
	>$DATADIR/aact_drugs_chembl_target.chemblid
#
printf "Targets (from ChEMBL): $(cat $DATADIR/aact_drugs_chembl_target.chemblid |wc -l)\n"
#
python3 -m BioClients.chembl.Client get_target_components \
	--i $DATADIR/aact_drugs_chembl_target.chemblid \
	--o $DATADIR/aact_drugs_chembl_target_component.tsv
#
printf "Target components (from ChEMBL): $(python3 -m BioClients.util.pandas.Utils selectcols --coltags "component_id" --i $DATADIR/aact_drugs_chembl_target_component.tsv |sed -e '1d' |wc -l)\n"
###
# 
python3 -m BioClients.util.pandas.Utils selectcols --coltags "document_chembl_id" \
	--i $DATADIR/aact_drugs_chembl_activity.tsv \
	|sed -e '1d' |sort -u \
	>$DATADIR/aact_drugs_chembl_document.chemblid
#
printf "Documents (from ChEMBL): $(cat $DATADIR/aact_drugs_chembl_document.chemblid |wc -l)\n"
#
python3 -m BioClients.chembl.Client get_document \
	--i $DATADIR/aact_drugs_chembl_document.chemblid \
	--o $DATADIR/aact_drugs_chembl_document.tsv
#
printf "PubMed IDs (from ChEMBL): $(python3 -m BioClients.util.pandas.Utils selectcols --coltags "pubmed_id" --i $DATADIR/aact_drugs_chembl_document.tsv |sed -e '1d' |wc -l)\n"
#
python3 -m BioClients.chembl.Client list_sources \
	--o $DATADIR/chembl_sources.tsv
#
