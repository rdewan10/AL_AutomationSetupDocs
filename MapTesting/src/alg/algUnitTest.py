#!/usr/bin/env python 

from algMain import *
from aldbConf import *
from datetime import *
import time

class algUtestX:
    def checkItem (self, ctype, xdict, xdictname, xval ):
        xdictval = xdict[xdictname]
	status = 'FAILED'
        if ctype == 'STR':
            if xdictval == xval :
                status = 'PASSED'
        elif ctype == 'INT':
            if int(xdictval) == xval :
                status = 'PASSED'
        elif ctype == 'FLOAT':
            if float(xdictval) == xval :
                status = 'PASSED'

        print '{} validation of {} : {}'.format(status, xdictname, xdictval)

class algUtestTerm(algUtestX):
    def __init__(self):
        print '\n***Opening Term...{}\n'.format(datetime.now().time())
        #self.myterm = algTerm("http://192.168.106.1", "root", "XYZ", "./results") 
        #self.myterm = algTerm("http://192.168.94.1", "root", "XYZ", "./results") 
        #self.myterm = algTerm("http://192.168.100.1", "root", "XYZ", "./results", vselPauseNlgTerm) 
        self.myterm = algTerm("http://192.168.83.1", "root", "XYZ", "./results", vselPauseNlgTerm) 
        #self.myterm = algTerm("http://192.168.86.1", "root", "XYZ", "./results", vselPauseNlgTerm) 
        #self.myterm = algTerm("http://192.168.103.1", "root", "XYZ", "./results") 

    def close(self):
        self.myterm.disconnectFromServer()
        print '\n***Closed Term...{}\n'.format(datetime.now().time())

    def testAll(self):
        print '\n***Beginning Terminal Unit Test Suite...{}\n'.format(datetime.now().time())
        if self.benchmark:
            self.myterm.algTermGoToPage()
        self.testStatusGen()
        self.testStatusFL()
        self.testStatusRL()
        self.testStatusACU()
        print '\n***Ending Terminal Unit Test Suite...{}\n'.format(datetime.now().time())

    def testStatusGen(self):
        if not self.benchmark:
            print '\n****Executing Terminal Status Gen...{}\n'.format(datetime.now().time())
            self.myterm.algTermGoToPage()
        result = self.myterm.algTermStatusGeneral()
        print result
        #self.checkItem ( 'STR', result, 'VS_SSCFFileVersion', '109.1.1' )
        #self.checkItem ( 'INT', result, 'HW_CPUTemperature', 50 )
        #self.checkItem ( 'FLOAT', result, 'Pos_Latitude', 18.2 )

    def testStatusFL(self):
        if not self.benchmark:
            print '\n****Executing Terminal Status FL...{}\n'.format(datetime.now().time())
            self.myterm.algTermGoToPage()
        result = self.myterm.algTermStatusFL()
        print result

    def testStatusRL(self):
        if not self.benchmark:
            print '\n****Executing Terminal Status RL...{}\n'.format(datetime.now().time())
            self.myterm.algTermGoToPage()
        result = self.myterm.algTermStatusRL()
        print result

    def testStatusACU(self):
        if not self.benchmark:
            print '\n****Executing Terminal Status ACU...{}\n'.format(datetime.now().time())
            self.myterm.algTermGoToPage()
        result = self.myterm.algTermStatusACU()
        print result

class algUtestNmspm(algUtestX):
    def __init__(self):
        print '\n***Opening NMSPM...{}\n'.format(datetime.now().time())
        self.mynmspm = algNmspm("http://192.168.136.35:9090","wolf","wolf","./results") 
        self.mynmspm.algNmspmLogin()
        #self.vmtname = "SL - Monitor"
        #self.vmtname = "Terminal 12 - 86.1"
        #self.vmtname = "Terminal 03 - 100.1"
        #self.vmtname = "Terminal 21 83.1"
        #self.vmtname = "Terminal 05 - 94.1"
        self.vmtname = "Terminal 15 - 88.1"

    def close(self):
        self.mynmspm.algNmspmLogout()
        time.sleep(1)
        self.mynmspm.disconnectFromServer()
        print '\n***Closed NMSPM...{}\n'.format(datetime.now().time())

    def testAll(self):
        print '\n***Begining NMSPM  Unit Test Suite...{}\n'.format(datetime.now().time())
        self.testNmspmVmtList()
        self.testNmspmVmtBasic()
        self.testNmspmVmtChart()
        #self.testNmspmVmtTrace()
        #self.testNmspmVmtFlight()
        print '\n***Ending NMSPM  Unit Test Suite...{}\n'.format(datetime.now().time())

    def testNmspmVmtList(self):
        print '\n***Executing NMSPM  VMT List Item...{}\n'.format(datetime.now().time())
        self.mynmspm.clickImage("img/navUncollapse.png")  # Hidden slider menu >>
        self.mynmspm.algNmspmSearchVmt(self.vmtname)
        print self.mynmspm.algNmspmGetVmtlist(self.vmtname)

    def testNmspmVmtBasic(self):
        print '\n***Executing NMSPM  VMT Basic...{}\n'.format(datetime.now().time())
        self.mynmspm.algNmspmGotoBasic(self.vmtname)
        print self.mynmspm.algNmspmGetBasic()

    def testNmspmVmtChart(self):
        print '\n***Executing NMSPM  VMT Charts...{}\n'.format(datetime.now().time())
        self.mynmspm.algNmspmChartScreenShots("FL", duration=(60*60*3))
        self.mynmspm.algNmspmChartScreenShots("RL", duration=(60*60*6))
        #self.mynmspm.algNmspmChartScreenShot("testChart","Velocity (knots)","Altitude (feet)")

    def testNmspmVmtTrace(self):
        print '\n***Executing NMSPM  VMT Trace...{}\n'.format(datetime.now().time())
        self.mynmspm.algNmspmGetTrace("testTrace")

    def testNmspmVmtFlight(self):
        print self.mynmspm.algNmspmGetFlightHistory("Past week")
        self.mynmspm.clickButton("VMT List")
        print self.mynmspm.algNmspmGetFirstRow("xpath=//*[@id='abstractPanel']/div/div[2]/div[2]/div/div[1]/div/table/tbody[2]/tr","xpath=//*[@id='abstractPanel']/div/div[2]/div[2]/div/div[2]/div[1]/table/tbody[2]/tr[1]")
        print self.mynmspm.algNmspmFlightHistoryRow(2)

class algUtestNms(algUtestX):
    def __init__(self):
        print '\n***Opening NMS...{}\n'.format(datetime.now().time())
        self.mynms = algNms("http://192.168.136.142:9090","wolf","wolf","./results") 
        self.mynms.algNmsLogin()

    def close(self):
        self.mynms.algNmsLogout()
        time.sleep(1)
        self.mynms.disconnectFromServer()
        print '\n***Closed NMS...{}\n'.format(datetime.now().time())

    def testAll(self):
        print '\n***Begining NMS  Unit Test Suite...{}\n'.format(datetime.now().time())
        self.testNmsDnld()
        print '\n***Ending NMS  Unit Test Suite...{}\n'.format(datetime.now().time())

    def testNmsDnld(self):
        self.mynms.algNmsDnldMapProfile("Random", True, 1000, True, "v1.169.vca00_afs00.sgn.zip", "scriptReboot-1.0.0.3.sh.vca00_", "SL-ACSM", 50, ['Terminal 05 - 94.1'])

    def testNmsVmtCommands(self):
        print '\n***Executing NMSPM  VMT Logout Command...{}\n'.format(datetime.now().time())
        self.mynms.algNmsVmtLogout("Terminal 05 - 94.1", "TA Hub EMS")
        print '\n***Executing NMSPM  VMT Relogin Command...{}\n'.format(datetime.now().time())
        self.mynms.algNmsVmtRelogin("Terminal 05 - 94.1", "TA Hub EMS")
        print '\n***Executing NMSPM  VMT Reboot Command...{}\n'.format(datetime.now().time())
        self.mynms.algNmsVmtReboot("Terminal 05 - 94.1", "TA Hub EMS")


if __name__ == '__main__':

    print "Please setup the __main__ to run the desired unit test(s)\n"

    #t = algUtestTerm()
    #t.benchmark = True
    #t.testAll()
    #t.close()

    npm = algUtestNmspm()
    npm.testNmspmVmtList()
    npm.testNmspmVmtBasic()
    #npm.mynmspm.algNmspmChartScreenShots("FL", duration=(60*60*3) )
    #npm.testAll()
    npm.close()

    #nms = algUtestNms()
    #nms.testAll()
    #nms.testNmsVmtCommands()
    #nms.close()

