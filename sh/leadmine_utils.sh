#!/bin/sh
#############################################################################
#
JAVA=java
#
#
if [ "`uname -s`" = "Darwin" ]; then
	APPDIR="/Users/app"
elif [ "`uname -s`" = "Linux" ]; then
	APPDIR="/home/app"
else
	APPDIR="/home/app"
fi
#
LIBDIR=$APPDIR/lib
CLASSPATH=$LIBDIR/unm_biocomp_nextmove.jar
CLASSPATH=$CLASSPATH:$LIBDIR/unm_biocomp_util.jar
CLASSPATH=$CLASSPATH:$APPDIR/nextmove/leadmine-3.13/LeadMine/leadmine-3.13.jar
#
#
$JAVA \
	-classpath $CLASSPATH \
	edu.unm.health.biocomp.nextmove.leadmine_utils $*
#
