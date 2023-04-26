#!/bin/bash
#############################################################################
#
printf "Executing: %s\n" "$(basename $0)"
#
cwd=$(pwd)
#
NM_ROOT="$(cd $HOME/../app/nextmove; pwd)"
LIBDIR="$(cd $HOME/../app/lib; pwd)"
#
DATADIR="$cwd/data"
#
#############################################################################
# Disease/phenotype NER (descriptions), with custom built dictionaries
# and config files.
#
CFGDIR="${DATADIR}/config"
DICTDIR="${DATADIR}/dict/mesh"
PREFIX="MeSH"
#
###
# CONFIG: Create LeadMine config files for each dict:
###
rm -f $CFGDIR/${PREFIX}_*.cfg
#
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
###
#
nthreads="4"
#
echo "Disease/phenotype NER (descriptions)..."
#
for f in $(ls $CFGDIR/${PREFIX}_*.cfg) ; do
	#
	dictname=$(basename $f |perl -pe 's/^(.*)\.cfg$/$1/')
	printf "Leadmine: $(basename $f) (${dictname})\n"
	#
	java -jar $LIBDIR/unm_biocomp_nextmove-0.0.1-SNAPSHOT-jar-with-dependencies.jar \
		-config $f \
		-i ${DATADIR}/aact_descriptions.tsv \
		-textcol 3 -unquote -idcol 1 \
		-o ${DATADIR}/aact_descriptions_${dictname}_leadmine.tsv \
		-v
	#
done
#
