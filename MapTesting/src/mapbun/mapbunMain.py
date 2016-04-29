##########################################################################
### mapbun Class
###   executes mapbundle test suite.
###   See //Arclight/ArcLight/AcceptanceTest/Automation/MapTesting/Docs/AL_Automation_SDD.docx
###
###########################################################################

from alDefaults import *
from aldbConf import aldbConf
from vselMain import *
from algMain import *
from TermSerialCom import *
from termLinkSSH import termLinkSSH as termLinkSSH, TermCmd as TermCmdSSH, Cmd as Cmd
import subprocess, ast
import time, re, sys, os
import csv

class mapbun(object):
    ###########################################################################
    ### mapbun()
    ###   Class Instantiation
    ###      Set up class local variables prior to configuration
    ###
    ###   Inputs:
    ###      groupId - GroupId for this instance
    ###
    ###########################################################################
    def __init__(self, groupId):
        self.grpId = groupId
        self.conf = aldbConf(self.grpId)
        self.nmsConf = self.conf.aldbConfNmsGuiGet()
        self.termConf = self.conf.aldbConfTermGuiGet()
        self.mapConf = self.conf.aldbConfMapbunGet()
        self.mapDirConf = self.conf.aldbConfDirsGet()
        self.tuningConf = self.conf.aldbTuningConfGet()
        self.hubsConf = self.conf.aldbConfHubsGet()

        # Will be changed and detected by tuningConfGet()
        self.returnLink = False
        self.debugFwdLink = True

        if self.termConf['cli'] == 'SSH':
            self.SSH = True
        else:
            self.SSH = False

    ###########################################################################
    ### mapbunConf()
    ###   Inputs:
    ###       lock - False(defaut); True to indicate re-prep files
    ###   initializes the aldbConfMapbunDetailed dictionary along with starting
    ###   both matlab excutables
    ###
    ###########################################################################
    def mapbunConf(self, lock=False):

        # Abort if it is not time to configure
        if self.mapConf['filename'] == "No file chosen":
            print "No mapfile to configure; may be for other tests\n"
            return

        # Create unique filenames for this map version
        self.satlistFile = 'satlist_v' + str(self.mapConf['bundleVersion'] + '.txt')
        self.precbyidFile = 'coords_precid_v' + str(self.mapConf['bundleVersion'] + '.csv')
        self.precbynameFile = 'coords_precname_v' + str(self.mapConf['bundleVersion'] + '.csv')
        self.coordsFile = 'coords_v' + str(self.mapConf['bundleVersion'] + '.txt')
        self.mapFile = 'map_v' + str(self.mapConf['bundleVersion'] + '.pdf')
        #see kmlFile below, after sed version determined

        lsOutput = ""
        if (not lock):
            cmd = subprocess.Popen(["ls " + self.mapDirConf['baseDir'] + "/*.agt " + self.mapDirConf['baseDir'] + "/*.agt.sgn "], stdout=subprocess.PIPE, shell=True)
            lsOutput,lsError = cmd.communicate()
        if(not(lsOutput)):
            cmd = ("./mapbunPrepFiles.sh " + self.mapDirConf['baseDir'] + " " +
                self.mapConf['filename'] + " " + self.mapConf['bundleVersion'] +
                " '" + self.mapConf['satName'] + "' " + sedFile + " " + sscfFile + " " + gdrmFile + " " + rlcFile + " " + sednomd5File + " " + sscfnomd5File + " " + gdrmnomd5File + " " + rlcnomd5File)
            result = ast.literal_eval(subprocess.check_output(cmd, shell=True))
            self.conf.aldbConfMapbunDetailedSet(**result)
            newgroup = True
            print(result)
            sys.stdout.flush()
        else:
            newgroup = False

        self.termMapverConf = self.conf.aldbConfMapbunDetailedGet()
        self.kmlFile = 'G_Earth_v' + str(self.termMapverConf['sedVersion'] + '.kml')
        if(self.termMapverConf['signed']):
            self.postfixExt='.sgn'
            self.postfixMap='.vca00_afs00.sgn.zip'
        else:
            self.postfixExt=''
            self.postfixMap='.zip'

        # Override FL Rx Freq if operator set it
        if(self.tuningConf['flRxFreq']):
            print("\nWarning: Operator overriding FL Rx Freq from {} to {} MHz\n".format(float(self.termMapverConf['flRxFreq'])/10.0, float(self.tuningConf['flRxFreq'])/10.0))
            self.termMapverConf['flRxFreq'] = self.tuningConf['flRxFreq']
            self.conf.aldbConfMapbunDetailedSet(**self.termMapverConf)

        self.antennaName = antennaNamesDict[self.termMapverConf['antennaType']]
        self.antennaLoFreq = self.mapbunTermLoFreq(self.termMapverConf['antennaType'], self.termMapverConf['flRxFreq'])
        self.termLbandFreq = self.termMapverConf['flRxFreq'] - self.antennaLoFreq

        # Detect AL2 setup and update for Mixer if Lband is out of range
        if (self.termMapverConf['pilot'] == '4') or (self.termMapverConf['pilot'] == '5'):
            print("\nWarning: Special Pilot detected; use AL2 Testbed (SAM4/FLM4) for FLLock Testing.\n")

            if (self.termLbandFreq > maxFlmLband):
                sigGen = self.termLbandFreq - mixerAl2Lband
                flmLband = mixerAl2Lband
            	print("Warning: Mixer Required-SigGen({})/FlmLBand({})/TermLBand({})\n".format(sigGen, flmLband, self.termLbandFreq))
            	print("Mixer Connections: FLM to (R), Sig-Gen to (L), and Terminal to (I)\n")
        
        # Changes the antenna type if the LbandFreq is out of range
        if self.termLbandFreq < 9500 or self.termLbandFreq > maxEflmLband:
            if self.termLbandFreq < 9500:
                antennaType = '51'
            else:
                antennaType = '1'

            self.termMapverConf['antennaType'] = antennaType
            self.conf.aldbConfMapbunDetailedSet(**self.termMapverConf)
            self.antennaName = antennaNamesDict[antennaType]
            self.antennaLoFreq = self.mapbunTermLoFreq(self.termMapverConf['antennaType'], self.termMapverConf['flRxFreq'])
            self.termLbandFreq = self.termMapverConf['flRxFreq'] - self.antennaLoFreq
            if 9500 > self.termLbandFreq > maxEflmLband:
                print("\nError: Terminal LBand out of range 950-{}MHz, cannot adjust so everything will fail.\n".format(maxEflmLband))
            else:
                print("\nWarning: Terminal LBand was out of range 950-{}MHz, antenna type changed to {}:{}.\n".format(maxEflmLband, self.termMapverConf['antennaType'], self.antennaName))

        # Prep stuff for Matlab
        if newgroup:
            coordfile =  open(self.mapDirConf['configDir'] + self.satlistFile, 'w')
            coordfile.write('{}\n'.format(self.mapConf['satName']))

            coordfile.flush()

            cmd = './run_findAllCoords.sh ' + matlabLibPath + ' ' + self.mapDirConf['configDir'] + sednomd5File + ' ' + self.mapDirConf['configDir'] + sscfnomd5File + ' ' +  self.mapDirConf['configDir'] + self.satlistFile + ' ' + self.mapConf['bundleVersion'] + ' ' + self.mapDirConf['resultDir'] + self.precbyidFile + ' ' + self.mapDirConf['resultDir'] + self.precbynameFile + ' ' +  self.mapDirConf['configDir'] + self.coordsFile + ' ' + self.mapDirConf['resultDir'] + self.mapFile
            result = subprocess.check_output(cmd, shell=True)

            # Generate kml file for this bundle
            cmd = './mapbunSed2Kml.sh ' + matlabLibPath + ' ' + self.mapDirConf['configDir'] + ' ' + sednomd5File + ' ' + self.kmlFile
            result = subprocess.check_output(cmd, shell=True)

            # Open coords csv file
            coords = open(self.mapDirConf['configDir'] + "coords_precname_v{}.csv".format(self.mapConf['bundleVersion']))

        # Gets best lat and long from coords file to be used for FLLock
        self.flLat = 0
        self.flLong = 0
        minSats = sys.maxint
        coordsId = open(self.mapDirConf['configDir'] + "coords_precid_v{}.csv".format(self.mapConf['bundleVersion']))
        coordsIdFile = csv.reader(coordsId)
        for row in coordsIdFile:
            if int(row[0].strip()) == int(self.termMapverConf['satId']):
                if len(row) - 3 < minSats:
                    sats = map(lambda x: x.strip(), row[3:])
                    minSats = len(row) - 3
                    self.flLat = float(row[1].strip())
                    self.flLong = float(row[2].strip())

        if newgroup or self.tuningConf['flRxFreq']:
            print("\nLatitude: {} Longitude: {} LoFreq: {} LbandFreq: {} FLRxFreq: {} Antenna: {} Terminal: {}\n".format(self.flLat, self.flLong, float(self.antennaLoFreq)/10.0, float(self.termLbandFreq)/10.0, float(self.termMapverConf['flRxFreq'])/10.0, self.antennaName, self.termConf['name']))


    ###########################################################################
    ### mapbunTrickle()
    ###   Inputs:
    ###     self - object id
    ###     testId - test id for this self.groupId
    ###
    ###   Setup the Trickle, wait for it to complete and verify at the Terminal
    ###
    ###########################################################################
    def mapbunTrickle(self, testId):

        result = "FAILED"
        state = "START"

        with algNms("http://"+ str(self.nmsConf['ip']) + ":" +
                str(self.nmsConf['port']), self.nmsConf['usern'],
                self.nmsConf['passw'], self.mapDirConf['resultDir']) as nms, algTerm("http://"+ str(self.termConf['ip']) + ":" + str(self.termConf['port']), self.termConf['usern'], self.termConf['passw'], self.mapDirConf['resultDir']) as term:

            # Checks to see if the terminal's state is Locked, 
            #   if so and not the new bundle, then it doesn't upload the baseline
            status = term.algTermStatusFLLock()
            if status and status['flState'] == "Locked" and not self.termStatusVerify(term):
                state = "LOCKED"
            else:
                self.mapbunBaseline(term)

            nms.algNmsLogin()
            # term.algTermLogin()
            mapfile = "v{}{}".format(self.mapConf['bundleVersion'],self.postfixMap)
            zipfile = self.mapDirConf['baseDir'] + mapfile


            nms.algNmsDnldMapUpload(zipfile, self.termMapverConf['signed'],
                self.antennaName)
            state = "UPLOAD"

            sys.stdout.flush()
            nms.algNmsDnldMapProfile("Trickle_v{}".format(self.mapConf['bundleVersion']),
                True, self.tuningConf['defaultBitRate'],
                self.termMapverConf['signed'], mapfile, self.mapConf['script'],
                self.mapConf['profile'], self.tuningConf['dnldBitRatePercent'],
                [self.termConf['name']])

            # Currently there is no return link (self.returnLink is set to false)
            # if set to true then this code will check the status of the map
            # download from the Nms Gui

            time.sleep(240) # Replace with the trickle time estimate when available
            state = "SENT"

            nms.algNmsDisableDnldProfiles()
            nms.algNmsLogout()

            if state == "SENT":
                if self.termStatusVerify(term):
                    # Save the MD5 if needed
                    self.mapbunTermMd5(termTrickleFn)
                    result = "PASSED"
                else:
                    result = "FAILED"

            # Add the results to Reda, and save screenshots to results
            term.scrollToText("GDRM File Version")
            term.algScreenShot("mapbunTrickleTermVers")

        return result

    ###########################################################################
    ### mapbunUpload()
    ### Inputs:
    ###     testId - testId for this groupId
    ###
    ### Uploads files from new mapbundle to the terminal and compares the
    ### versions that the terminal gets with the ones we grab from the files.
    ###########################################################################
    def mapbunUpload(self, testId, reboot=False):

        with algTerm("http://"+ str(self.termConf['ip']) + ":" + str(self.termConf['port']), self.termConf['usern'], self.termConf['passw'], self.mapDirConf['resultDir']) as term:
            term.algTermLogin()

            # Determine if you have all 4 files in the bundle, or only 2
            # (maybe improve with filename dictionary)
            if (self.termMapverConf['gdrmVersion']):
                rlcfn = self.mapDirConf['configDir'] + rlcFile + self.postfixExt
                gdrmfn = self.mapDirConf['configDir'] + gdrmFile + self.postfixExt
            else:
                rlcfn = None
                gdrmfn = None

            # Upload the files on the terminal
            term.algTermMapUpload(self.mapDirConf['configDir'] + sedFile + self.postfixExt,
                self.mapDirConf['configDir'] + sscfFile + self.postfixExt, rlcfn, gdrmfn)

            # Check the upload version values on the terminal
            termVerConf = term.algTermConfVersion()

            if termVerConf['sedVersion'] == self.termMapverConf['sedVersion'] and termVerConf['sscfVersion'] == self.termMapverConf['sscfVersion'] and termVerConf['rlcVersion'] == self.termMapverConf['rlcVersion'] and termVerConf['gdrmVersion'] == self.termMapverConf['gdrmVersion']:
                result = "PASSED"
            else:
                result = "FAILED"

            term.algTermConfVerSave()

            # Add the results to Reda, and save screenshots to results
            term.algScreenShot("mapbunUploadVers")

            if reboot:
                term.algTermConfVerReboot()
                time.sleep(180)

                # Save the MD5 if needed
                self.mapbunTermMd5(termUploadFn)


        return result

    ###########################################################################
    ### mapbunFLLock()
    ###     Executes the FLLock test, by changing the forward link parameters on
    ###     the EMS to match the bundle and beam specified and then monitoring
    ###     the terminal.
    ###
    ###########################################################################
    def mapbunFLLock(self, testId):
        result = 'FAILED'

        # Uploads the correct bundle to the terminal if versions are different
        if not self.termStatusVerify():
            self.mapbunUpload(testId, True)
    
        with algEms("http://"+ str(self.nmsConf['ip']) + ":" +
            str(self.nmsConf['port']), self.nmsConf['usern'],
            self.nmsConf['passw'], self.mapDirConf['resultDir']) as ems:

            # Workaround for Ka systems on EMS GUI
            kfreq = self.termMapverConf['flRxFreq']
            if (kfreq < 107000 or kfreq > 127500):
                kfreq = 127000

            ems.algEmsLogin()
            ems.algEmsAcsmFlUpdate(self.mapConf['profile'], self.hubsConf['hub1Name'], self.termLbandFreq, kfreq, self.termMapverConf['flChipRate'])
            ems.algEmsFlEnable(self.hubsConf['hub1Name'])
            ems.algEmsLogout()

        state = "FLTX"
        # need to pass in log file
        logFile = open(self.mapDirConf['resultDir'] + termFLLockFn, 'a+')
        if self.SSH:
            tl = termLinkSSH(self.termConf['ip'], self.termConf['usern'], self.termConf['passw'], logFile)
            termCmd = TermCmdSSH(tl)
        else:
            tl = TerminalLink(self.termConf['port'], logFile)
            termCmd = TermCmd(tl)
            termCmd.login()

        termCmd.setLatLong(self.flLat, self.flLong)
        termCmd.setAntenna(self.termMapverConf['antennaType'])
        Cmd(tl, "sed -ri 's/(.*),(.*),(.*),(.*),(.*),[0-9]+,(.*)/\\1,\\2,\\3,\\4,\\5,{},\\6/' {}/{}".format(self.tuningConf['precedenceDwell'], termConfig[self.termConf['consolePort']]['path'], sscfnomd5File), termCmd.resp_shellPrompt).send()
        termCmd.reboot()
        termCmd.tl.close()
        state = "REBOOT"

        with algTerm("http://"+ str(self.termConf['ip']) + ":" +
            str(self.termConf['port']), self.termConf['usern'],
            self.termConf['passw'], self.mapDirConf['resultDir']) as term:

            if state == "REBOOT":
                timeout = time.time() + self.mapbunGetDwell(self.flLat, self.flLong) #Maritime timeout
                while time.time() < timeout:
                    status = term.algTermStatusFLLock()
                    if status['flState'] == "Locked":
                        state = "LOCKED"
                        break
                    else:
                        time.sleep(5)


            if state == "LOCKED":
                # Normally L-Band, but for spectral inversion only RF will match
                flockstat = term.algTermStatusFLLock()
                if flockstat['lbandFreq'] == self.termLbandFreq or flockstat['dlFreq'] == self.termMapverConf['flRxFreq']:
                    result = "PASSED"
                else:
                    result = "FAILED"
            else:
                result = "FAILED"

            # Add the results to Reda
            term.algScreenShot("algTermStatusFLLock")
            time.sleep(20)

        return result

    ###########################################################################
    ### mapbunPrecedence()
    ###     Executes the precedence test by changing the terminal's lat and long
    ###     and then rebooting and monitoring/verifying its output (with the
    ###     use of other internal functions)
    ###
    ###########################################################################
    def mapbunPrecedence(self, testId):

        # Uploads the correct bundle to the terminal if versions are different
        if not self.termStatusVerify():
            self.mapbunUpload(testId, True)
    
        with algEms("http://"+ str(self.nmsConf['ip']) + ":" + str(self.nmsConf['port']), self.nmsConf['usern'], self.nmsConf['passw'], self.mapDirConf['resultDir']) as ems:
            ems.algEmsLogin()
            ems.algEmsFlDisable(self.hubsConf['hub1Name'])

            subprocess.call(["rm", "-f", self.mapDirConf['resultDir'] + termPrecLogFn, self.mapDirConf['resultDir'] + precVerifyLogFn, self.mapDirConf['resultDir'] + precVerifyErrFn])
            termLogFile = open(self.mapDirConf['resultDir'] + termPrecLogFn, 'ar+')
    
            # Creates the correct terminal link
            if self.SSH:
                tl = termLinkSSH(self.termConf['ip'], self.termConf['usern'], self.termConf['passw'], termLogFile)
                termCmd = TermCmdSSH(tl)
            else:
                tl = TerminalLink(self.termConf['port'], termLogFile)
                termCmd = TermCmd(tl)
                termCmd.login()
            zoneid = 0
            latLongs = []
    
            # Command sent to the terminal for it to change its sscf file so that
            # the dwell times aren't too long. It uses the tuningConf variables to
            # determine if its too long
            Cmd(tl, "sed -ri 's/(.*),(.*),(.*),(.*),(.*),[0-9]+,(.*)/\\1,\\2,\\3,\\4,\\5,{},\\6/' {}/{}".format(self.tuningConf['precedenceDwell'], termConfig[self.termConf['consolePort']]['path'], sscfnomd5File), termCmd.resp_shellPrompt).send()
    
            # Finds each lat and long set from the coords file, sets the terminal to those coords and antenna, then reboots and greps the log file
            with open(self.mapDirConf['configDir'] + "coords_v{}.txt".format(self.mapConf['bundleVersion'])) as coords:
                for line in iter(coords.readline, ''):
                    latLong = re.match("([-\d\.]+),([-\d\.]+)", line).groups()
                    zoneid += 1
                    latLongs.append(latLong)
                    sys.stdout.flush()
    
                    # This is needed so we can determine in our terminal log file, which cooordinates each set of satellites belongs too
                    termLogFile.write("Setting coordinates to {}, {}\n".format(latLong[0], latLong[1]))
                    termCmd.setLatLong(latLong[0], latLong[1])
                    termCmd.setAntenna(self.termMapverConf['antennaType'])
                    termCmd.rmFile('/test/syslogMsgs')
                    sys.stdout.flush()

                    termCmd.reboot()
                    termCmd.login()
    
                    sys.stdout.flush()
                    time.sleep(self.mapbunGetDwell(float(latLong[0]), float(latLong[1])))
                    termCmd.grepLog("Set Antenna")
                    sys.stdout.flush()
            termCmd.ctrlC()
            # tl.close() closes the terminalLog file that is passed into the terminalLink constructor
            termCmd.tl.close()
            termLogFile = open(self.mapDirConf['resultDir'] + termPrecLogFn, 'r')
            f = open(self.mapDirConf['resultDir'] + precVerifyLogFn, "a+")
    
            # For each lat long pair, it converts the terminal log output into an output simliar to the coords_precname file
            for latLon in latLongs:
                f.write(latLon[0] + ", " + latLon[1])
                for line in iter(termLogFile.readline, ''):
                    setCoords = re.search("Setting coordinates to ([-\d\.]+), ([-\d\.]+)", line)
                    if setCoords and setCoords.groups() != latLon:
                        sys.stdout.flush()
                        break;
                    if "Set Antenna" in line:
                        if "grep" in line:
                            pass;
                        else:
                            line = line.split(',')
                            for half in line:
                                if "cant:" in half:
                                    half1 = half.split()
                                    f.write(", {}".format(half1[0]))
                f.write("\n")
    
            sys.stdout.flush()
            termLogFile.close()
            f.close()

            ems.algEmsFlEnable(self.hubsConf['hub1Name'])
            ems.algEmsLogout()

        if self.mapbunPrecedenceVerify(self.mapDirConf['resultDir'] + "coords_precname_v{}.csv".format(self.mapConf['bundleVersion']), self.mapDirConf['resultDir'] + precVerifyLogFn, self.mapDirConf['resultDir'] + precVerifyErrFn):
            result = "PASSED"
	else:
            result = "FAILED"

        # Add the results to Reda

        return result
	

    ###########################################################################
    ### mapbunPrecedenceVerify()
    ###
    ### Returns
    ###   True if the precedence result matches the computed
    ###   Otherwise False
    ###   Puts errors into errFileName
    ###
    ###########################################################################
    def mapbunPrecedenceVerify(self, compFileName, resultFileName, errFileName):

        # Call to an internal function that maps the truncated names in the sed file to the full names in the sscf file
        beamDict = self.mapbunSedToSscf(self.mapDirConf['configDir']+sednomd5File, self.mapDirConf['configDir']+sscfnomd5File)

        # Open files
        comp=open(compFileName)
        result=open(resultFileName)
        errs=open(errFileName, 'w+')

        # Split files into rows
        compfile = csv.reader(comp)
        resfile = csv.reader(result)

        # Verify each row in computed file matches the result file
        comprownum = 0
        errors = False
        for comprow in compfile:
            comprownum += 1
            errs.write ("Processing row {}...\n".format(comprownum))
            passnum = 0

            # Error out if there is not a corresponding log file row
            try:
                resrow = resfile.next()
            except StopIteration:
                errs.write ("\tMore rows in computed  file than results file.\n")
                errs.write ("\t\tExiting...\n")
                errors = True
                break

            # Go to next computed row if there are not as many satellites in results row as in computed row
            if len(resrow)-2 < len(comprow)-3:
                errs.write ("\tNot enough satellites in row {} of log file.\n".format(comprownum))
                errors = True
                continue

            # Report error if the lattitudes of the two files don't match
            if comprow[1].strip() == resrow[0].strip():
                passnum += 1
            else:
                errs.write ("\tLattitude mismatch in row {}\n".format(comprownum))
                errs.write ("\t\tcomputed ={}, result = {}\n".format(comprow[1],resrow[0]))
                errors = True

            # Report error if the longitudes of the two files don't match
            if comprow[2].strip() == resrow[1].strip():
                passnum += 1
            else:
                errs.write ("\tLongitude mismatch in row {}\n".format(comprownum))
                errs.write ("\t\tcomputed ={}, result ={}\n".format(comprow[2],resrow[1]))
                errors = True

            # Verify each of the satellites in the computed row match the order in result row
            for i in range(3,len(comprow)):
                if comprow[i].strip() == beamDict[resrow[i-1].strip()]:
                    passnum += 1
                else:
                    errs.write ("\tSatellite mismatch for row {}, satellite {}\n".format(comprownum,i-2))
                    errs.write ("\t\tcomputed ={}, result ={}\n".format(comprow[i],beamDict[resrow[i-1].strip()]))
                    errors = True

            # Check if list of satellites in results file repeats properly
            # Which satellite in row of result file we are comparing to
            # For each repeated satellite in log file row
            j = 2
            for i in range(len(comprow)-1,len(resrow)):
                # If repeating more than once, look at the first satellite in computed file row
                if j == len(comprow)-1:
                    j = 2
                # Report error if repeated satellite in result file is not correct name
                if resrow[j].strip() == resrow[i].strip():
                    j += 1
                    passnum += 1
                else:
                    errs.write ("\tSatellites in row {} of result file not repeating properly.\n".format(comprownum))
                    errs.write ("\t\trow {}, satellite {} in result file should be{}, instead was {}.\n".format(comprownum,i-1,comprow[1+j],resrow[i]))
                    errors = True
                    break

            # If every value in log file was as expected, print a verify message
            if passnum >= len(resrow):
                errs.write ("\tRow {} of log file is correct!\n".format(comprownum))

        # Report error if there are more rows in the result file than the computed file
        try:
            resrow = resfile.next()
            errs.write ("More rows in result file than computed file.\n")
            errors = True
        except StopIteration:
            pass

        # Return if verified T/F
	return (not errors)

    ###########################################################################
    ### mapbunBaseline()
    ###   Set the terminal and Hub to a know working state with a FL locked
    ###
    ###########################################################################
    def mapbunBaseline(self, term=None):
        if not term:
            with algTerm("http://"+ str(self.termConf['ip']) + ":" +
                    str(self.termConf['port']), self.termConf['usern'],
                    self.termConf['passw'], self.mapDirConf['resultDir']) as term:
                term.algTermLogin()
                term.algTermRestore(baselineBin + '.' + self.termConf['consolePort'] + '.v'+ str(term.algGetVersion()))
        else:
            term.algTermLogin()
            term.algTermRestore(baselineBin + '.' + self.termConf['consolePort'] + '.v'+ str(term.algGetVersion()))

        timeBegin = time.time()

        with algEms("http://"+ str(self.nmsConf['ip']) + ":" +
                str(self.nmsConf['port']), self.nmsConf['usern'],
                self.nmsConf['passw'], self.mapDirConf['resultDir']) as ems:
            ems.algEmsLogin()
            ems.algEmsAcsmFlUpdate(self.mapConf['profile'], self.hubsConf['hub1Name'], hubConfig[self.termConf['consolePort']]['txFreq'], hubConfig[self.termConf['consolePort']]['rxFreq'], hubConfig[self.termConf['consolePort']]['chiprate'])
            ems.algEmsFlEnable(self.hubsConf['hub1Name'])
            ems.algEmsLogout()

        timeToSleep = 180 - (time.time() - timeBegin)
        if timeToSleep > 0:
            time.sleep(timeToSleep)

    ###########################################################################
    ### mapbunGetDwell()
    ###   Finds the number of satellites are available at the specified
    ###   coordinate and then adds one and multiplies it by the tuningConf
    ###   parameter specified for the precedenceDwell
    ###
    ###########################################################################

    def mapbunGetDwell(self, lat, lon):
        coordsId = open(self.mapDirConf['configDir'] + "coords_precid_v{}.csv".format(self.mapConf['bundleVersion']))
        coordsIdFile = csv.reader(coordsId)
        for row in coordsIdFile:
                if float(row[1].strip()) == lat and float(row[2].strip()) == lon:
                    sats = map(lambda x: x.strip(), row[3:])
                    break;

        return (len(sats) + 2) * self.tuningConf['precedenceDwell']

    ###########################################################################
    ### mapbunSedToSscf()
    ###   Maps the names from the sedFile passed in to the names of the sscf
    ###   file that is passed it. Returns a dictionary where the keys are the
    ###   sed names and the values are the sscf names.
    ###
    ###########################################################################
    def mapbunSedToSscf(self, sedFileName, sscfFileName):
        sedNames = {}
        sscfNames = {}
        with open(sedFileName, "r") as sed:
            for line in iter(sed.readline, ''):
                sedMap = re.match("([1-9]\d*),1,\d+,([^,]+),.*", line)
                if sedMap:
                        sedNames[sedMap.groups()[0]] = sedMap.groups()[1]

        with open(sscfFileName, "r") as sscf:
            for line in iter(sscf.readline, ''):
                sscfMap = re.match("([1-9]\d*),\d+,([^,]+),.*",line)
                if sscfMap:
                        sscfNames[sscfMap.groups()[0]] = sscfMap.groups()[1]

        beamDict = {}

        # Only match the names for beams in SSCF
        for key in sscfNames.keys():
            beamDict[sedNames[key]] = sscfNames[key]
        return beamDict


    ###########################################################################
    ### termStatusVerify(term)
    ###   
    ###   Input:
    ###     term - Term instance that is currently opened by with statement
    ###
    ###   Checks if the current versions of the sed, sscf, rlc, and gdrm versions
    ###   match the versions that are about to be uploaded. If they are the same,
    ###   no upload is needed.
    ###
    ###########################################################################
    def termStatusVerify(self, term=None):
        if not term:
            with algTerm("http://"+ str(self.termConf['ip']) + ":" + str(self.termConf['port']), self.termConf['usern'], self.termConf['passw'], self.mapDirConf['resultDir']) as term:
                termVerStatus = term.algTermStatusVersion()
        else:
            termVerStatus = term.algTermStatusVersion()
        
        if termVerStatus['sedVersion'] == self.termMapverConf['sedVersion'] and termVerStatus['sscfVersion'] == self.termMapverConf['sscfVersion']:
            if self.termMapverConf['rlcVersion'] and self.termMapverConf['gdrmVersion']:
                if termVerStatus['rlcVersion'] == self.termMapverConf['rlcVersion'] and termVerStatus['gdrmVersion'] == self.termMapverConf['gdrmVersion']:
                    status = True
                else:
                    status = False
            else:
                status = True
        else:
            status = False

        return status

    ###########################################################################
    ### mapbunTermLoFreq()
    ###   Inputs:
    ###       antenna, rfFreq (in MHz)
    ###   Returns:
    ###       the LO Freq in MHzX10 that term will used,
    ###        based on antenna & rffreq MHzX10
    ###
    ###########################################################################
    def mapbunTermLoFreq(self, antType, rfFreq):

        # Rantec
        if antType == '1' or antType ==2:
            #per An, there is a JIRA for low end to 116750 from 117000 
            if 116750 <= rfFreq < 122000:
                return 107500
            elif 122500 <= rfFreq < 127500:
                return 113000
            else:
                print("\nError: RF ({}) Out of range for this antenna ({})\n".format(rfFreq, antennaNamesDict[antType]))
                return 113000

        # VR12T
        # VR-12H
        elif antType == '3' or antType == '4':
            if 115500 <= rfFreq < 127500:
                return 106000
            else:
                print("\nError: RF ({}) Out of range for this antenna ({})\n".format(rfFreq, antennaNamesDict[antType]))
                return 106000

        # VR-12HS
        elif antType == '5':
            if 115500 <= rfFreq < 127500:
                return 105000
            else:
                print("\nError: RF ({}) Out of range for this antenna ({})\n".format(rfFreq, antennaNamesDict[antType]))
                return 105000

        # VR-12Ku-HP
        elif antType == '6':
            if 109500 <= rfFreq < 115500:
                return 100000
            elif 115500 <= rfFreq < 127500:
                return 106000
            else:
                print("\nError: RF ({}) Out of range for this antenna ({})\n".format(rfFreq, antennaNamesDict[antType]))
                return 106000

        # VR-12Ka
        # HMSA
        elif antType == '7' or antType == '10':
            if 195000 <= rfFreq < 202000:
                return 187500
            elif 202000 <= rfFreq < 212000:
                return 192500
            else:
                print("\nError: RF ({}) Out of range for this antenna ({})\n".format(rfFreq, antennaNamesDict[antType]))
                return 192500

        # KuKarray
        elif antType == '8':
            if 109500 <= rfFreq < 113000:
                return 100000
            if 113000 <= rfFreq < 115500:
                return 102000
            if 115500 <= rfFreq < 118500:
                return 105000
            if 118500 <= rfFreq < 121500:
                return 108000
            if 121500 <= rfFreq < 124000:
                return 111000
            if 124000 <= rfFreq < 127500:
                return 113000
            if 183000 <= rfFreq < 188000:
                return 180000
            if 188000 <= rfFreq < 193000:
                return 185000
            if 193000 <= rfFreq < 197000:
                return 189000
            if 197000 <= rfFreq < 202000:
                return 194000
            if 202000 <= rfFreq < 207000:
                return 199000
            if 207000 <= rfFreq < 212000:
                return 204000
            else:
                print("\nError: RF ({}) Out of range for this antenna ({})\n".format(rfFreq, antennaNamesDict[antType]))
                return 204000

        # KVH-V7
        # KVH-V3
        elif antType == '11' or antType == '12':
            #if 117000 <= rfFreq < 129000:
            if 116750 <= rfFreq < 129000:
                return 107500
            else:
                print("\nError: RF ({}) Out of range for this antenna ({})\n".format(rfFreq, antennaNamesDict[antType]))
                return 107500

        # KVH-V11
        elif antType == '13':
            if 117000 <= rfFreq < 129000:
                return 107500
            elif 36250 <= rfFreq < 42000:
                # Handle Spectral Inversion
                termLo = 51500
                absInvFreq = termLo - rfFreq 
                sigGen = absInvFreq + specInverLband
                lo = rfFreq - specInverLband
                print("\nWarning: Spectral Inversion Required-SigGen({})/InverFreq(-{})/RF({})/TermLO({})/LBand({})/TestLO({})\n".format(sigGen, absInvFreq, rfFreq, termLo, specInverLband, lo))
                print("Mixer Connections: EFLM to (R), Sig-Gen to (L), and Terminal to (I)\n")
                return lo
            else:
                print("\nError: RF ({}) Out of range for this antenna ({})\n".format(rfFreq, antennaNamesDict[antType]))
                return 107500

        # Tracstar
        # Raysat
        elif antType == '21' or antType == '31':
            if 107000 <= rfFreq < 129000:
                return 107500
            else:
                print("\nError: RF ({}) Out of range for this antenna ({})\n".format(rfFreq, antennaNamesDict[antType]))
                return 107500

        # TECOM KuStream 1500
        # TECOM KuStream 1015
        elif antType == '51' or antType == '52':
            if 107000 <= rfFreq < 117000:
                return 97500
            elif 11700 <= rfFreq < 127500:
                return 106000
            else:
                print("\nError: RF ({}) Out of range for this antenna ({})\n".format(rfFreq, antennaNamesDict[antType]))
                return 106000

    ###########################################################################
    ### mapbunTermMd5(term)
    ###   
    ###   Input:
    ###     logfn - log filename to capture results
    ###
    ###   Checks the MD5 checksum(s) on the terminal map files
    ###     if the terminal "needs to" because it supports unsigned files
    ###
    ###########################################################################
    def mapbunTermMd5(self, logfn):

        if termConfig[self.termConf['consolePort']]['logMD5']:
            logFile = open(self.mapDirConf['resultDir'] + logfn, 'a+')
            if self.SSH:
                tl = termLinkSSH(self.termConf['ip'], self.termConf['usern'], self.termConf['passw'], logFile)
                termCmd = TermCmdSSH(tl)
            else:
                tl = TerminalLink(self.termConf['port'], logFile)
                termCmd = TermCmd(tl)
                termCmd.login()

            Cmd(tl, "/test/md5sum4", termCmd.resp_shellPrompt).send()
            termCmd.tl.close()

if __name__ == '__main__':


    #x = mapbun(487)
    x = mapbun(488)
    #x = mapbun(493)
    x.mapbunPrecedenceVerify(x.mapDirConf['resultDir'] + "coords_precname_v{}.csv".format(x.mapConf['bundleVersion']), x.mapDirConf['resultDir'] + precVerifyLogFn, './results/' + precVerifyErrFn)
    
