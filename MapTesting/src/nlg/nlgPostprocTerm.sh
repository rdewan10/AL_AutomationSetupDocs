#!/bin/bash
###############################################
### nlgPostprocTerm.sh
###
### This script parses the terminal syslog file 
###    into an event oriented CSV file w/Header Row
### Currently, the following events are parsed:
###    SAT_SRCH, SAT_LOCK, BRL_LOGIN, CRL_LOGIN, 
###    LOGOUT_CMD, REBOOT_CMD, RELOGIN_CMD, TOD_RESET, 
###    SET_ANT, DWELL_TIMEO, SAT_HANDO, RLC_STATE, 
###    SMS_STATE, BB_STATE, LOGIN_STATE, TERM_STATE, 
###    UPD_ANTTXB, SEND_ANTSAT, MODE_CHG
### Each event is represented with a "1" in the event column, 
###    and any supporting info is in the VARG column(s) as
###    follows:
### If TOD_RESET, then VARG_1 is TOD_NEW and VARG_2 is TOD_OLD
### If SET_ANT, then VARG_1 is BEAM_NAME and VARG_2 is 0
### If *_STATE, then VARG_1 is state change value and VARG_2 is 0
### If SEND_ANTSAT, then VARG_1 is AcuSt and VARG_2 is 0
### If UPD_ANTTXB, then VARG_1 is AcuSt and VARG_2 is 0
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
modu="Terminal"

# CSV Header Row; first line of output file
#   Vargs as per description above
hdrRow="POLLSEC, POLLTIME, VARG_1, VARG_2, SAT_SRCH, SAT_LOCK, BRL_LOGIN, CRL_LOGIN, LOGOUT_CMD, REBOOT_CMD, RELOGIN_CMD, TOD_RESET, SET_ANT, DWELL_TIMEO, SAT_HANDO, RLC_STATE, SMS_STATE, BB_STATE, LOGIN_STATE, TERM_STATE, UPD_ANTTXB, SEND_ANTSAT, MODE_CHG"

# Unique search string for each event
declare -a srchArray=(
"CCD: \[SSM:NO COVER" 
"CCD: \[SSM:SAT LOCK"
"CCD: Received CRL PCM after Login response PCM Ack sent - Assume officially logged in via BRL now" 
"CCD: \[LSM:07:01\] LOGIN STATE CHANGE:"
"CCD: \[ACP:10:03\] ACP Command Message --"
"CCD: \[ACP:10:01\] ACP Command Message --"
"CCD: \[ACP:10:02\] ACP Command Message --"
"CCD: Time of Day Reset." 
"CCD: \[SSM:SEARCH\] Set Antenna State sat:"
"satsearch"
"Satellite Handover, satDistance"
"RLC MSG STATE CHANGE:"
"SMS STATE CHANGE:"
"BB MSG STATE CHANGE:"
"LOGIN STATE CHANGE:"
"TERM STATE CHANGE:"
"UpdateAntennaTxbSettings"
"SendAntSatUpdateUnconditional"
"Mode Change Event:"
)

# Unique search string for each event (FILTER 2)
declare -a srchArray2=(
"SAT #Avail:"
"SATSRCH STATE CHANGE:"
""
"Terminal Logged In (CRL)" 
"LOGOUT CMD"
"REBOOT CMD"
"RELOGIN CMD" 
""
""
""
""
""
""
""
""
""
""
""
""
)

# Cuts to grep for each search string event
declare -a srchCutArray=(
"1-16" 
"1-16" 
"1-16 35-200" 
"1-16" 
"1-16" 
"1-16" 
"1-16" 
"1-16 35-200"
"1-16 37-200"
"1-16" 
"1-16" 
"1-16 35-200" 
"1-16 35-200" 
"1-16 35-200" 
"1-16 35-200" 
"1-16 35-200" 
"1-16 35-200" 
"1-16 35-200" 
"1-16 35-200" 
)

# Flag for each search string event
declare -a srchCmdArray=(
"" 
"" 
"{s/CCD:.*t=/\"/;s/ csec\)/\"/}"
"" 
"" 
"" 
"" 
"{s/CCD.*new://;s/ old:/,/}"
"{s/CCD.*State sat:.,/\"/;s/ lon.*$/\"/}"
"" 
"" 
"{s/CCD:.*CHANGE: /\"/;s/$/\"/}"
"{s/CCD:.*CHANGE: /\"/;s/$/\"/}"
"{s/CCD:.*CHANGE: /\"/;s/$/\"/}"
"{s/CCD:.*CHANGE: /\"/;s/$/\"/}"
"{s/CCD:.*CHANGE: /\"/;s/$/\"/}"
"{s/CCD:.*AcuSt:/\"/;s/$/\"/}"
"{s/CCD:.*AcuSt:/\"/;s/$/\"/}"
"{s/CCD:.*Event:/\"/;s/$/\"/}"
)

# Flag for each search string event (graphed on same line or staggered lines)
# same line per event
declare -a evtPatternBin=(
"0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
"0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
 ",0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
"0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
"0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
"0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0"
"0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0"
   ",0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0"
 ",0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0"
"0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0"
"0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0"
 ",0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0"
 ",0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0"
 ",0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0"
 ",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0"
 ",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0"
 ",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0"
 ",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0"
 ",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1"
)

# different line per event (don't use spaces to make pretty - messes up copy)
declare -a evtPatternOff=(
"0,0,19,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0"
"0,0,18,18,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0"
 ",0,18,17,17,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0"
"0,0,18,17,16,16,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0"
"0,0,18,17,16,15,15,13,12,11,10,9,8,7,6,5,4,3,2,1,0"
"0,0,18,17,16,15,14,14,12,11,10,9,8,7,6,5,4,3,2,1,0"
"0,0,18,17,16,15,14,13,13,11,10,9,8,7,6,5,4,3,2,1,0"
   ",18,17,16,15,14,13,12,12,10,9,8,7,6,5,4,3,2,1,0"
 ",0,18,17,16,15,14,13,12,11,11,9,8,7,6,5,4,3,2,1,0"
"0,0,18,17,16,15,14,13,12,11,10,10,8,7,6,5,4,3,2,1,0"
"0,0,18,17,16,15,14,13,12,11,10,9,9,7,6,5,4,3,2,1,0"
 ",0,18,17,16,15,14,13,12,11,10,9,8,8,6,5,4,3,2,1,0"
 ",0,18,17,16,15,14,13,12,11,10,9,8,7,7,5,4,3,2,1,0"
 ",0,18,17,16,15,14,13,12,11,10,9,8,7,6,6,4,3,2,1,0"
 ",0,18,17,16,15,14,13,12,11,10,9,8,7,6,5,5,3,2,1,0"
 ",0,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,4,2,1,0"
 ",0,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,3,1,0"
 ",0,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,2,0"
 ",0,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,1"
)

# Set evtPattern (Binary flags, or offset)
declare -a evtPattern=(${evtPatternOff[*]})

# Include common file to process the globally named data items
. nlgPostproc.sh
