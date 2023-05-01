#!/bin/bash
###
#
T0=$(date +%s)
#
printf "Executing: $(basename $0)\n"
#
cwd=$(pwd)
DATADIR="${cwd}/data"
TAGGER_DIR="$(cd $HOME/../app/tagger_precompiled; pwd)"
LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$TAGGER_DIR"
DICT_DIR="$(cd $HOME/../data/JensenLab/data; pwd)"

TAGGER_EXE="${TAGGER_DIR}/tagcorpus"

${TAGGER_EXE} --help
#
###
# "-26" is DOID disease type.
echo "-26" >$DATADIR/disease_types.tsv
#
###
# Tagger (document.h) document TSV format requirements.
# Documents one per line.
# First field example PMID:23909892|DOI:10.1021/pr400457u
# so the program parses out the PMID 23909892.
# Also 5th field is text to be processed.
###
# Output mentions to stdout or --out-matches.
# Fields: docid, paragraph, sentence, ch_first, ch_last, term, type, serialno.
# (serialno from the names file, which resolves synonyms.)
###
cat $DATADIR/aact_study_refs_pubmed-records.tsv \
	|sed '1d' |sed -e 's/^/PMID:/' \
	|awk -F '\t' '{print $1 "\t" $2 "\t" $4 "\t" $5 "\t" $3}' \
	| ${TAGGER_EXE} \
	--threads=16 \
	--entities=$DICT_DIR/diseases_entities.tsv \
	--names=$DICT_DIR/diseases_names.tsv \
	--stopwords=$DICT_DIR/diseases_global.tsv \
	--types=$DATADIR/disease_types.tsv \
	--out-matches=$DATADIR/aact_study_refs_pubmed-records_tagger_disease_matches.tsv

#
date
###
# 
#
printf "Elapsed time: %ds\n" "$[$(date +%s) - ${T0}]"
#
