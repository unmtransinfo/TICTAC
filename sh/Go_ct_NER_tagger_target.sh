#!/bin/bash
### https://bitbucket.org/larsjuhljensen/tagger
### See http://download.jensenlab.org/ for dictionaries, e.g.
### http://download.jensenlab.org/human_dictionary.tar.gz

cwd=$(pwd)

DATADIR="${cwd}/data"
TAGGER_DIR="/home/app/tagger"
DICT_DIR="/home/data/jensenlab/data"

###
# "9606" is taxonomy human type.
echo "9606" >$DATADIR/human_types.tsv
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
	| ${TAGGER_DIR}/tagcorpus \
	--threads=4 \
	--entities=$DICT_DIR/human_entities.tsv \
	--names=$DICT_DIR/human_names.tsv \
	--types=$DATADIR/human_types.tsv \
	--stopwords=$DATADIR/tagger_global.tsv \
	--out-matches=$DATADIR/aact_descriptions_tagger_target_matches.tsv
#
