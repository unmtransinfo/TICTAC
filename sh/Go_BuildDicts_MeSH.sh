#!/bin/sh
#
cwd=$(pwd)
#
NM_ROOT="/home/app/nextmove"
#
#COMPILE_JAR=${NM_ROOT}/leadmine-3.12/DictionaryBuilding/CompileCfx/compilecfx-3.12.jar
COMPILE_JAR=${NM_ROOT}/leadmine-3.13/bin/compilecfx.jar
#
DATADIR="$cwd/data"
#
###
#MeSH:
MESHDIR="/home/data/MeSH/2018"
DICTDIR="${DATADIR}/dict/mesh"
#
python/mesh_xml_utils.py --desc2csv --branch "C" \
        --i $MESHDIR/desc2018.xml \
        --o $DATADIR/mesh_disease.tsv
#
python/mesh_xml_utils.py --supp2csv --branch "C" \
        --i $MESHDIR/supp2018.xml \
        --o $DATADIR/mesh_supp_disease.tsv
#
cat $DATADIR/mesh_disease.tsv \
	|sed -e '1d' \
	|awk -F '\t' '{print $3}' \
	>$DICTDIR/disease.txt
#
cat $DATADIR/mesh_supp_disease.tsv \
	|sed -e '1d' \
	|awk -F '\t' '{print $2}' \
	>$DICTDIR/supp_disease.txt
#
srcdicts="\
$DICTDIR/disease.txt \
$DICTDIR/supp_disease.txt"
#
for srcdict in $srcdicts ; do
	DICTNAME=$(basename $srcdict|sed -e 's/\.txt$//')
	CFXFILE="$DICTDIR/${DICTNAME}.cfx"
	printf "%s terms: %d\n" $(basename $srcdict) $(cat $srcdict |wc -l)
	#Case insensitive
	LMOPTS="-i"
	printf "Compiling Source dictionary: %s\n" $(basename $srcdict)
	java -jar $COMPILE_JAR $LMOPTS $srcdict $CFXFILE
done
#
