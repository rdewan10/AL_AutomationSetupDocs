#!/usr/bin/env python
from aldbConf import *
from string import Template
from cgiSetup import *
from alamMain import *
import datetime, time
import os, re, subprocess, random, sys

############################################################################
# Used to get a new groupId for a particular test/Configuration or to load
# the correct group when a group is specified to be loaded by the altg, also
# returns the FieldStorage object that it used, so it can be passed on to the
# other methods
############################################################################
def changeGroup():
    form = cgi.FieldStorage()
    if form.getvalue('groupId'):
        if re.search('-|,', form.getvalue('groupId')):
            groupId = form.getvalue('groupId')
        else :
            groupId = int(form.getvalue('groupId'))
    else:
        groupId = aldbConf.getGroup(aldbConnParmsGet(), False)
    return {'groupId': groupId, 'form': form}


############################################################################
# Convert short hand group ids, 
#    e.g. 539,541-543,529-530 to 539,541,542,543,529,530
############################################################################
def makeGroupList(groupIds, sort=True):
    groupIds = str(groupIds)

    # Expand any range patterns in groupIds
    ranges = re.findall("(\d+)\s*-\s*(\d+)", groupIds)
    for i in ranges:
        groupList = []
        for j in range(int(i[0]), int(i[1])+1):
            groupList.append(j)
        groupIds = re.sub(i[0]+"\s*-\s*"+i[1], str(groupList), groupIds)

    # Convert to integer list
    groupList = []
    for i in re.findall("(\d+)", groupIds):
        groupList.append(int(i))

    if sort:
        return sorted(set(groupList))
    else:
        return (groupList)


############################################################################
############################################################################
# Class confScreen provides the methods for the ALTG Main Config Screen
############################################################################
############################################################################
class confScreen(object):

    ############################################################################
    # conf is an aldbConf object, which is needed to set/get data from the
    # database
    ############################################################################
    def __init__(self, conf, form):
        self.conf = conf
        self.form = form

    ############################################################################
    # Gets the changes to the Map Bundles configuration through http post. And
    # then sets the changes in the database
    ############################################################################
    def confMapBundleChange(self):
        if self.form['filename'] != None and re.compile(".*\.zip$").match(self.form['filename'].filename):
            # change it to print the filename from the database if the groupId is
            # already stated
            fn = '/tmp/%s' % os.path.basename(self.form['filename'].filename)
            open(fn, 'wb').write(self.form['filename'].file.read())
        elif self.form.getvalue('mapFile') != "No file uploaded":
            fn = '/tmp/%s' % self.form.getvalue('mapFile')
        else:
            fn = "No file chosen"
        self.conf.aldbConfMapbunSet(fn, self.form.getvalue('mapbprofile'),
            self.form.getvalue('mapbscript'), self.form.getvalue('mapbsatname'),
            self.form.getvalue('mapbundlever'))

    ############################################################################
    # Gets the changes to the NMS/EMS Gui configuration through http post. And
    # then sets the changes in the database
    ############################################################################
    def nmsAccessChange(self):
        self.conf.aldbConfNmsGuiSet(self.form.getvalue('nmsip'),
            self.form.getvalue('nmsport'),
            self.form.getvalue('nmsuname'), self.form.getvalue('nmspw'))

    ############################################################################
    # Gets the changes to the hubs configuration through http post. And
    # then sets the changes in the database
    ############################################################################
    def hubsAccessChange(self):
        self.conf.aldbConfHubsSet(self.form.getvalue('hub1list'), 
            self.form.getvalue('hub2list'))

    ############################################################################
    # Gets the changes to the Terminal Gui configuratoin through http post. And
    # then sets the changes in the database
    ############################################################################
    def termAccessChange(self):
        self.conf.aldbConfTermGuiSet(self.form.getvalue('termip'),
            self.form.getvalue('termport'), self.form.getvalue('termuname'),
            self.form.getvalue('termpw'), self.form.getvalue('termname'),
            self.form.getvalue('termcmd'), self.form.getvalue('serial'))

    ############################################################################
    # Gets the changes to the group description configuration through http post. And
    # then sets the changes in the database
    ############################################################################
    def groupDescChange(self):
        self.conf.aldbConfGroupSet(self.form.getvalue('grptestc'),
            self.form.getvalue('grpdesc'), self.form.getvalue('grpstation'))

    def makeSubDict(self):
        subs = {}
        for key in self.form.keys():
            subs[key] = self.form.getvalue(key)
        if self.form['filename'] != None and re.compile(".*\.zip$").match(self.form['filename'].filename):
            fn = os.path.basename(self.form['filename'].filename)
            open('/tmp/%s' % fn, 'wb').write(self.form['filename'].file.read())
            subs['mapFile'] = fn
        if subs['termcmd'] == "Console":
            subs['termcmd1'] = 'Checked'
            subs['termcmd2'] = ''
        else:
            subs['termcmd1'] = ''
            subs['termcmd2'] = 'Checked'
        subs['hub1Name'] = subs['hub1list'] 
        subs['hub2Name'] = subs['hub2list'] 
        return subs

    def resetConf(self):
        self.conf.aldbConfMapbunSet()
        self.conf.aldbConfNmsGuiSet()
        self.conf.aldbConfTermGuiSet()
        self.conf.aldbConfHubsSet()
        self.conf.aldbTuningConfSet()
        self.conf.aldbGroupSet()

    ############################################################################
    # Prints the configuration screen, using the subs paramter as data to fill
    # in the fields
    ############################################################################
    def printScreen(self, subs=None):

        # printing of html
        template = Template("""Content-type: text/html\n\n
            <head>
            <title>Config-AL Test Automation</title>
            </head>
            <body>

            <form action="altgConfScreen.py" enctype="multipart/form-data"
            method="post">
            <fieldset>
            <legend>Currently Loaded Group</legend>
            <p>
            Group ID
            <input type="text" name="groupId" value=${groupId}>
            </p>
            <div>
            <input type="submit" value="Load">
            </div>
            </fieldset>

            <br>

            <fieldset>
            <table>
            <tr>
            <td align="right">Name:</td>
            <td align="left"><input type="text" size="50" name="grptestc" value="${grptestc}">
            </td>
            </tr>
            <tr>
            <td align="right">Description:</td>
            <td align="left"><input type="text" size="100" name="grpdesc" value="${grpdesc}">
            </td>
            </tr>
            <tr>
            <td align="right">Station:</td>
            <td align="left"><input type="text" size="50" name="grpstation" value="${grpstation}">
            </td>
            </tr>
            </table>
            <br>
            <input type="submit" value="Save" formaction="/cgi-bin/altgGroupDesc.py"
            enctype="multipart/form-data" method="post">
            </fieldset>

            <br>

            <fieldset>
            <legend>ArcLight Test Automation Map Bundles Configuration</legend>
            <p>
            Map Bundle File:
            <input type="file" name="filename" size="400">
            </p>
            <table>
	        <tr>
            <td align="right">Current Mapbun File:</td>
            <td align="left"><input type="text" name="mapFile" value="${mapFile}" readonly="readonly">
            </td>
            </tr>

            <tr>
            <td align="right">FL Profile:</td>
            <td align="left"><input type="text" name="mapbprofile" value="${mapbprofile}">
            </td>
            </tr>
            <tr>
            <td align="right">Install Script:</td>
            <td align="left"><input type="text" name="mapbscript" value="${mapbscript}">
            </td>
            </tr>
            <tr>
            <td align="right">SSCF Beam Name:</td>
            <td align="left"><input type="text" name="mapbsatname" value="${mapbsatname}">
            </td>
            </tr>
            <tr>
            <td align="right">Map Bundle Version:</td>
            <td align="left"><input type="text" name="mapbundlever" value="${mapbundlever}">
            </td>
            </tr>
            </table>
            <br>
            <input type="submit" value="Save" formaction="altgConfMapbundle.py"
            enctype="multipart/form-data" method="post">
            </fieldset>


            <br>

            <fieldset>
            <legend>ArcLight Test Automation NMS/EMS GUI Access Configuration</legend>
            <table>
            <tr>
            <td align="right">IP:</td>
            <td align="left"><input type="text" name="nmsip" value="${nmsip}">
            </td>
            </tr>
            <tr>
            <td align="right">Port:</td>
            <td align="left"><input type="text" name="nmsport" value=${nmsport}>
            </td>
            </tr>
            <tr>
            <td align="right">Username:</td>
            <td align="left"><input type="text" name="nmsuname" value="${nmsuname}">
            </td>
            </tr>
            <tr>
            <td align="right">Password:</td>
            <td align="left"><input type="password" name="nmspw" value="${nmspw}">
            </td>
            </tr>
            </table>
            <br>
            <input type="submit" value="Save" formaction="/cgi-bin/altgNmsAccess.py"
            enctype="multipart/form-data" method="post">
            </fieldset>

            <br>

            <fieldset>
            <legend>ArcLight Test Automation Terminal Access Configuration</legend>
            <table>
            <tr>
            <td align="right">IP:</td>
            <td align="left"><input type="text" name="termip" value="${termip}">
            </td>
            </tr>
            <tr>
            <td align="right">Port:</td>
            <td align="left"><input type="text" name="termport" value=${termport}>
            </td>
            </tr>
            <tr>
            <td align="right">Username:</td>
            <td align="left"><input type="text" name="termuname" value="${termuname}">
            </td>
            </tr>
            <tr>
            <td align="right">Password:</td>
            <td align="left"><input type="password" name="termpw" value="${termpw}">
            </td>
            </tr>
            <tr>
            <td align="right">Terminal Name:</td>
            <td align="left"><input type="text" name="termname" value="${termname}">
            </td>
            </tr>
            <tr>
            <td align="right">Terminal CLI:</td>
            <td>
		<align="left"><input type="radio" name="termcmd" value="Console" ${termcmd1}>Console
		<align="left"><input type="radio" name="termcmd" value="SSH" ${termcmd2}>SSH
	    </td>
            </tr>
            <tr>
            <td align="right">Console Port:</td>
            <td align="left"><input type="text" name="serial" value="${serial}">
            </td>
            </tr>
            </table>
            <br>
            <input type="submit" value="Save" formaction="altgTermAccess.py"
            enctype="multipart/form-data" method="post">
            </fieldset>
	    
            <br>

            <fieldset>
            <legend>ArcLight Test Automation Hub Association Configuration</legend>
            <table>
            <tr>
            <td align="right">Hub 1:</td>
            <td align="left"><input type="text" name="hub1Name" value="${hub1Name}" readonly>
            </td>
            </tr>
            <tr>
            <td></td>
            <td><select name="hub1list" >
                <option value="" selected>None</option>
                <option value="TA Hub EMS" >TA Hub EMS</option>
                <option value="Snowshoe">Snowshoe</option>
                <option value="Sugarloaf">Sugarloaf</option>
                <option value="Wintergreen">Wintergreen</option>
            </select>
            </td>
            </tr>
            <tr>
            <td align="right">Hub 2:</td>
            <td align="left"><input type="text" name="hub2Name" value="${hub2Name}" readonly>
            </td>
            </tr>
            <tr>
            <td></td>
            <td><select name="hub2list">
                <option value="" selected>None</option>
                <option value="TA Hub EMS">TA Hub EMS</option>
                <option value="Snowshoe">Snowshoe</option>
                <option value="Sugarloaf">Sugarloaf</option>
                <option value="Wintergreen">Wintergreen</option>
            </select>
            </td>
            </tr>
            </table>
            <br>
            <input type="submit" value="Save" formaction="/cgi-bin/altgHubsAccess.py"
            enctype="multipart/form-data" method="post">
            </fieldset>

            <br>
	    <a href="/cgi-bin/altgConfTuning.py?groupId=${groupId}"> Test Automation Tuning Parameters </a>
	    <br><br>
            <input type="submit" value="Reset" formaction="altgResetConf.py"
            enctype="multipart/form-data" method="post">
            <input type="submit" value="Lock Configuration" formaction="altgConfScreenLock.py"\
            enctype="multipart/form-data" method="post">
	    <br><br>
	    <a href="/cgi-bin/altgTestLauncher.py?groupId=${groupId}"> Test Launcher </a>
            <br><br>
            <a href="/index.html"> Main Screen </a>
            </fieldset>
            </form>



            </body>""")

        # Used for reset or coming from mainScreen
        if not(subs):
            mapbun = self.conf.aldbConfMapbunGet()
            nms = self.conf.aldbConfNmsGuiGet()
            term = self.conf.aldbConfTermGuiGet()
            hubs = self.conf.aldbConfHubsGet()
            grp = self.conf.aldbConfGroupGet()

            # Determine what CLI radio button should be checked
            if term['cli'] == 'Console':
                termcmd1 = 'Checked'
                termcmd2 = ''
            else:
                termcmd1 = ''
                termcmd2 = 'Checked'

            match = re.compile(".*\/([^\/]*\..*)$").match(mapbun['filename'])
            if match:
                mapFile = match.group(1)
            else:
                mapFile = "No file uploaded"


            subs = { 'groupId' : self.conf.groupId, 'mapFile': mapFile,
    	        'mapbprofile' : mapbun['profile'],
                'mapbscript' : mapbun['script'],
                'mapbsatname' : mapbun['satName'],
                'mapbundlever' : mapbun['bundleVersion'], 'nmsip' : nms['ip'],
                'nmsport' : nms['port'],'nmsuname' : nms['usern'],
                'nmspw' : nms['passw'], 
                'hub1Name' : hubs['hub1Name'], 'hub2Name' : hubs['hub2Name'],
                'termip' : term['ip'],
                'termport' : term['port'], 'termuname' : term['usern'],
                'termpw' : term['passw'], 'termname' : term['name'],
                'termcmd1' : termcmd1, 'termcmd2' : termcmd2,
                'serial': term['consolePort'], 'extra': 3,
                'grptestc': grp['TestCase'], 'grpdesc': grp['Description'], 'grpstation': grp['StationName']}

        print template.substitute(subs)

############################################################################
############################################################################
# Class confTuningScreen provides the methods for the ALTG Tuning Config Screen
############################################################################
############################################################################
class confTuningScreen(object):

    ############################################################################
    # conf is an aldbConf object, which is needed to set/get data from the
    # database
    ############################################################################
    def __init__(self, conf, form):
        self.conf = conf
        self.form = form

    ############################################################################
    # Gets the changes to the tuning paramaters configuration through http post.
    # And then sets the changes in the database
    ############################################################################
    def tuningChange(self):
        self.conf.aldbTuningConfSet(self.form.getvalue('tunepresdwell'), 
            int(self.form.getvalue('defbitrate')),
            int(self.form.getvalue('dnldBitRatePercent')),
            self.form.getvalue('hubname'),
            int(self.form.getvalue('flrxfreq')))
    def makeSubDict(self):
        subs = {}
        for key in self.form.keys():
            subs[key] = self.form.getvalue(key)
        return subs

    ############################################################################
    # Prints the configuration screen, uses the respective get methods from
    # aldbConf to get the configurations from the database
    ############################################################################
    def printScreen(self, subs=None):
        template = Template("""Content-type: text/html\n\n
        <head>
        <title>Tuning-AL Test Automation</title>
        </head>
        <body>

        <br>

        <form action="/cgi-bin/altgConfTuningParams.py"
        enctype="multipart/form-data" method="post">
        <fieldset>
        <legend>ArcLight Test Automation Tuning Parameters</legend>
        <table>
        <tr>
        <td align="right">Group ID:</td>
        <td align="left"><input type="text" name="groupId" value=${groupId} readonly="readonly">
        </td>
        </tr>
        <tr>
        <td align="right">Precedence Dwell (sec):</td>
        <td align="left"><input type="text" name="tunepresdwell" value=${tunepresdwell}>
        </td>
        </tr>
        <tr>
        <td align="right">Default Bitrate(kbps):</td>
        <td align="left"><input type="text" name="defbitrate" value=${defbitrate}>
        </td>
        </tr>
        <tr>
        <td align="right"> Download Bitrate Percentage:</td>
        <td align="left"><input type="text" name="dnldBitRatePercent" value=${dnldBitRatePercent}>
        </td>
        </tr>
        <tr>
        <td align="right">FL Rx Freq (MHzX10):</td>
        <td align="left"><input type="text" name="flrxfreq" value=${flrxfreq}>
        </td>
        </tr>
        </table>
        <br><br>
        <div>
        <input type="submit" value="Save">
        </div>
        </fieldset>
        <br>
	<a href="/cgi-bin/altgConfScreen.py?groupId=${groupId}"> View Configuration </a>
	<br><br>
	<a href="/cgi-bin/altgTestLauncher.py?groupId=${groupId}"> Test Launcher </a>
        </form>

        <a href="/index.html"> Main Screen </a>

        </body>""")

        if subs == None:
            tuning = self.conf.aldbTuningConfGet()
            subs = {'groupId': self.conf.groupId,
                'tunepresdwell': tuning['precedenceDwell'], 'defbitrate':tuning['defaultBitRate'],
                'dnldBitRatePercent':tuning['dnldBitRatePercent'], 'flrxfreq':tuning['flRxFreq'] }
        print template.substitute(subs)


############################################################################
############################################################################
# Class testLauncher provides the methods for the ALTG Test Launch Screen
############################################################################
############################################################################
class testLauncher(object):

    ############################################################################
    # Trickle, terminal, precedence, fllock, and all are merely strings (which
    # should be set to "Checked" or "") self.groupId is set to changeGroup(),
    # which will either return a specified group by the text field or the next
    # unlocked group. If it returns the next unlocked group, it will most likely
    # correspond ot a default configuration (hence why it is unlocked)
    ############################################################################
    def __init__(self):
        data = changeGroup()
        self.form = data['form']

        # This is to prevent the user from running a test on an unconfigured
        # group. If there is groupId in the post request, then it will get
        # the latest locked group, instead of the latest unlocked group. We can
        # safely  just subtract one becaause getGroup() in aldbConf adds one to
        # the latest locked group
        if self.form.getvalue('groupId'):
            self.groupId = data['groupId']
        else:
            self.groupId = str(aldbConf.getGroup(aldbConnParmsGet(), True))

    ############################################################################
    # Gets the selected test that was sent via post request and specifies it as
    # checked. Then runs the correct test by calling the Arclight Automation
    # Manager (alam)
    ############################################################################
    def selectTest(self):
        if self.form.getvalue('Test'):
            groupId = "{}".format(self.groupId)
            testList = self.form.getvalue('Test')
            cmd = ['./altgRunTests.py \"{}\" \"{}\" &'.format(self.groupId, testList)]
            #print(cmd)
            subprocess.Popen(cmd, shell=True)
            result = "Test %s started" % testList
        else:
            result = "No Test selected"

        return result



    ############################################################################
    # Prints the testLauncher screen, using the self instance variables
    # to determine if a test radio button should be selected by default and
    # using httpd post to pass along the radio button selection.
    ############################################################################
    def printScreen(self):
        template = Template("""Content-type: text/html\n\n
            <head>
            <title>Launcher-AL Test Automation</title>
            </head>
            <body>

            <form action="/cgi-bin/altgTestLauncher.py"
            enctype="multipart/form-data" method="post">
            <fieldset>
            <legend>Currently Loaded Group</legend>
            <table>
            <tr>
            <td align="right">Group ID:</td>
            <td align="left"><input type="text" name="groupId" value="${groupId}"> 
            </td>
            </tr>
            <tr>
            <td align="right">Name:</td>
            <td align="left"><input type="text" size="50" name="grptestc" value="${grptestc}" readonly="readonly">
            </td>
            </tr>
            <tr>
            <td align="right">Description:</td>
            <td align="left"><input type="text" size="100" name="grpdesc" value="${grpdesc}" readonly="readonly">
            </td>
            </tr>
            </table>
            <br>
            <div>
            <input type="submit" value="Load">
            </div>
            </fieldset>

            <br>

            <fieldset>
            <legend>ArcLight Test Automation Test Case Launcher</legend>
            <input type="checkbox" name="Test" value="upload">Map Bundle-Terminal Upload
            <br>
            <input type="checkbox" name="Test" value="trickle">Map Bundle-Trickle Download
            <br>
            <input type="checkbox" name="Test" value="fllock">Map Bundle-Forward Link Lock
            <br>
            <input type="checkbox" name="Test" value="precedence">Map Bundle-Precedence
            <br>
            <input type="checkbox" name="Test" value="nlgstart">NLG-Poll Start
            <br>
            <input type="checkbox" name="Test" value="nlgtermstart">NLG-Poll Term-only Start
            <br>
            <input type="checkbox" name="Test" value="nlgstop">NLG-Poll Stop
            <br>
            <input type="checkbox" name="Test" value="logout">NLG-VMT Logout
            <br>
            <input type="checkbox" name="Test" value="relogin">NLG-VMT ReLogin
            <br>
            <input type="checkbox" name="Test" value="reboot">NLG-VMT Reboot
            <br><br>
            <input type="submit" value="Start">
            </fieldset>
            <br>
            <a href="$link">Test Results</a>
            <br>
            </form>
            <a href="/index.html"> Main Screen </a>

            </body>
            </html>""")

        groupList = makeGroupList(self.groupId)
        if len(groupList) > 1:
            link = "/cgi-bin/altgTestResultsMain.py?groupList={}".format(groupList)
            subs = { 'groupId' : self.groupId, 'link': link, 'grptestc': "Multiple Groups", 'grpdesc': "See individual configuration for groups "+str(groupList) }
        else:
            link = "/cgi-bin/altgTestResults.py?groupId={}".format(self.groupId)
            self.conf = aldbConf(self.groupId)
            grp = self.conf.aldbConfGroupGet()
            subs = { 'groupId' : self.groupId, 'link': link, 'grptestc': grp['TestCase'], 'grpdesc': grp['Description'] }
        print template.substitute(subs)

############################################################################
############################################################################
# Class dbExportScreen provides the methods for the 
#   ALTG Status Databases Export Screen
############################################################################
############################################################################
class dbExportScreen(object):

    ############################################################################
    # conf is an aldbConf object, which is needed to set/get data from the
    # database
    ############################################################################
    def __init__(self, conf, form):
        self.conf = conf
        self.form = form

    ############################################################################
    # Get Database Export parameters through http post, and
    #   then export the database
    ############################################################################
    def exportSave(self):

        # Get the DB Table name, and start/stop times
        tableName = self.form.getvalue('dbtable')
        keyStart = self.form.getvalue('startdate')+" "+self.form.getvalue('starttime')
        keyEnd = self.form.getvalue('enddate')+" "+self.form.getvalue('endtime')

        # Construct a filename from the DB Table name and keyStart/keyEnd values
        filename = self.conf.aldbConfDirsGet()['resultDir'] + "dbx"+tableName+"_"+keyStart+"_"+keyEnd+".csv"
        filename = filename.replace(':','')
        filename = filename.replace('-','')
        filename = filename.replace(' ','')

        # Save the exported DB to the results for this group
        self.conf.aldbExportToCsv(filename, tableName, 'pollTime', keyStart,keyEnd)


    ############################################################################
    # Prints the Database Export screen, Pre-loads timestamp fields
    ############################################################################
    def printScreen(self, subs=None):
        template = Template("""Content-type: text/html\n\n
        <head>
        <title>Database Export-AL Test Automation</title>
        </head>
        <body>

        <br>

        <form action="/cgi-bin/altgDbExportSave.py"
        enctype="multipart/form-data" method="post">
        <fieldset>
        <legend>ArcLight Test Automation Database Export</legend>
        <table>
        <tr>
        <td align="right">Group ID:</td>
        <td align="left"><input type="text" name="groupId" value=${groupId} readonly="readonly">
        </td>
        </tr>
        <tr>
        <td><br></td>
        </tr>
        <td>Database Table:</td>
        <td><select required name="dbtable">
            <option value="">None</option>
            <option value="NmsPmVmtStatus">NMSPM Status</option>
            <option value="TerminalStatus">Terminal Status</option>
        </select>
        </td>
        </tr>
        <tr>
        <td align="right">Start Time:</td>
        <td><input type="date" name="startdate" value=${startdate} size=5>
        <td><input type="time" name="starttime" value=${starttime} size=5>
        </td>
        </tr>
        <tr>
        <td align="right">End Time:</td>
        </td>
        <td><input type="date" name="enddate" value=${enddate} size=5>
        <td><input type="time" name="endtime" value=${endtime} size=5>
        </tr>
        </table>
        <br>
        <div>
        <input type="submit" value="Export">
        </div>
        </fieldset>
        <br>
	<a href="/cgi-bin/altgTestResults.py?groupId=${groupId}"> Test Results </a>
        </form>


        <a href="/index.html"> Main Screen </a>

        </body>""")

        if subs == None:
            curDate = datetime.datetime.utcnow() 
            curTime = datetime.datetime.utcnow().time().strftime("%H:%M:%S")
            subs = {'groupId': self.conf.groupId,
                'startdate': curDate,
                'enddate': curDate,
                'starttime': curTime,
                'endtime': curTime}
        print template.substitute(subs)


############################################################################
# Class utilScreen provides the methods for the ALTG Utility Toolbox Screen
############################################################################
############################################################################
class utilScreen(object):

    ############################################################################
    # 
    ############################################################################
    def __init__(self):
        self.ogroupId = 1
        self.ngroupId = 1
        self.form = cgi.FieldStorage()
        if self.form.getvalue('ogroupId'):
            if re.search('-|,', self.form.getvalue('ogroupId')):
                self.ogroupId = self.form.getvalue('ogroupId')
        if self.form.getvalue('ngroupId'):
            if re.search('-|,', self.form.getvalue('ngroupId')):
                self.ngroupId = self.form.getvalue('ngroupId')


    ############################################################################
    # Gets the selected test that was sent via post request and specifies it as
    # checked. Then runs the correct test by calling the Arclight Automation
    # Manager (alam)
    ############################################################################
    def mapResult(self):
        if self.form.getvalue('Report'):
            reportList = self.form.getvalue('Report')
            if (len(reportList) <= 5):
                cmd = ['./utilsMapResults.sh -o \"{}\" -n \"{}\" {} > /var/www/html/{} &'.format(str(makeGroupList(self.ogroupId, sort=False)).strip('[]'), str(makeGroupList(self.ngroupId, sort=False)).strip('[]'), " ".join(str(x) for x in reportList), mapTestReportFn )]
            else:
                # Only one option selected
                cmd = ['./utilsMapResults.sh -o \"{}\" -n \"{}\" {} > /var/www/html/{} &'.format(str(makeGroupList(self.ogroupId, sort=False)).strip('[]'), str(makeGroupList(self.ngroupId, sort=False)).strip('[]'), reportList, mapTestReportFn )]
            subprocess.Popen(cmd, shell=True)
            result = "Report %s started" % reportList
        else:
            result = "No Report selected"

        return result

    ############################################################################
    # 
    ############################################################################
    def testMaint(self):
        if self.form.getvalue('Maint'):
            maintopt = self.form.getvalue('Maint')
            cmd = './utilsTestMaint.sh {}'.format(maintopt)
            result = subprocess.check_output(cmd, shell=True)
        else:
            result ="No Test Maintenance Option Selected"

        return result

    ############################################################################
    # 
    ############################################################################
    def testMaintWdog(self):
        if self.form.getvalue('Wdog'):
            dogopt = self.form.getvalue('Wdog')
            if (dogopt == "--on"):
                cmd = './utilsTestMaintWdog.sh &>/dev/null'
                subprocess.check_output(cmd, shell=True)
                result="Watchdog On"
            else :
                cmd = "ps aux | grep utilsTestMaintWdog"
                result = subprocess.check_output(cmd, shell=True)
        else:
            result=""

        return result

    ############################################################################
    # Prints the util screen, using the self instance variables
    # to determine if a test radio button should be selected by default and
    # using httpd post to pass along the radio button selection.
    ############################################################################
    def printScreen(self):
        template = Template("""Content-type: text/html\n\n
            <head>
            <title>Utilities-AL Test Automation</title>
            </head>
            <body>

            <form action="/cgi-bin/altgUtilScreen.py"
            enctype="multipart/form-data" method="post">
            <input type="hidden" name="Option" value="Report" />
            <fieldset>
            <legend>Map Bundles Test Report</legend>
            <table>
            <tr>
            <td align="right">Old Group List:</td>
            <td align="left"><input type="text" name="ogroupId" value="${ogroupId}"> 
            </td>
            </tr>
            <tr>
            <td align="right">New Group List:</td>
            <td align="left"><input type="text" name="ngroupId" value="${ngroupId}"> 
            </td>
            </tr>
            <br>
            <tr>
            <td align="right">Report Features:</td>
            <td align="left"><input type="checkbox" name="Report" value="--upload" >Terminal Upload
            <input type="checkbox" name="Report" value="--trickle" >Trickle Download
            <input type="checkbox" name="Report" value="--fllock" >Forward Link Lock
            <input type="checkbox" name="Report" value="--precedence" >Precedence
            <input type="checkbox" name="Report" value="--signed" >Signed Validation
            <input type="checkbox" name="Report" value="--compare" >SED/SSCF Differences
            </td>
            </tr>
            </table>
            <br>
            <input type="submit" value="Create">
            <br><br>
            <a href="$link">Test Report</a>
            <br>
            </fieldset>
            </form>

            <form action="/cgi-bin/altgUtilScreen.py"
            enctype="multipart/form-data" method="post">
            <input type="hidden" name="Option" value="Maint" />
            <fieldset>
            <legend>Test Maintenance</legend>
            <table>
            <tr>
            <td align="right">Action:</td>
            <td>
		<align="left"><input type="radio" name="Maint" value="" checked >None
		<align="left"><input type="radio" name="Maint" value="--status" >Status
		<align="left"><input type="radio" name="Maint" value="--skip" >Skip
		<align="left"><input type="radio" name="Maint" value="--stop" >Stop
		<align="left"><input type="radio" name="Maint" value="--statusnlg" >NLG Status
		<align="left"><input type="radio" name="Maint" value="--stopnlg" >NLG Stop
	    </td>
            </tr>
            </table>
            <br>
            <input type="submit" value="Submit">
            <br><br>
            </fieldset>
            </form>

            <form action="/cgi-bin/altgUtilScreen.py"
            enctype="multipart/form-data" method="post">
            <input type="hidden" name="Option" value="Wdog" />
            <fieldset>
            <legend>Test Maintenance Watchdog</legend>
            <table>
            <tr>
            <td align="right">Action:</td>
            <td>
		<align="left"><input type="radio" name="Wdog" value="--status" checked>Status
		<align="left"><input type="radio" name="Wdog" value="--on" >On
	    </td>
            </tr>
            </table>
            <br>
            <input type="submit" value="Submit">
            <br><br>
            </fieldset>
            </form>

            <a href="/index.html"> Main Screen </a>

            </body>
            </html>""")

        ogroupList = makeGroupList(self.ogroupId, sort=False)
        ngroupList = makeGroupList(self.ngroupId, sort=False)
        link = mapTestReportFn+'?'+str(random.randint(1,sys.maxint))
        subs = { 'ogroupId': ogroupList, 'ngroupId': ngroupList, 'link': link}
        print template.substitute(subs)

############################################################################
############################################################################
# Class confRtnmsScreen provides the methods for the ALTG RTNMS Config Screen
#   RTNMS list is not group Id based and is accessed by the hubName key
# TODO - NOT YET IMPLEMENTED - TABLE ENTERED IN SQL via CLI
############################################################################
############################################################################
class confRtnmsScreen(object):

    ############################################################################
    # Gets the changes to the rtnms configuration through http post. And
    # then sets the changes in the database
    ############################################################################
    def rtnmsAccessChange(self):
       self.conf.aldbConfRtnmsSet(self.form.getvalue('rtnmsip'), 
           self.form.getvalue('rtnmshubname'),
           self.form.getvalue('rtnmsuname'), self.form.getvalue('rtnmspw'))

    ############################################################################
    # Prints the RTNMS configuration screen, using the subs paramter as data to fill
    # in the fields
    ############################################################################
    def printScreen(self, subs=None):

        # printing of html
        template = Template("""Content-type: text/html\n\n
            <head>
            <title>Config-AL Test Automation</title>
            </head>
            <body>

            <form action="altgConfRtnms.py" enctype="multipart/form-data"
            method="post">

            <fieldset>
            <legend>ArcLight Test Automation RTNMS Access Configuration</legend>
            <table>
            <tr>
            <td align="right">IP:</td>
            <td align="left"><input type="text" name="rtnmsip" value="${rtnmsip}">
            </td>
            </tr>
            <tr>
            <td align="right">Hub Name:</td>
            <td align="left"><input type="text" name="rtnmshubname" value="${rtnmshubname}">
            </td>
            </tr>
            <tr>
            <td align="right">Username:</td>
            <td align="left"><input type="text" name="rtnmsuname" value="${rtnmsuname}">
            </td>
            </tr>
            <tr>
            <td align="right">Password:</td>
            <td align="left"><input type="password" name="rtnmspw" value="${rtnmspw}">
            </td>
            </tr>
            </table>
            <br>
            <input type="submit" value="Save" formaction="/cgi-bin/altgRtnmsAccess.py"
            enctype="multipart/form-data" method="post">
            </fieldset>

            <br>
	    <a href="/cgi-bin/altgConfTuning.py?groupId=${groupId}"> Test Automation Tuning Parameters </a>
	    <br><br>
            <input type="submit" value="Reset" formaction="altgResetConf.py"
            enctype="multipart/form-data" method="post">
            <input type="submit" value="Lock Configuration" formaction="altgConfScreenLock.py"\
            enctype="multipart/form-data" method="post">
	    <br><br>
	    <a href="/cgi-bin/altgTestLauncher.py?groupId=${groupId}"> Test Launcher </a>
            <br><br>
            <a href="/index.html"> Main Screen </a>
            </fieldset>
            </form>

            </body>""")

        # Used for reset or coming from mainScreen
        if not(subs):
            mapbun = self.conf.aldbConfMapbunGet()
            rtnms = self.conf.aldbConfRtnmsGet()

            subs = { 
                'rtnmsip' : rtnms['ip'], 'rtnmshubname' : rtnms['hubName'],
                'rtnmsuname' : rtnms['usern'], 'rtnmspw' : rtnms['passw'], 
                'extra': 3}

        print template.substitute(subs)


