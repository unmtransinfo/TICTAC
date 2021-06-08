#!/bin/bash
###
### Why are we mining Brexit tweets for targets? Control, to test our
### belief that clinical trials text is not suited to target NER.
###
### https://bitbucket.org/larsjuhljensen/tagger
### See http://download.jensenlab.org/ for dictionaries, e.g.
### http://download.jensenlab.org/human_dictionary.tar.gz

printf "Executing: $(basename $0)\n"

cwd=$(pwd)

DATADIR="${cwd}/data"

###
#
DATE="$(date +'%Y%m%d')"
tweetfile="$DATADIR/twitter_brexit_${DATE}.tsv"
${cwd}/python/twitter_utils.py \
	--hashtag "brexit" \
	--n 100000 \
	--o $tweetfile
#
###
TAGGER_DIR="$(cd $HOME/../app/tagger; pwd)"
DICT_DIR="$(cd $HOME/../data/JensenLab/data; pwd)"
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
# "9606" is taxonomy human type.
echo "9606" >$DATADIR/human_types.tsv
###
#
taggerfile="$DATADIR/twitter_brexit_tagger_target_matches.tsv"
cat ${tweetfile} |sed -e '1d' \
	|sed -e 's/^/:/' \
	|awk -F '\t' '{print $1 "\t\t\t\t" $2}' \
	| ${TAGGER_DIR}/tagcorpus --threads=4 \
	--entities=$DICT_DIR/human_entities.tsv \
	--names=$DICT_DIR/human_names.tsv \
	--stopwords=$DICT_DIR/tagger_global.tsv \
	--types=$DATADIR/human_types.tsv \
	--out-matches=$taggerfile
#
# Compute entities per 1000 chars rate.
n_chr=$(cat ${tweetfile} |sed -e '1d' |awk -F '\t' '{print $6}' |wc -m)
n_ent=$(cat $taggerfile |wc -l)
eptc=$(echo "1000 * $n_ent / $n_chr" |bc)
printf "Entities per 1000 chars: %.2f\n" "${eptc}"
# 8.63
