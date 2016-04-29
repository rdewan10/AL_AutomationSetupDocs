#!/bin/bash
###############################################
### nlgPostproc.sh
###
### This script parses the Rtnms/Term syslog file 
###    into an event oriented CSV file w/Header Row
### This is a common file that is included by the 
###    RTNMS/Terminal common data struct definitions
###    so that the code is maintained in one file
###
### Input parameters:
###    basedir to put files
###    input file name (in basedir or full path)
###    output file name (to basedir)
###
### ArcLight Test Automation
###
###############################################


### Variables/Structures

# Inputs
resultBaseDir=$1
logf=$2
if [ $# -gt 2 ]; then
    outf=$3
else
    outf="junk"
fi

# Following variables are set w/in RTNMS/Terminal script: 
#    modu, srchArray, srchArray2, srchCmdArray, srchCutArray, evtPattern


# Set flag for any RTNMS/Term logic differences
if [[ $modu == "Terminal" ]]; then
    termMode=1
else
    termMode=0
fi

# Save current location and work in resultBaseDir
myhome=`pwd`
cd $resultBaseDir

# Abort if file does not exist
if [ ! -f $logf ]; then
    echo File $logf not found!
    rm -f $logf
    touch $logf
    exit
fi

# Clean any old garbage
tempf=$outf.junk
rm -f $tempf
touch $tempf

# Extract all occurences of each event type
curryear=`date +%Y`
count=0
for patt in "${srchArray[@]}"
do
    # Only search for items that exist so that garbage doesn't end up in output
    patt2="${srchArray2[$count]}"
    numitem=`grep "$patt" $logf | grep -c "$patt2"`
    if [[ $numitem != 0 ]]; then
        speccmdp="${srchCmdArray[$count]}"
        if [[ $termMode == 1 ]]; then
            sedstr="{s/  / 0/;s/ /-/;s/^/\"/;s/ / UTC ""$curryear""\",/2;s/--//g;s/\*\*//g;s/  / /g;s/,0/,/;s/,\" /,\"/g;s/ \",/\",/g;s/$/""${evtPattern[$count]}""/}"
        else
            sedstr="{;s/^/\"/;s/UTC/UTC\",/;s/$/""${evtPattern[$count]}""/}"
        fi
        if [[ $speccmdp != "" ]]; then
            grep "$patt" $logf | grep "$patt2" | cut -c "${srchCutArray[$count]}" | sed -r "$speccmdp" | sed "$sedstr" >> $tempf
        else
            grep "$patt" $logf | grep "$patt2" | cut -c "${srchCutArray[$count]}" | sed "$sedstr" >> $tempf
        fi
    fi
    count=`expr $count + 1`
done

# Create a new column (seconds) based on date
#   All records in tempf are moving to outf
rm -f $outf

while read -r line
do
    if [[ $termMode == 1 ]]; then
        #TODO - fix for the month of January (term should have year)
        sedstr="{/Jan-01/ s/UTC ""$curryear""/UTC 2000/}"
        newline=`echo $line | sed "$sedstr"`
        datestr=`echo $newline | sed 's/-/ /;s/\"//g' |  cut -c 1-24`
    else
        newline=$line
        datestr=`echo $newline | sed 's/-/\//g' |  cut -c 2-28`
    fi
        datesec=`date --date="$datestr" +%s`
        echo "$datesec,$newline" >> $outf
done < "$tempf"

if [ ! -f $outf ]; then
    echo Warning: No events found in $logf
else
    mv $outf $tempf
fi


# Add Header Row for CSV, add records (sorted by time), cleanup temp files and return home
echo $hdrRow | cat > $outf
sort -n -t "," $tempf >> $outf
rm -f $tempf

# For debug print to screen is no outfile
if [ $# -le 2 ]; then
    cat $outf
    rm -f $outf
else
    echo "$modu events processed from $logf into $outf; zipping $logf"
    gzip -f $logf
fi


cd $myhome
