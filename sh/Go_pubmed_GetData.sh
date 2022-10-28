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
DBHOST="tcrd.kmc.io"
DBPORT="3306"
DBNAME="tcrd6124"
DBUSR="tcrd"
#DBPW=""
#
#DBHOST="tcrd.newdrugtargets.org"
#DBPORT="3306"
#DBNAME="tcrd"
#DBUSR="tcrd_read_only"
#DBPW=""
#
unset DBPW
DBPW=$(read_password "${DBUSR}@${DBHOST}:${DBPORT}:${DBNAME} PASSWORD:")
#
date
#
#############################################################################
# TCRD "pubmed" table:
#(3879431 rows in May 2021)
python3 -m BioClients.idg.tcrd.Client listPublications \
	--dbhost "$DBHOST" --dbport "$DBPORT" --dbname "$DBNAME" --dbusr "$DBUSR" --dbpw "$DBPW" \
	|gzip -c >${TCRDDATADIR}/pubmed.tsv.gz
#
#
