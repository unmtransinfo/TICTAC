#!/bin/bash
###
#
printf "Executing: %s\n" "$(basename $0)"
#
cwd=$(pwd)
#
JENSENLABDATADIR="$(cd $HOME/../data/JensenLab/data; pwd)"
#
###
tgzs="\
human_dictionary.tar.gz
diseases_dictionary.tar.gz
tagger_dictionary.tar.gz
"
#
for tgz in $tgzs ; do
	wget -O $JENSENLABDATADIR/${tgz} https://download.jensenlab.org/${tgz}
	(cd $JENSENLABDATADIR; tar xzvf ${tgz})
done
#
###
