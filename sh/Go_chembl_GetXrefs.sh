#!/bin/bash
###
#
T0=$(date +%s)
#
printf "Executing: $(basename $0)\n"
#
cwd=$(pwd)
DATADIR="${cwd}/data"
#
date
###
printf "InChIKeys (from PubChem): $(cat $DATADIR/aact_drugs.ink |wc -l)\n"
###
# ChEMBL:
python3 -m BioClients.chembl.Client get_mol_by_inchikey \
	--i $DATADIR/aact_drugs.ink \
	--o $DATADIR/aact_drugs_ink2chembl.tsv
#
python3 -m BioClients.util.pandas.App selectcols --coltags "molecule_chembl_id" \
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
python3 -m BioClients.util.pandas.App selectcols --coltags "target_chembl_id" \
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
printf "Target components (from ChEMBL): $(python3 -m BioClients.util.pandas.App selectcols --coltags "component_id" --i $DATADIR/aact_drugs_chembl_target_component.tsv |sed -e '1d' |wc -l)\n"
###
# 
python3 -m BioClients.util.pandas.App selectcols --coltags "document_chembl_id" \
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
printf "PubMed IDs (from ChEMBL): $(python3 -m BioClients.util.pandas.App selectcols --coltags "pubmed_id" --i $DATADIR/aact_drugs_chembl_document.tsv |sed -e '1d' |wc -l)\n"
#
python3 -m BioClients.chembl.Client list_sources \
	--o $DATADIR/chembl_sources.tsv
#
printf "Elapsed time: %ds\n" "$[$(date +%s) - ${T0}]"
#
