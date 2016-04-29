#!/bin/bash
###############################################
### mapbunPrepFiles.sh
### This script extracts the map bundle files into the
###   configuration directory and  returns the data
###   dictionary compatable with aldbConfMapbunDetailedGet()
###
### Input parameters:
###    basedir to put files
###    zipFile name (must be full path)
###    Map Bundle version number
###    Satellite Name to test
###
###############################################

# Inputs
baseDir=$1
zipFile=$2
version=$3
satName=$4
sedFile=$5
sscfFile=$6
gdrmFile=$7
rlcFile=$8
sednomd5File=$9
sscfnomd5File=${10}
gdrmnomd5File=${11}
rlcnomd5FilecFile=${12}

# Well known items (import?)
mapFileList="${sedFile} ${sscfFile} ${gdrmFile} ${rlcFile}"
mapVerNameArray=("sedVersion" "sscfVersion" "gdrmVersion" "rlcVersion")
md5NameArray=("sedmd5" "sscfmd5" "gdrmmd5" "rlcmd5")

# Save current location and work in baseDir
myhome=`pwd`
cd $baseDir


# Determine Sign/Unsigned
if [[ $zipFile =~ "sgn.zip" ]]; then
	isSigned=1
        extpostfix='.sgn'
else
	isSigned=0
        extpostfix=''
fi
dict="{'signed':$isSigned,"

# Unzip files (without output)
supress=`ls $zipFile | xargs unzip -o `
supress=`ls v$version*.zip | xargs unzip -o`

# Move the bundle file to the config directory
#mv -f $zipFile .
cp -f $zipFile .

# Extract the versions, md5 checksums, create stripped files,
count=0
for fn in $mapFileList
do

  fn=$fn$extpostfix
  if [ -f $fn ]; then
      if [[ $fn =~ "gdrm.txt" ]] || [[ $fn =~ "rlc.txt" ]]; then
          mapVerNumArray[$count]=`sed -rn 's/.*ersion[^0-9]+([0-9\.]+)/\1/p' $fn`
      else
          mapVerNumArray[$count]=`sed -rn '0,/ersion/ s/.*ersion[^0-9]+([0-9\.]+)/\1/p' $fn`
      fi
    md5Array[$count]=`grep -aoE '[0-9a-fA-F]{32}' $fn`

    if [ $isSigned == 1 ]; then
        newFile=${fn::-8}
        `sed '$s/,60,20/,60,20\n/' $fn > $newFile.junk`
        #`sed '52s/,60,20/,60,20\n/' $newFile.junk > $newFile`
        `sed '$s/,900,20/,900,20\n/' $newFile.junk > $newFile`
        `sed '$s/,11,2/,11,2\n/' $newFile > $newFile.junk`
        #`sed '803s/,11,2/,11,2\n/' $newFile > $newFile.junk`
        `mv $newFile.junk $newFile`
        `sed -n '$ q;p' $newFile | sed '/[^[:print:]]/d' > $newFile.junk`
        `sed -n '1,/END CERTIFICATE/d;p' $newFile.junk > $newFile`
        `rm $newFile.junk`
    else
        newFile=${fn::-4}
        `sed '$s/,60,20/,60,20\n/' $fn > $newFile.junk`
        #`sed '32s/,60,20/,60,20\n/' $newFile.junk > $newFile`
        `sed '$s/,900,20/,900,20\n/' $newFile.junk > $newFile`
        `sed '$s/,11,2/,11,2\n/' $newFile > $newFile.junk`
        #`sed '785s/,11,2/,11,2\n/' $newFile > $newFile.junk`
        `sed -n '$ q;p' $newFile.junk | sed '/[^[:print:]]/d' > $newFile`
        `rm $newFile.junk`
    fi

  else
    mapVerNumArray[$count]=""
    md5Array[$count]=""
  fi

  dict=$dict\'${mapVerNameArray[$count]}\':\'${mapVerNumArray[$count]}\',
  dict=$dict\'${md5NameArray[$count]}\':\'${md5Array[$count]}\',
  count=`expr $count + 1`
done

# Get Satellite Id, Freq, and Chiprate from the given Name
xsatName=`echo $satName | sed '{s/(/\\\(/g;s/)/\\\)/g;s#\/#\\\/#g;}'`
satid=`sed -rn '0,/([0-9]+),[0-9]+,'$xsatName'/ s/([0-9]+),[0-9]+,'$xsatName'.*/\1/p' ${sscfnomd5File}`

# Get the Antenna Type
#antennatype=`sed -rn 's/#\s*Antenna type:.*\(type ([0-9]+).*/\1/p' ${sednomd5File}`
#antennatype=3
verprefix=`echo $version | sed -rn 's/([0-9]+)\.[0-9]+/\1/p'`
case "$verprefix" in
    "3" | "102" | "107" | "108" | "110")
        #VR-12
        antennatype=3
        ;;
    "106")
        #TECOM Ku Stream
        antennatype=51
        ;;
    "109")
        #KuKarray
        antennatype=8
        ;;
    "200")
        #VR-12Ka
        antennatype=7
        ;;
    "203")
        #HMSA
        antennatype=10
        ;;
    "6")
        #Rantec
        antennatype=1
        ;;
    "1")
        #KVH7
        antennatype=11
        ;;
    "5")
        #KVH3
        antennatype=12
        ;;
    "7")
        #KVH11
        antennatype=13
        ;;
    *)
        # Default to Undefined
        antennatype=99
        ;;
esac


# Gets the record for just that satellite, so you don't have to look through
# the whole document over and over again
# Select Freq based on the Frequency Index
satRecord=`grep -aE '^'$satid',' ${sednomd5File}`
freqidRegex='^'$satid',1,([0-9]+),([a-zA-Z0-9_\/\(\)\.\-]+),(-?[0-9]+),([0-9]+),([0-9]+)'
#chiprateRegex='^'$satid',9,([0-9]+)'
chiprateRegex='^'$satid',9,([A-Za-z0-9]+),([A-Za-z0-9]+),([A-Za-z0-9]+),([A-Za-z0-9]+),([A-Za-z0-9]+),([A-Za-z0-9]+),([A-Za-z0-9]+),([A-Za-z0-9]+),([A-Za-z0-9]+),([A-Za-z0-9]+),([A-Za-z0-9]+),([A-Za-z0-9]+),([A-Za-z0-9]+)'
freqRegex='^'$satid',3,([HVLR]),([0-9]+),([0-9]+),([HVLR]),([0-9]+),([0-9]+)'
rxfreqA=0
txfreqA=0
txfreqB=0
rxfreqB=0
chiprate=0
rolloff=0
pilot=0
freqid=0
freqline=0
polA=0
polB=0
pol=0
satLong=0
while read line; do
  if [[ $line =~ $freqidRegex ]]; then
    satLong="${BASH_REMATCH[3]}"
    freqid=${BASH_REMATCH[5]}
    freqline=$((($freqid + 1)/2))
    count=1
  elif [[ $line =~ $chiprateRegex ]]; then
    chiprate=${BASH_REMATCH[1]}
    rolloff="${BASH_REMATCH[3]}"
    pilot="${BASH_REMATCH[10]}"
  elif [[ $line =~ $freqRegex ]]; then
    if [[ $count == $freqline ]]; then
      # Tx comes first, then rx
      polA="${BASH_REMATCH[1]}"
      txfreqA=${BASH_REMATCH[2]}
      txfreqB=${BASH_REMATCH[5]}
      polB="${BASH_REMATCH[4]}"
      rxfreqA=${BASH_REMATCH[3]}
      rxfreqB=${BASH_REMATCH[6]}
      if [[ $((freqid%2)) == 0 ]]; then
        txfreq=$txfreqB
        rxfreq=$rxfreqB
        pol=$polB
      else
        txfreq=$txfreqA
        rxfreq=$rxfreqA
        pol=$polA
      fi
    fi
    count=`expr $count + 1`
  fi
done <<<"$satRecord"

count=0
dict=$dict\'satName\':\'$satName\',\'satId\':${satid},
dict=$dict\'satLong\':\'$satLong\',
dict=$dict\'flTxFreq\':$txfreq,\'flRxFreq\':$rxfreq,
dict=$dict\'polarity\':\'$pol\',
dict=$dict\'rolloff\':\'$rolloff\',\'pilot\':\'$pilot\',
dict=$dict\'flChipRate\':${chiprate},\'antennaType\':${antennatype}
dict=$dict'}'
echo $dict

cd $myhome
