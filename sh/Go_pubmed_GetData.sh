#!/bin/bash
###
#
printf "Executing: %s\n" "$(basename $0)"
#
cwd=$(pwd)
#
###
function read_password()
{
  prompt=$1
  while IFS= read -p "$prompt" -r -s -n 1 char
  do
    if [[ $char == $'\0' ]]; then
         break
    fi
    prompt='*'
    password+="$char"
  done
  echo $password
}
#
TCRDDATADIR="$(cd $HOME/../data/TCRD/data; pwd)"
#
#
DBHOST="tcrd.ncats.io"
DBPORT="3306"
DBNAME="tcrd6134pharos2"
DBUSR="tcrd"
#DBPW=""
#
unset DBPW
DBPW=$(read_password "${DBUSR}@${DBHOST}:${DBPORT}:${DBNAME} PASSWORD:")
#
date
#
ARGS="-h $DBHOST -D $DBNAME -u $DBUSR -p${DBPW}"
#
#############################################################################
# TCRD "pubmed" table:
#(3879431 rows in May 2021)
mysql $ARGS -e "SELECT DISTINCT pubmed_id FROM protein2pubmed ORDER BY pubmed_id" \
	>${TCRDDATADIR}/tcrd_pubmed_ids.txt
#
#
