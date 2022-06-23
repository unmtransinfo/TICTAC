#!/bin/bash
###
### Why are we mining Brexit tweets for targets? Control, to test our
### belief that clinical trials text is not suited to target NER.
###

T0=$(date +%s)

printf "Executing: $(basename $0)\n"

cwd=$(pwd)

DATADIR="${cwd}/data"

###
# ~9hr, 2021-06-08
DATE="$(date +'%Y%m%d')"
tweetfile="$DATADIR/twitter_brexit_${DATE}.tsv"
${cwd}/python/twitter_utils.py \
	--query "brexit" \
	--n 100000 \
	--o $tweetfile
#
printf "Elapsed time: %ds\n" "$[$(date +%s) - ${T0}]"
