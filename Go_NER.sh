#!/bin/sh
#############################################################################
#
cwd=$(pwd)
#
NM_ROOT="/home/app/nextmove"
#
DATADIR="$cwd/data"
CFGDIR="$cwd/config"
DICTDIR="$cwd/dict/meddra"
#
PREFIX="MedDRA"
#
LEADMINE_JAR="${NM_ROOT}/leadmine-3.12/LeadMine/leadmine-3.12.jar"
#
###
# CONFIG: Create LeadMine config files for each dict:
###
for f in $(ls $DICTDIR/*.cfx) ; do
	#
	entitytype=$(basename $f |perl -pe 's/^(.*)\.cfx$/$1/')
	printf "CFG: %s (%s)\n" $(basename $f) $entitytype
	DICTNAME="${PREFIX}_$(basename $f|sed -e 's/\.cfx$//')"
	#
	caseSens="false"
	minEntLen="5"
	spelCor="true"
	maxCorDist="1"
	minCorEntLen="5"
	#
	(cat <<__EOF__
[dictionary]
  location ${f}
  entityType ${entitytype}
  caseSensitive ${caseSens}
  minimumEntityLength ${minEntLen}
  useSpellingCorrection ${spelCor}
  maxCorrectionDistance  ${maxCorDist}
  minimumCorrectedEntityLength ${minCorEntLen}

__EOF__
) \
	>"$CFGDIR/${DICTNAME}.cfg"
done
#
#############################################################################
#
###
# NER: Chemical NER, with default LeadMine dictionary and resolver.
###
leadmine_utils.sh \
	-i ${DATADIR}/drugs.tsv \
	-textcol 3 -unquote -idcol 2 \
	-o ${DATADIR}/drugs_leadmine.tsv \
	-v
#
###
#
nthreads="4"
#
echo "LeadMining (descriptions)..."
#
for f in $(ls $CFGDIR/${PREFIX}_*.cfg) ; do
	#
	dictname=$(basename $f |perl -pe 's/^(.*)\.cfg$/$1/')
	printf "Leadmine: %s (%s)\n" $(basename $f) $dictname
	#
	leadmine_utils.sh \
		-config $f \
		-i ${DATADIR}/descriptions.tsv \
		-textcol 3 -unquote -idcol 2 \
		-o ${DATADIR}/descriptions_${dictname}_leadmine.tsv \
		-v
	#
done
#
