#!/bin/bash
###
# 
###
#
set -e
#
#
cwd=$(pwd)
#
docker version
#
INAME="tictac_db"
TAG="latest"
#
if [ ! -e "${cwd}/data" ]; then
	mkdir ${cwd}/data/
fi
#
if [ ! -e ${cwd}/data/tictac_db_mysqldump.sql  ]; then
	mysqldump --single-transaction tictac_db >${cwd}/data/tictac_db_mysqldump.sql 
fi
#
T0=$(date +%s)
#
###
# Build image from Dockerfile.
dockerfile="${cwd}/Dockerfile_Db"
docker build -f ${dockerfile} -t ${INAME}:${TAG} .
#
printf "Elapsed time: %ds\n" "$[$(date +%s) - ${T0}]"
#
#rm -f ${cwd}/data/tictac_db_mysqldump.sql
#
docker images
#
