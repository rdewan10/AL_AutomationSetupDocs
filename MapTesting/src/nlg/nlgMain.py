#!/usr/bin/env python

from alDefaults import *
from algMain import algNmspm, algTerm, algNms 
from aldbConf import aldbConf 
from altgEnv import setEnv
from threading import Timer
from datetime import *
from viasatSsh import *
import sys, time, signal, os, subprocess 

##############################################################################
#  Main NLG (network login)  Class  
#  Poll NmsPM and Terminal for Status and Save data using independent threads.
#   A poller is Launched by __main__ and runs until (SIGUSR1) is received
##############################################################################
class nlg(object):
    #########################################################################
    #  Initialize class; connect to configuration
    #########################################################################
    def __init__(self,groupId, termonly=False):
        self.groupId = groupId
        self.conf = aldbConf(self.groupId)
        self.nmsConf = self.conf.aldbConfNmsGuiGet()
        self.termConf = self.conf.aldbConfTermGuiGet()
        self.mapDirConf = self.conf.aldbConfDirsGet()
        self.tuningConf = self.conf.aldbTuningConfGet()
        self.nlgConf = self.conf.aldbConfNlgGet()
        self.hubsConf = self.conf.aldbConfHubsGet()
        if (self.hubsConf['hub1Name'] != ""):
            self.rtnms1Conf = self.conf.aldbConfRtnmsGet(self.hubsConf['hub1Name'])
        if (self.hubsConf['hub2Name'] != ""):
            self.rtnms2Conf = self.conf.aldbConfRtnmsGet(self.hubsConf['hub2Name'])
        self.termOnly = termonly

    #########################################################################
    #  Setup the NMSPM page for fast polling
    #########################################################################
    def nlgNmspmOpen(self):
        self.nmspm = algNmspm("http://"+ str(self.nmsConf['ip']) + ":" +
                str(self.nmsConf['port']), self.nmsConf['usern'],
                self.nmsConf['passw'], self.mapDirConf['resultDir'])
        self.nmspm.algNmspmLogin()
        self.nmspm.clickImage("img/navUncollapse.png")  # Hidden slider menu >>
        #self.nmspm.algNmspmSearchVmt(self.termConf['name']) 
        #self.nmspm.algNmspmGotoVmtBasic(self.termConf['name']) 
        #self.nmspm.clickButton("Refresh rate: Off")


    #########################################################################
    #  Setup the Terminal page for fast polling
    #########################################################################
    def nlgTermOpen(self):
        self.term = algTerm("http://"+ str(self.termConf['ip']) + ":" +
                str(self.termConf['port']), self.termConf['usern'],
                self.termConf['passw'], self.mapDirConf['resultDir'], vselPauseNlgTerm)
        self.term.algTermGoToPage()  


    #########################################################################
    #  close the NMSPM page and generate results
    #########################################################################
    def nlgNmspmClose(self):
        delta = self.stopTime - self.startTime
        self.nmspm.clickButton("Refresh rate: 30 seconds")
        self.nmspm.algNmspmChartScreenShots("FL", duration=delta.total_seconds())
        self.nmspm.algNmspmChartScreenShots("RL", duration=delta.total_seconds())
        #self.nmspm.algNmspmGetTrace("TraceFile")
        self.nmspm.algNmspmLogout()
        self.nmspm.disconnectFromServer()
        self.conf.aldbExportToCsv(self.mapDirConf['resultDir']+'nlgNmspmStatDb.csv', 'NmsPmVmtStatus', 'pollTime', self.startTime, self.stopTime)
        # Get events from the RTNMS syslog and place into results
        if (self.hubsConf['hub1Name'] != ""):
            self.vsshRtnms = viasatSsh(self.rtnms1Conf['ip'], self.rtnms1Conf['usern'], self.rtnms1Conf['passw'])
            self.vsshRtnms.getFile("/usr/local/rtnms/log/rtnms.log", self.mapDirConf['resultDir'] + self.hubsConf['hub1Name'] + rtnms0SyslogFn)
            cmd = ("./nlgPostprocRtnms.sh " + self.mapDirConf['resultDir'] + " " + self.hubsConf['hub1Name'] + rtnms0SyslogFn + " " + self.hubsConf['hub1Name'] + rtnms0SyslogEventFn)
            result = subprocess.check_output(cmd, shell=True)
            print(result)
            sys.stdout.flush()

        if (self.hubsConf['hub2Name'] != ""):
            self.vsshRtnms = viasatSsh(self.rtnms2Conf['ip'], self.rtnms2Conf['usern'], self.rtnms2Conf['passw'])
            self.vsshRtnms.getFile("/usr/local/rtnms/log/rtnms.log", self.mapDirConf['resultDir'] + self.hubsConf['hub2Name'] + rtnms0SyslogFn)
            cmd = ("./nlgPostprocRtnms.sh " + self.mapDirConf['resultDir'] + " " + self.hubsConf['hub2Name'] + rtnms0SyslogFn + " " + self.hubsConf['hub2Name'] + rtnms0SyslogEventFn)
            result = subprocess.check_output(cmd, shell=True)
            print(result)
            sys.stdout.flush()

        # Update ReDa
        self.conf.updateGroupConfig(self.groupId, dict(Status='complete'))

    #########################################################################
    #  close the Terminal page and generate results
    #########################################################################
    def nlgTermClose(self):
        self.term.algTermLogout()
        self.term.disconnectFromServer()
        self.conf.aldbExportToCsv(self.mapDirConf['resultDir']+'nlgTermStatDb.csv', 'TerminalStatus','pollTime', self.startTime, self.stopTime)

        # Get events from the Terminal syslog and place into results
        self.vsshTerm = viasatSsh(self.termConf['ip'], self.termConf['usern'], self.termConf['passw'])
        self.vsshTerm.getFile("/test/syslogMsgs", self.mapDirConf['resultDir'] + termSyslogFn)
        self.vsshTerm.getFile("/test/syslogMsgs.0", self.mapDirConf['resultDir'] + termSyslog0Fn)
        cmd = ("./nlgPostprocTerm.sh " + self.mapDirConf['resultDir'] + " " + termSyslogFn + " " + termSyslogEventFn)
        result = subprocess.check_output(cmd, shell=True)
        print(result)
        cmd = ("./nlgPostprocTerm.sh " + self.mapDirConf['resultDir'] + " " + termSyslog0Fn + " " + termSyslog0EventFn)
        result = subprocess.check_output(cmd, shell=True)
        print(result)
        sys.stdout.flush()

        # Update ReDa
        if (self.termOnly):
            self.conf.updateGroupConfig(self.groupId, dict(Status='complete'))

    #########################################################################
    #  Start the terminal and if necessary the nmspm
    #########################################################################
    def start(self):
        self.startTime = datetime.utcnow()
        signal.signal(signal.SIGUSR1, self.nlgSigHandler)
        self.nlgTermStart()
        if (not self.termOnly):
            self.nlgNmspmStart()

    #########################################################################
    #  Start NMSPM  Data collection data
    #########################################################################
    def nlgNmspmStart(self):
        self.nlgNmspmOpen()
        self.timerNmspmState = True
        # Schedule the Timer Thread
        self.timerNmspm = Timer(defNlgTimeoutNmspm,self.nlgNmspmTimerThread)
        self.timerNmspm.start()


    #########################################################################
    #  Start Terminal Data collection data
    #########################################################################
    def nlgTermStart(self):
        self.nlgTermOpen()
        self.timerTermState = True
        # Schedule the Timer Thread
        self.timerTerm = Timer(defNlgTimeoutTerm,self.nlgTermTimerThread)
        self.timerTerm.start()

    #########################################################################
    #  Stop the nmspm & terminal
    #########################################################################
    def stop(self):
        self.stopTime = datetime.utcnow()
        self.nlgTermStop()
        self.nlgNmspmStop()
        print "NLG Test for Group {} started at {} and ended at {}\n".format(self.groupId, self.startTime, self.stopTime)
        sys.stdout.flush()

    #########################################################################
    #  Stop NMSPM Data collection
    #########################################################################
    def nlgNmspmStop(self):
        self.timerNmspmState = False

    #########################################################################
    #  Stop Terminal Data collection
    #########################################################################
    def nlgTermStop(self):
        self.timerTermState = False

    #########################################################################
    #  Signal Handler
    #     Upon receipt of SIGUSR1; stop the running poll processor
    #########################################################################
    def nlgSigHandler(self, signum, stack):
        if signum == signal.SIGUSR1:
            self.conf.aldbConfNlgSet(pid=self.nlgConf['pid'], active=0)
            self.stop()

    #########################################################################
    #  Get NMSPM Terminal (VMT) Flight Data
    #########################################################################
    #def nlgNmspmGetTerminaFlight(self, nmspm):
        #print self.nmspm.algNmspmGetFlightHistory("Past week")
        #self.nmspm.clickButton("VMT List")
        #print self.nmspm.algNmspmGetFirstRow("xpath=//*[@id='abstractPanel']/div/div[2]/div[2]/div/div[1]/div/table/tbody[2]/tr","xpath=//*[@id='abstractPanel']/div/div[2]/div[2]/div/div[2]/div[1]/table/tbody[2]/tr[1]")
        #print self.nmspm.algNmspmFlightHistoryRow(2)


    #########################################################################
    #  Poll the NMSPM Terminal (VMT) Data and add entry to the database
    #    Assumes NMS Map window opened
    #########################################################################
    def nlgNmspmPollStatus(self):

        pollTime = datetime.utcnow()

        self.nmspm.algNmspmSearchVmt(self.termConf['name']) 
        myDict = self.nmspm.algNmspmGetVmtlist(self.termConf['name'])
        self.conf.aldbStatusNmspmVmtlistSet(pollTime=pollTime,**myDict) 

        time.sleep(1)
        self.nmspm.algNmspmGotoBasic(self.termConf['name']) 
        myDict = self.nmspm.algNmspmGetBasic()
        self.conf.aldbStatusNmspmBasicSet(pollTime=pollTime,**myDict) 

        sys.stdout.flush()

    #########################################################################
    #  Poll the Terminal Data and add entry to the database
    #    Assumes Terminal window opened
    #########################################################################
    def nlgTermPollStatus(self):

        pollTime = datetime.utcnow()

        #time.sleep(1)
        myDict=self.term.algTermStatusGeneral()
        self.conf.aldbStatusTerminalGenSet(pollTime=pollTime,**myDict) 

        time.sleep(1)
        myDict=self.term.algTermStatusFL()
        self.conf.aldbStatusTerminalFLSet(pollTime=pollTime,**myDict) 

        time.sleep(1)
        myDict=self.term.algTermStatusRL()
        self.conf.aldbStatusTerminalRLSet(pollTime=pollTime,**myDict) 

        time.sleep(1)
        myDict=self.term.algTermStatusACU()
        self.conf.aldbStatusTerminalACUSet(pollTime=pollTime,**myDict) 

        sys.stdout.flush()


    #########################################################################
    #  Timer Thread for collecting NSPM data
    #########################################################################
    def nlgNmspmTimerThread(self):
        if self.timerNmspmState :
            self.nlgNmspmPollStatus()
            # Start timer after - indeterminant duration of PollStatus
            self.timerNmspm = Timer(defNlgTimeoutNmspm,self.nlgNmspmTimerThread)
            self.timerNmspm.start()
        else:
            self.nlgNmspmClose()

    #########################################################################
    #  Timer Thread for collecting Term data
    #########################################################################
    def nlgTermTimerThread(self):
        if self.timerTermState :
            self.timerTerm = Timer(defNlgTimeoutTerm,self.nlgTermTimerThread)
            self.timerTerm.start()
            self.nlgTermPollStatus()
        else:
            self.nlgTermClose()

    #########################################################################
    #  NLG VMT Logout Command
    #########################################################################
    def nlgNmsVmtCommand(self, command):

        with algNms("http://"+ str(self.nmsConf['ip']) + ":" +
                str(self.nmsConf['port']), self.nmsConf['usern'],
                self.nmsConf['passw'], self.mapDirConf['resultDir']) as nms:

            nms.algNmsLogin()

            # TODO - fix to get 1 or 2
            if (command == "logout" ):
                nms.algNmsVmtLogout(self.termConf['name'], self.hubsConf['hub1Name'])
            elif (command == "relogin" ):
                nms.algNmsVmtRelogin(self.termConf['name'], self.hubsConf['hub1Name'])
            elif (command == "reboot" ):
                nms.algNmsVmtReboot(self.termConf['name'], self.hubsConf['hub1Name'])


    #########################################################################
    #  Start a backgroun running poller task for this group
    #########################################################################
    def nlgStartPoll(self):
        self.conf.aldbConfNlgSet(os.getpid(), active=1)
        self.start()

    #########################################################################
    #  Send signal to the running poller task for this group
    #########################################################################
    def nlgStopPoll(self):
        #print "Send a kill to pid={}\n".format(self.nlgConf['pid'], signal.SIGUSR1)
        os.kill(self.nlgConf['pid'], signal.SIGUSR1)

    #########################################################################
    #  MAIN Launch the poller and run until a stop signal (SIGUSR1) is received
    #########################################################################
if __name__ == '__main__':

    setEnv()

    groupId = int(sys.argv[1])
    termonly = True if sys.argv[2] == 'True' else False

    x=nlg(groupId, termonly)

    x.conf.aldbConfNlgSet(pid=os.getpid(), active=1)
    x.nlgConf = x.conf.aldbConfNlgGet()

    x.start()

    # Do we need to wait forever here to keep altgLaunched running ?
    #   No
