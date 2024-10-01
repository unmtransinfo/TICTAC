#!/bin/bash
###
#
DO_HOME="$(cd $HOME/../data/DiseaseOntology ; pwd)"

DO_RELEASE="20240927"

cwd="$(pwd)"
DATADIR="${cwd}/data"

#conda activate bioclients

python3 -m BioClients.util.obo.App \
	--i ${DO_HOME}/${DO_RELEASE}/doid.obo \
	--o ${DATADIR}/doid.tsv

