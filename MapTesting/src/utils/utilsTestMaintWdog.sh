#!/bin/bash

###############################################################################
## utilsTestMaintWdog.sh
##
## Automation test watchdog, best for batch/overnight map test
## Allow test to run for 900 seconds without progress
## Kills chrome session when no progress
## Stops itself after 3 minutes of idle
##
## Input parameters:
##   none
###############################################################################
wdogAuto () {
    grid=$1
    if [[ $grid != '' ]]; then
        usern=`whoami`
        tmp=`ls -lt /var/www/html/results/$grid | head -2 | grep $usern | cut -c 36-47`
        lastupd=`date -d "$tmp" +%s`
        currtime=`date +%s`
        tmp=`expr $lastupd + 900`
        if [[ $currtime > $tmp ]]; then
            tmp=`ps aux | grep chrome | grep $usern | cut -c 9-15 | xargs kill`
            echo "wdog timeout on group $grid"
        fi
    fi
}

testInProg=1
idleCount=0
while [[ testInProg != 0 ]]
do
    grid=`ps aux | grep "python /var/www/cgi-bin/altgTestLaunched.py"  | grep -v grep | grep -m 1 python |  cut -c 110-112`
    if [[ $grid != '' ]]; then
        idleCount=0
        wdogAuto $grid
    else 
        idleCount=`expr $idleCount + 1`
    fi

    if [[ $idleCount > 3 ]]; then
        echo "wdog exiting, no tests"
        exit
    fi
    
    sleep 60

done
