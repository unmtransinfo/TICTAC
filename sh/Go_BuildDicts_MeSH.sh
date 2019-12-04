#!/bin/sh
#
printf "Executing: %s\n" "$(basename $0)"
#
cwd=$(pwd)
#
NM_ROOT="/home/app/nextmove"
#
#COMPILE_JAR=${NM_ROOT}/leadmine-3.12/DictionaryBuilding/CompileCfx/compilecfx-3.12.jar
#COMPILE_JAR=${NM_ROOT}/leadmine-3.13/bin/compilecfx.jar
COMPILE_JAR=${NM_ROOT}/leadmine-3.14.1/bin/compilecfx.jar
#
DATADIR="$cwd/data"
#
###
#MeSH:
#MESHYEAR="2018"
MESHYEAR="2020"
MESHDIR="/home/data/MeSH/${MESHYEAR}"
DICTDIR="${DATADIR}/dict/mesh"
#
${cwd}/python/mesh_xml_utils.py desc2csv --branch "C" \
        --i $MESHDIR/desc${MESHYEAR}.xml.gz \
        --o $DATADIR/mesh_disease.tsv
#
${cwd}/python/mesh_xml_utils.py supp2csv --branch "C" \
        --i $MESHDIR/supp${MESHYEAR}.xml.gz \
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
	# "-i" = case insensitive
	printf "Compiling Source dictionary: %s\n" $(basename $srcdict)
	java -jar $COMPILE_JAR -i $srcdict --out $CFXFILE
done
#
