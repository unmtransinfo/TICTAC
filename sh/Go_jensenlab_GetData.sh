#!/bin/bash
###
#
printf "Executing: %s\n" "$(basename $0)"
#
cwd=$(pwd)
#
###
#
JENSENLABDATADIR="$(cd $HOME/../data/JensenLab/data; pwd)"
#
#
###
wget -O $JENSENLABDATADIR/diseases_dictionary.tar.gz https://download.jensenlab.org/diseases_dictionary.tar.gz
#
(cd $JENSENLABDATADIR; tar xzvf diseases_dictionary.tar.gz)
#
