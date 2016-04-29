#!/bin/bash

###############################################
### utilsMapResults.sh
### This script generates a report of map test results
###   for specified groups
###
### Input parameters:
###    -o old (unsigned) group list
###    -n new (signed) group list
###    -c (| --compare) compare sed/sscf differences
###    -f (| --fllock) report fllock
###    -p (| --precedence) report precedence
###    -s (| --signed) compare unsigned/signed checksum differences
###    -t (| --trickle) report trickle
###    -u (| --upload) report upload
###
###############################################


compar=0
fllock=0
prec=0
trickle=0
upload=0

while [ ! $# -eq 0 ]
do
    case "$1" in
        -c | --compare)
            compar=1
            ;;
        -f | --fllock)
            fllock=1
            ;;
        -n)
            group_new=(`echo $2 | sed '{s/,/ /g;s/\[//;s/\]//}'`)
            shift
            ;;
        -o)
            group_old=(`echo $2 | sed '{s/,/ /g;s/\[//;s/\]//}'`)
            shift
            ;;
        -p | --precedence)
            prec=1
            ;;
        -s | --signed)
            signver=1
            ;;
        -t | --trickle)
            trickle=1
            ;;
        -u | --upload)
            upload=1
            ;;
    esac
    shift
done

resDir="/var/www/html/results"

if [[ $compar -eq 1 ]]; then
    echo
    echo "################ SED/SSCF Comparison"
    echo
    for ((count=0; count<${#group_new[@]}; count++));
    do
        echo
        echo "######## Results between Groups ${group_old[$count]} / ${group_new[$count]}"
        echo
        echo "#### SED File diffs"
        diff $resDir/${group_old[$count]}/sed.csv $resDir/${group_new[$count]}/sed.csv
        echo
        echo "#### SSCF File diffs"
        diff $resDir/${group_old[$count]}/sscf.csv $resDir/${group_new[$count]}/sscf.csv
        echo
    done
fi

if [[ $signver -eq 1 ]]; then
    echo
    echo "################ Unsigned/Signed Verification (consider dirs /etc/ vs. /test)"
    echo
    for ((count=0; count<${#group_new[@]}; count++));
    do
        ogrpid=${group_old[$count]}
        ngrpid=${group_new[$count]}
        echo
        echo "######## Results between Groups $ogrpid / $ngrpid"
        echo
        osever=`grep Version $resDir/$ogrpid/sed.csv`
        nsever=`grep Version $resDir/$ngrpid/sed.csv`
        ossver=`grep Version $resDir/$ogrpid/sscf.csv`
        nssver=`grep Version $resDir/$ngrpid/sscf.csv`
        echo "Group $ogrpid	SED $osever 	SSCF $ossver"
        echo "Group $ngrpid	SED $nsever 	SSCF $nssver"
        echo
        echo "#### Upload MD5 diffs"
        fno=$resDir/$ogrpid/termUpload.log 
        fnn=$resDir/$ngrpid/termUpload.log 
        if [[ -f $fno && -f $fnn ]]; then
            grep -v PEXPECT $fno | tac | grep -m2 -B 5 sed | tac > /tmp/md5_old.log
            grep -v PEXPECT $fnn | tac | grep -m2 -B 5 sed | tac > /tmp/md5_new.log
            diff /tmp/md5_old.log /tmp/md5_new.log
            rm -f /tmp/md5_old.log /tmp/md5_new.log
        else
            echo "Missing Upload MD5 file(s)"
        fi
        echo
        echo "#### Trickle MD5 diffs"
        fno=$resDir/$ogrpid/termTrickle.log 
        fnn=$resDir/$ngrpid/termTrickle.log 
        if [[ -f $fno && -f $fnn ]]; then
            grep -v PEXPECT $fno | tac | grep -m2 -B 5 sed | tac > /tmp/md5_old.log
            grep -v PEXPECT $fnn | tac | grep -m2 -B 5 sed | tac > /tmp/md5_new.log
            diff /tmp/md5_old.log /tmp/md5_new.log
            rm -f /tmp/md5_old.log /tmp/md5_new.log
        else
            echo "Missing Trickle MD5 file(s)"
        fi
        echo
    done
fi


if [[ $trickle -eq 1 || $upload -eq 1 ]]; then
    echo
    echo "################ SED/SSCF Upload/Trickle Download"
    echo
    for ((count=0; count<${#group_new[@]}; count++));
    do
        grpid=${group_new[$count]}
        echo
        echo "######## Results for Group $grpid}"
        echo
        echo SED Version
        grep Version $resDir/$grpid/sed.csv
        echo SSCF Version
        grep Version $resDir/$grpid/sscf.csv
        echo
        if [[ $upload -eq 1 ]]; then
            echo "#### UPLOAD"
            grep -A 2 Upload $resDir/$grpid/results | grep -B 2 PASSED
            grep -v PEXPECT $resDir/$grpid/termUpload.log | tac | grep -m2 -B 5 sed | tac > /tmp/tu.log
            cat /tmp/tu.log
        fi
    
        if [[ $trickle -eq 1 ]]; then
            echo
            echo "#### TRICKLE"
            grep -A 2 Trickle $resDir/$grpid/results | grep -B 2 PASSED
            grep -v PEXPECT $resDir/$grpid/termTrickle.log | tac | grep -m2 -B 5 sed | tac > /tmp/tt.log
            cat /tmp/tt.log
        fi
    
        if [[ $trickle -eq 1 && $upload -eq 1 ]]; then
            echo
            echo "#### UPLOAD & TRICKLE Checksum Comparison (diff)"
            diff /tmp/tu.log /tmp/tt.log
            echo
        fi

    done
    rm -f /tmp/tu.log /tmp/tl.log
fi

if [[ $fllock -eq 1 ]]; then
    echo
    echo "################ FL Lock Details"
    echo
    for ((count=0; count<${#group_new[@]}; count++));
    do
        grpid=${group_new[$count]}
        echo
        echo "######## $resDir/$grpid"
        grep satName $resDir/$grpid/results
        echo 
        grep "Latitude:" $resDir/$grpid/results
        echo
        grep "Warning:" $resDir/$grpid/results
        echo
        #grep -A 2 FLLock $resDir/$grpid/results | grep -B 2 PASSED
        grep -A 2 FLLock $resDir/$grpid/results 
        echo
    done
fi

if [[ $prec -eq 1 ]]; then
    echo
    echo "################ Precedence Details"
    echo
    for ((count=0; count<${#group_new[@]}; count++));
    do
        grpid=${group_new[$count]}
        echo
        echo "######## $resDir/$grpid"
        echo SED Version
        grep Version $resDir/$grpid/sed.csv
        echo SSCF Version
        grep Version $resDir/$grpid/sscf.csv
        echo
        echo Calculated:
        cat $resDir/$grpid/coords_precname* 
        echo
        echo Result:
        grep -A 2 Precedence $resDir/$grpid/results | grep -B 2 PASSED
        #grep -A 2 Precedence $resDir/$grpid/results 
        echo
        cat $resDir/$grpid/mapbunPrecVerify.log
    done
fi

