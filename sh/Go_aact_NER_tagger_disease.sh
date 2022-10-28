#!/bin/bash
### https://bitbucket.org/larsjuhljensen/tagger
### See http://download.jensenlab.org/ for dictionaries, e.g.
### http://download.jensenlab.org/human_dictionary.tar.gz

### Issue: Tagger compiles fine on CentOS 7, but not
### Ubuntu 20.04 or 22.04. So we copy pre-compiled executable
### and necessary libraries from CentOS to Ubuntu server.

T0=$(date +%s)

printf "Executing: %s\n" "$(basename $0)"

cwd=$(pwd)

DATADIR="${cwd}/data"
TAGGER_DIR="$(cd $HOME/../app/tagger_precompiled; pwd)"
DICT_DIR="$(cd $HOME/../data/JensenLab/data; pwd)"

TAGGER_EXE="${TAGGER_DIR}/tagcorpus"

###
# "-26" is DOID disease type.
echo "-26" >$DATADIR/disease_types.tsv
#
###
# Tagger (document.h) document TSV format requirements.
# Documents one per line.
# First field example PMID:23909892|DOI:10.1021/pr400457u
# so the program parses out the PMID 23909892.
# We kludge by prefixing every line with ":". Then first field parsed as docid.
# Also 5th field is text (skip author, year, etc.), so another
# kludge to insert dummy fields.
###
# Output mentions to stdout or --out-matches.
# Fields: docid, paragraph, sentence, ch_first, ch_last, term, type, serialno.
# (serialno from the names file, which resolves synonyms.)
###
cat ${DATADIR}/aact_descriptions.tsv \
	|sed -e 's/^/:/' \
	|awk -F '\t' '{print $1 "\t" $2 "\t\t\t" $3}' \
	| ${TAGGER_EXE} \
	--threads=4 \
	--entities=$DICT_DIR/diseases_entities.tsv \
	--names=$DICT_DIR/diseases_names.tsv \
	--stopwords=$DICT_DIR/diseases_global.tsv \
	--types=$DATADIR/disease_types.tsv \
	--out-matches=$DATADIR/aact_descriptions_tagger_disease_matches.tsv
#
printf "Elapsed time: %ds\n" "$[$(date +%s) - ${T0}]"
#
