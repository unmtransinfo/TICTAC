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
cat $DATADIR/aact_drugs_smi_pubchem_cid2ink.tsv \
	|awk -F '\t' '{print $2}' |sed -e '1d' \
	>$DATADIR/aact_drugs.ink
#
printf "InChIKeys: $(cat $DATADIR/aact_drugs.ink |wc -l)\n"
#
printf "Elapsed time: %ds\n" "$[$(date +%s) - ${T0}]"
#
