#!/bin/sh
###############################################
### mapbunSed2Kml.sh
###   This script invokes the MATLAB Standalone 
###   sed2kml  program for generating the 
###   Google Earth KML file. Since the sed2kml is
###   from the engineering baseline and relies on
###   hardcoded filenames, this script provides
###   a wrapper with additional flexibility
###
### Input parameters:
###    config basedir to get/put files
###    sed (nomd5) name 
###    kml file name
###
###############################################

# Inputs
matlabPath=$1
baseDir=$2
sednomd5File=$3
kmlFile=$4

# Save current location and work in baseDir
myhome=`pwd`
cd $baseDir

if [ "$sednomd5File" != "sed.csv" ]; then
    cp -p $sednomd5File "sed.csv"
fi

$myhome/run_sed2kml.sh $matlabPath

if [ "$kmlFile" != "G_Earth_plot.kml" ]; then
    mv "G_Earth_plot.kml" $kmlFile 
fi

cd $myhome
