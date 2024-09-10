#!/bin/bash
###
# TICTAC-Db: AACT plus TICTAC tables needed to provide accountability and
# provenance for TICTAC disease-gene associations, including to supporting
# clinical trials and publications.
###

set -e
set -x

# Prerequisite: "aact" should already exist.

DBNAME_AACT="aact"
SCHEMA_AACT="ctgov"
#
DBNAME="aact_tictac"
SCHEMA="tictac"

cwd=$(pwd)
DATADIR="${cwd}/data"

N=$(psql -t -d ${DBNAME_AACT} -c "SELECT COUNT(*) FROM ${SCHEMA_AACT}.studies")
if [ ! ${N} -gt 0 ]; then
	printf "ERROR: Cannot access existing AACT db (\"${DBNAME_AACT}\")\n"
	exit
fi
#
psql -c "CREATE DATABASE ${DBNAME} WITH TEMPLATE ${DBNAME_AACT}"
#
psql -d $DBNAME -c "CREATE SCHEMA ${SCHEMA}"
#
# Start by loading associations table:
header=$(head -1 ${DATADIR}/tictac_genes_disease_associations.csv |tr "[:upper:]" "[:lower:]" |sed 's/-/_/g')
colspecs=$(echo ${header} |sed 's/,/ VARCHAR(512),/g' |sed 's/$/ VARCHAR(512)/')
psql -d $DBNAME -c "CREATE TABLE ${SCHEMA}.gene_disease_assns ( ${colspecs} )"
#
printf "${header}\n" >${DATADIR}/tmp.csv
cat ${DATADIR}/tictac_genes_disease_associations.csv |sed '1d' >>${DATADIR}/tmp.csv
#
cat ${DATADIR}/tmp.csv \
	|psql -d $DBNAME -c "COPY ${SCHEMA}.gene_disease_assns FROM STDIN WITH (FORMAT CSV,DELIMITER ',', HEADER TRUE)"
psql -d $DBNAME -c "COMMENT ON TABLE ${SCHEMA}.gene_disease_assns IS 'TICTAC gene-disease associations'"
#
cols_int="\
nstudy \
npub \
unique_drugs_count \
ndrugmention \
ndiseasemention \
"
for col in ${cols_int} ; do
	psql -d $DBNAME -c "ALTER TABLE ${SCHEMA}.gene_disease_assns ALTER COLUMN ${col} TYPE INTEGER USING ${col}::INTEGER" 
done
#
cols_float="\
npub_weighted \
rank \
rank_nstudy_weighted \
rank_npub_weighted \
rank_ndiseasemention \
rank_ndrugmention \
npub_weight \
mean_rank \
mean_rank_score \
"
#
for col in ${cols_float} ; do
	psql -d $DBNAME -c "ALTER TABLE ${SCHEMA}.gene_disease_assns ALTER COLUMN ${col} TYPE FLOAT USING ${col}::FLOAT" 
done
#
###
# Tagger disease NER on AACT study descriptions.
psql -d $DBNAME <<__EOF__
CREATE TABLE ${SCHEMA}.descriptions_tagger_disease_matches (
	nct_id VARCHAR(12),
	paragraph INTEGER,
	sentence INTEGER,
	ch_first INTEGER,
	ch_last INTEGER,
	term VARCHAR(512),
	termtype INTEGER,
	serialno INTEGER
)
__EOF__
#
cat ${DATADIR}/aact_descriptions_tagger_disease_matches.tsv \
	|psql -d $DBNAME -c "COPY ${SCHEMA}.descriptions_tagger_disease_matches FROM STDIN WITH (FORMAT CSV,DELIMITER E'\t', HEADER FALSE)"
#
###
# Leadmine chemical NER on AACT study descriptions.
psql -d $DBNAME <<__EOF__
CREATE TABLE ${SCHEMA}.descriptions_leadmine_chemical_matches (
	docname VARCHAR(12),
	sectiontype VARCHAR(1),
	originaltext VARCHAR(512),
	entitytype VARCHAR(1),
	begindex INTEGER,
	entitytext VARCHAR(512),
	possiblycorrectedtext  VARCHAR(512),
	correctiondistance INTEGER,
	resolvedform VARCHAR(2048)
)
__EOF__
#
cat ${DATADIR}/aact_drugs_leadmine.tsv |sed '1d' \
	|psql -d $DBNAME -c "COPY ${SCHEMA}.descriptions_leadmine_chemical_matches FROM STDIN WITH (FORMAT CSV,DELIMITER E'\t', HEADER FALSE)"
#
