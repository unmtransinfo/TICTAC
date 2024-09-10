#!/bin/bash
###
# Local instance of AACT.
# https://aact.ctti-clinicaltrials.org/snapshots
###
#
set -e
set -x
#
DBNAME="aact"
DBSCHEMA="ctgov"
#DBVER="20240909"
DBVER=`date +'%Y%m%d'`
#
cwd=$(pwd)
DATADIR="${cwd}/data"
#
SRCDATADIR=$(cd $HOME/../data/AACT/${DBVER}; pwd)
if [ ! -e "${SRCDATADIR}" ]; then
	printf "ERROR: Data dir not found: %s\n" "${SRCDATADIR}"
	exit
fi
#
DBHOST="aact-db.ctti-clinicaltrials.org"
DBNAME="aact"
#
pg_dump --no-privileges -Fc --schema=${DBSCHEMA} -h $DBHOST -d $DBNAME >$SRCDATADIR/aact.pgdump
#
dropdb ${DBNAME}
createdb ${DBNAME}
#
#
pg_restore -e -v -O -x -h localhost -d ${DBNAME} --no-owner ${SRCDATADIR}/aact.pgdump
#
N=$(psql -t -d ${DBNAME} -c "SELECT COUNT(*) FROM ${SCHEMA}.studies")
if [ ! ${N} -gt 0 ]; then
	printf "ERROR: Cannot access existing AACT db (\"${DBNAME}\")\n"
	exit
else
	printf "Study count: %d\n" "${N}"
fi
#
