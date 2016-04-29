#!/bin/bash
###############################################
### mapbunPrecLogExtract.sh
### This script extracts the LAT/LONG and 
###    beam precedence info from the
###    Terminal log in order to verify the 
###    Terminal follows precedence
###
### Inputs: input file name, output file name
###
### Note: File names are complete paths
###
###############################################

# Inputs
infn=$1
outfn=$2

cat $infn | sed -e '{/Zone /{s/.*:/Zone_/;s/lat//;s/long//;s/ //g;N;s/\n//;s/--.*/,/}}' -e t -e '{/Antenna State/{s/.*sat:1,//;s/ .*/,/}}' | awk '/Zone_$/ {print;next;} {printf("%s",$0);}' | sed -e 's/,Zone_/\n/g' | sed -e 's/Zone_//' | sed -e '$s/,$/\n/' | sed -e 's/,/, /g' > $outfn

