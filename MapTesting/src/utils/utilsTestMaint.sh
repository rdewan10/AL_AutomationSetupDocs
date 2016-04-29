#!/bin/bash
###############################################################################
## utilsTestMaint.sh
##
## This script executes linux commmands and reports status thereof to
## assist in managing Automation test, most relevantly
## when the Selenium Chrome Web Driver (Chromiun) gets deadlocked
## this util can be used to kill the chrome session and allow the automation
## to continue
##
## Input parameters:
##   --status) CheckStatus of map tests (altg status)
##   --skip) SkipTest by killing chrome
##   --stop) StopTest by killing altg tasks
##   --statusnlg) CheckStatusNlg of NLG tests 
##   --stopnlg) StopTestNlg by killing nlg tasks
##
###############################################################################

CheckStatus () {
    #grid=`ps aux | grep apache | grep -m 1 "python /var/www/cgi-bin/altgTestLaunched.py"  |  cut -c 110-112`
    grid=`ps aux | grep "python /var/www/cgi-bin/altgTestLaunched.py"  | grep -v grep | grep -m 1 python |  cut -c 110-112`
    if [[ $grid == '' ]]; then
        echo "No tests currently running"
    else
        tmp=`ls -lt /var/www/html/results/$grid | head -2 | grep apache | cut -c 36-47`
        lastupd=`date -d "$tmp" +%s`
        currtime=`date +%s`
        tmp=`expr $currtime - $lastupd`
        echo "Currently testing Group Id " $grid "[updated " $tmp " secs ago]"
        date
        ls -lt /var/www/html/results/$grid | head -2 | grep apache 
        tmp=`expr $lastupd + 900`
        if [[ $currtime > $tmp ]]; then
            echo "Progress for this test has timed out"
        fi
    fi

}

CheckStatusNlg () {
    usern=`whoami`
    grid=`ps aux | grep python | grep nlgMain | grep $usern | grep -v grep | cut -c 86-89`
    if [[ $grid == '' ]]; then
        echo "No NLG tests currently running"
    else
        echo "Following NLG groups running $grid"
    fi
}


SkipTest () {
    usern=`whoami`
    cjobs=`ps aux | grep chrome | grep $usern | grep -v grep`
    if [ ${#cjobs} -gt 0 ]; then
        cjobs=`ps aux | grep chrome | grep $usern | grep -v grep | cut -c 9-15 | xargs kill`
        echo "Killed chromes for $usern"
    else
        echo "No chromes for $usern"
    fi
}

StopTest () {
    usern=`whoami`
    cjobs=`ps aux | grep python | grep altg | grep Launch | grep $usern | grep -v grep`
    if [ ${#cjobs} -gt 0 ]; then
        cjobs=`ps aux | grep python | grep altg | grep Launch | grep $usern | grep -v grep |  cut -c 9-15 | xargs kill`
        echo "Killed altgs for $usern"
    else
        echo "No altgs for $usern"
    fi

}

StopTestNlg () {
    usern=`whoami`
    cjobs=`ps aux | grep python | grep nlg | grep $usern | grep -v grep`
    if [ ${#cjobs} -gt 0 ]; then
        echo $cjobs
        cjobs=`ps aux | grep python | grep nlg | grep $usern | grep -v grep |  cut -c 9-15 | xargs kill`
        echo "Killed nlgs for $usern"
    else
        echo "No nlgs for $usern"
    fi
}

while [ ! $# -eq 0 ]
do
    case "$1" in
        --status)
            CheckStatus
            ;;
        --skip)
            SkipTest
            ;;
        --stop)
            StopTest
            ;;
        --statusnlg)
            CheckStatusNlg
            ;;
        --stopnlg)
            StopTestNlg
            ;;
        *)
            echo "No option selected"
            ;;
    esac
    shift
done


