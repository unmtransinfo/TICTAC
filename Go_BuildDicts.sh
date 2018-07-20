#!/bin/sh
#
cwd=$(pwd)
#
NM_ROOT="/home/app/nextmove"
#
COMPILE_JAR=${NM_ROOT}/leadmine-3.12/DictionaryBuilding/CompileCfx/compilecfx-3.12.jar
#
DATADIR="$cwd/data"
DICTDIR="$cwd/dict/meddra"
#
psql -d "meddra" -Atc "SELECT text FROM hlt" >$DICTDIR/hlt.txt
psql -d "meddra" -Atc "SELECT text FROM llt" >$DICTDIR/llt.txt
#
for srcdict in $(ls $DICTDIR/*.txt) ; do
	#
	DICTNAME=$(basename $srcdict|sed -e 's/\.txt$//')
	CFXFILE="$DICTDIR/${DICTNAME}.cfx"
	printf "%s terms: %d\n" $(basename $srcdict) $(cat $srcdict |wc -l)
	#
	#Case insensitive
	LMOPTS="-i"
	#
	printf "Compiling Source dictionary: %s\n" $(basename $srcdict)
	java -jar $COMPILE_JAR $LMOPTS $srcdict $CFXFILE
done
#
