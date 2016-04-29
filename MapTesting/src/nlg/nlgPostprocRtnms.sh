#!/bin/bash
###############################################
### nlgPostprocRtnms.sh
###
### This script parses the Rtnms syslog file 
###    into an event oriented CSV file w/Header Row
### Currently, the following events are parsed:
###    VMT_STATE,CRL_STATE,CONN_LOGIN,CONN_OPER,
###    CONN_SESS,PWRCTL_UPD,ACSM_UPD,CONN_LOGOUT,
###    CONN_Vmt,CONN_VMT,CONN_RL"
### Each event is represented with a "1" in the event column, 
###    and any supporting info is in the VARG column(s) as
###    follows:
### VARG_1 is Terminal ID (decimal equiv of 0.0.c.d addr), or
###  CRL indicator for CRL_STATE
### VARG_2 is State for VMT_STATE or CRL_STATE, otherwise
###   contains message
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

modu="Rtnms"

# CSV Header Row; first line of output file
#   Vargs as per description above
hdrRow="POLLSEC,POLLTIME,VARG_1,VARG_2,VMT_STATE,CRL_STATE,CONN_LOGIN,CONN_OPER,CONN_SESS,PWRCTL_UPD,ACSM_UPD,CONN_LOGOUT,CONN_Vmt,CONN_VMT,CONN_RL,MULTIRATE_STATE,MULTIRATE_ADJ,MULTIRATE_MSG,MULTIRATE_PCRETRY,MULTIRATE_DGTO"

# Unique search string for each event (FILTER 1)
# "PwrCtrl: VMT:"
declare -a srchArray=(
"State Change: VMT:"
"State Change: CRL:"
"Connection Activity: Login complete VMT:"
"Connection Activity: Operator Telling VMT:"
"Connection Activity: Session-Layer Telling VMT:"
"PwrCtrl: VMT "
"PwrCtrl: VMT:"
"Acsm: VMT:"
"Connection Activity: Logout from VMT: "
"Connection Activity: Vmt:" 
"Connection Activity: VMT:" 
"Connection Activity: Change Return Link sent to VMT:"
"Multirate: VMT"
"Multirate: VMT"
"Multirate: VMT"
"Multirate: VMT:"
"Multirate:  VMT"
)

# Unique search string for each event (FILTER 2)
declare -a srchArray2=(
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
"State --> "
"Adjust: attenuator"
" - "
""
""
)

# Cuts to grep for each search string event
declare -a srchCutArray=(
"2-29 45-300" 
"2-29 45-300" 
"2-29 45-300" 
"2-29 45-300" 
"2-29 45-300" 
"2-29 45-300" 
"2-29 45-300" 
"2-29 45-300" 
"2-29 45-300" 
"2-29 45-300" 
"2-29 45-300" 
"2-29 45-300" 
"2-29 45-300" 
"2-29 45-300" 
"2-29 45-300" 
"2-29 45-300" 
"2-29 45-300" 
"2-29 45-300" 
"2-29 45-300" 
)

# Flag for each search string event
declare -a srchCmdArray=(
"{s/ State Change: VMT:/\"/;s/: .*-> /\",\"/;s/$/\"/;s/ \"/\"/}"
"{s/ State Change: CRL:/\"/;s/\]: .*-> /\]\",\"/;s/$/\"/;s/ \"/\"/}"
"{s/ Connection Activity: Login complete VMT:/\"/;s/\./\#/;s/\./\#/;s/\.//;s/\#/\./g;s/$/\"/}"
"{s/ Connection Activity: Operator.*VMT:/\"/;s/ to Logout/\",\"to Logout/;s/$/\"/}"
"{s/ Connection Activity: Session.*VMT:/\"/;s/ to Logout.*$/\"/}"
"{s/ PwrCtrl: VMT /\"/;s/\/([0-9]+)\.([0-9]+)/&\",\"/;s/$/\"/}"
"{s/ PwrCtrl: VMT:/\"/;s/\/([0-9]+)\.([0-9]+)/&\",\"/;s/$/\"/}"
"{s/ Acsm: VMT:/\"/;s/\/([0-9]+)\.([0-9]+)/&\",\"/;s/$/\"/}"
"{s/ Connection Activity: Logout.*VMT: /\"/;s/\. Reason: /\",\"/;s/$/\"/}"
"{s/ Connection Activity: Vmt:/\"/;s/ now /\",\"now /;s/$/\"/}"
"{s/ Connection Activity: VMT:/\"/;s/ [a-zABD-SV-Z]/\",\"&/;s/\",\" /\",\"/;s/$/\"/}"
"{s/ Connection Activity: Change Return Link sent to VMT:/\"/;s/ Goto/\",\"Goto/;s/$/\"/}"
"{s/ Multirate: VMT /\"/;s/ State --> /\",\"/;s/$/\"/}"
"{s/ Multirate: VMT /\"/;s/ Adjust: /\",\"/;s/$/\"/}"
"{s/ Multirate: VMT /\"/;s/ - /\",\"/;s/$/\"/}"
"{s/ Multirate: VMT:/\"/;s/ PwrCtrl/\",\"PwrCtrl/;s/ - /\",\"/;s/$/\"/}"
"{s/ Multirate:  VMT /\"/;s/ \- Timed/\",\"Timed/;s/$/\"/}"
)

# Flag for each search string event (graphed on same line or staggered lines)

# same  line per event
#  NOTE: PwrCtrl bit repeated on 2 lines to mux different search strings
declare -a evtPatternBin=(
  ",1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
  ",0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
",0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0"
  ",0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0"
",0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0"
  ",0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0"
  ",0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0"
  ",0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0"
  ",0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0"
  ",0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0"
  ",0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0"
  ",0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0"
  ",0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0"
  ",0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0"
  ",0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0"
  ",0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0"
  ",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1"
)

# different line per event (don't use spaces to make pretty - messes up copy)
#  NOTE: PwrCtrl bit repeated on 2 lines to mux different search strings
declare -a evtPatternOff=(
   ",16,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0"
   ",15,15,13,12,11,10,9,8,7,6,5,4,3,2,1,0"
 ",0,15,14,14,12,11,10,9,8,7,6,5,4,3,2,1,0"
   ",15,14,13,13,11,10,9,8,7,6,5,4,3,2,1,0"
 ",0,15,14,13,12,12,10,9,8,7,6,5,4,3,2,1,0"
   ",15,14,13,12,11,11,9,8,7,6,5,4,3,2,1,0"
   ",15,14,13,12,11,11,9,8,7,6,5,4,3,2,1,0"
   ",15,14,13,12,11,10,10,8,7,6,5,4,3,2,1,0"
   ",15,14,13,12,11,10,9,9,7,6,5,4,3,2,1,0"
   ",15,14,13,12,11,10,9,8,8,6,5,4,3,2,1,0"
   ",15,14,13,12,11,10,9,8,7,7,5,4,3,2,1,0"
   ",15,14,13,12,11,10,9,8,7,6,6,4,3,2,1,0"
   ",15,14,13,12,11,10,9,8,7,6,5,5,3,2,1,0"
   ",15,14,13,12,11,10,9,8,7,6,5,4,4,2,1,0"
   ",15,14,13,12,11,10,9,8,7,6,5,4,3,3,1,0"
   ",15,14,13,12,11,10,9,8,7,6,5,4,3,2,2,0"
   ",15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,1"
)

# Set evtPattern (Binary flags, or offset)
declare -a evtPattern=(${evtPatternOff[*]})

# Include common file to process the globally named data items
. nlgPostproc.sh

