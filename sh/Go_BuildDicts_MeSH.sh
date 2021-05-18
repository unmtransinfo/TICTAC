#!/bin/bash
#
printf "Executing: %s\n" "$(basename $0)"
#
cwd=$(pwd)
#
NM_ROOT="$(cd $HOME/../app/nextmove; pwd)"
#
#COMPILE_JAR=${NM_ROOT}/leadmine-3.12/DictionaryBuilding/CompileCfx/compilecfx-3.12.jar
#COMPILE_JAR=${NM_ROOT}/leadmine-3.13/bin/compilecfx.jar
COMPILE_JAR=${NM_ROOT}/leadmine-3.14.1/bin/compilecfx.jar
#
DATADIR="$cwd/data"
#
###
# MeSH:
# Download XML files for current year.
# https://www.nlm.nih.gov/databases/download/mesh.html
# lftp ftp://anonymous:@nlmpubs.nlm.nih.gov -e "cd online/mesh/MESH_FILES/xmlmesh; mget *.zip; quit"
MESHYEAR="2021"
MESHDIR="$(cd $HOME/../data/MeSH/${MESHYEAR}; pwd)"
DICTDIR="${DATADIR}/dict/mesh"
#
if [ ! -e ${DICTDIR} ]; then
	mkdir -p ${DICTDIR}
fi
#
python3 -m BioClients.mesh.Client desc2csv --branch "C" \
        --i $MESHDIR/desc${MESHYEAR}.xml \
        --o $DATADIR/mesh_disease.tsv
#
python3 -m BioClients.mesh.Client supp2csv --branch "C" \
        --i $MESHDIR/supp${MESHYEAR}.xml \
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
	DICTNAME="$(basename $srcdict|sed -e 's/\.txt$//')"
	CFXFILE="$DICTDIR/${DICTNAME}.cfx"
	printf "$(basename $srcdict) terms: $(cat $srcdict |wc -l)\n"
	# "-i" = case insensitive
	printf "Compiling Source dictionary: $(basename $srcdict)\n"
	java -jar $COMPILE_JAR -i $srcdict --out $CFXFILE
done
#
