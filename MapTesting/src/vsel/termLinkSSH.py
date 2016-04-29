import sys
import pxssh, pexpect
import time
import re
from TermSerialCom import getTimestamp




# Terminal Link for SSH
# Alternative connection to TerminalLink (Serial) from TermSerialCom
class termLinkSSH():

        def __init__(self, host, usern, passw, log):
            self.host = host
            self.usern = usern
            self.passw = passw
            self.log = log
            self.px = pxssh.pxssh()
            self.px.login(host, usern, passw, terminal_type='ansi')

            self.log.write('{} Connected to {}\n'.format(getTimestamp(), host))

        def sendCommand(self, cmd, resp, timeout):
            self.px.send(cmd)
            self.px.expect(resp, timeout = timeout)
            return self.px.before + self.px.after

        def prompt(self):
            self.px.prompt()

        def close(self):
            self.log.write('{} Closing connection'.format(getTimestamp()))
            self.log.close()
            self.px.close()

        def resetWaitingStatus(self):
            self.currentCmd = None

        def reLogin(self):
            self.px = pxssh.pxssh()
            self.px.login(self.host, self.usern, self.passw, terminal_type='ansi')
            self.log.write('{} Connected to {}\n'.format(getTimestamp(), self.host))

class Cmd:

    def __init__(self, tl, cmdString, response, timeout = 30, sleepTime = 0):
        self.tl = tl
        if cmdString != None:
            self.cmdString = cmdString + "\n"

        else:
            self.cmdString = ''

        self.response = response
        self.respBuf = ''
        self.timeout = timeout
        self.sleepTime = sleepTime
        self.txTime = None
        self.rxTime = None
        self.sent = False
        self.responseReceived = False
        self.responseResult = ''

    def send(self):

        try:
            self.txTime = time.time()
            self.responseResult  = self.tl.sendCommand(self.cmdString, self.response, self.timeout)
            self.rxTime = time.time()
            self.sent = True
            if self.sleepTime:
                time.sleep(self.sleepTime)
        except pexpect.TIMEOUT:
            self.timeoutExpired()
        except pexpect.EOF:
            if self.response == None:
                self.response = "No response string"
            self.tl.log.write("\r\n**Enf of file waiting for: " + self.response + "\r\n")
        self.tl.log.write(self.responseResult)
        return self.responseResult

    def reRespSearch(self, regexp):
        r = re.compile(regexp, re.MULTILINE)
        m = r.search(self.responseResult)
        if m:
            if r.groups > 0:
                return m.groups()
            else:
                return True
        else:
            return False


    def timeoutExpired(self):
        """Handle expiration of timeout.

        Logs the occurrence of the timeout, the command that was sent, and the expected response.
        Calls this Cmd's callback. The callback can determine that the response was not
        successfully received by checking the responseReceived flag.
        """
        if self.response == None:
            self.response = "No response string"

        if self.cmdString == '':
            self.tl.log.write("\r\n***Timeout waiting for: "+self.response+"\r\n")
        else:
            self.tl.log.write("\r\n***Timeout waiting for: "+self.response+" in response to command "+self.cmdString+"\r\n")
        self.tl.resetWaitingStatus()

class TermCmd(object):

    def __init__(self, tl):
        self.tl = tl

        self.wait_terminalLogin = 180
        self.wait_fileRxMsg = 300
        self.wait_mdlcFail = 60
        self.wait_rxIdleChange = 600
        self.wait_mdlcFlash = 800

        self.resp_shellPrompt = '# '
        self.resp_termcfgPrompt = 'Please enter menu item: '
        self.resp_terminalLogin = 'Terminal Logged In'
        self.resp_terminalLogout = 'Wait for Login Info'
        self.resp_txEnable = 'STATE CHANGE: [*]* TX Enable'
        self.resp_fileRxMsg = 'FT:0x40 CHANGE: Rxing File Data'
        self.resp_mdlcFail = 'segment out of order'
        self.resp_rxIdleChange = 'FT:0x40 CHANGE: IDLE'
        self.resp_mdlcFlash = 'FT:0x40 CHANGE: Writing File Data'
        self.resp_fileAnnounce = 'File Announce Msg - FT:0x40'

        self.TxrVersion = None
        self.FlrVersionStr = None
        self.flrApp = None          # name of program for controlling FLR

    def login(self):
        self.tl.reLogin()

    def checkVersions(self):
        result = self.termcfgVersion()
        # print(result.response)
        self.TxrVersion = result.reRespSearch('TXR Software Version:\s+(\S+)\s+')[0]
        self.FlrVersionStr = result.reRespSearch('FLR Versions.+\r\n((?:.+\r\n)+)')[0]
        # account for 'flrmsg' change to 'flrapp' in terminal version 3
        if self.TxrVersion[0] == 'r':
            self.flrApp = 'flrmsg'
        else:
            self.flrApp = 'flrapp'
        self.ctrlC()
        return self.TxrVersion, self.FlrVersionStr

    def checkTxrVersion(self):
        result = Cmd(self.tl, 'uname -v', '.*Version:.*\n.*# $').send()
        self.TxrVersion = result.reRespSearch('Version:\s+(\S+)\s+')[0]
        return self.TxrVersion

    def checkLoginStatus(self):
        result = self.termcfgStatus()
        return result.reRespSearch(self.resp_terminalLogin)

    def uploadFile(self, ftpAddress, filename, targetName=None):

        wgetCmd = "cd /test; wget ftp://" + ftpAddress + "/" + filename
        if (targetName):
            wgetCmd += "; mv " + filename + " " + targetName
        # send the command to upload the file
        Cmd(self.tl, wgetCmd, self.resp_shellPrompt, 400).send()

    def changeHubLogin(self, HubName, waveform):
        forwardLinkID = Hubnmae, waveform
        from ArclightTestFLParams import ForwardLink
        import time

        # error checking
        if not ForwardLink.has_key(forwardLinkID):
            print "The Forward link ID that you entered: ", forwardLinkID, "is not valid"
            return (False)
        else:
            #===================================================================
            # # do terminal version check can use self.TxrVersion if a checkVersion() is called before this function
            #===================================================================
            codeRates = ['1/4','1/3','2/5','1/2','3/5','2/3','3/4']
            rolloffFactors = ['0.2','0.25','0.35']
            scrambleOptions = ['off','on']
            #endToEndDelay = ['0','100','150','200','300','400','500']
            FECFrameSize = ['Normal','Short','Legacy']
            pilotPercentages = ['1','2','5','10']
            self.termcfg()
            #===================================================================
            # ensure that sat search and ACU server are off before this function
            #===================================================================

            # enter the satellite params menu
            Cmd(self.tl, '1', self.resp_termcfgPrompt).send()
            # turn off Sat search
            Cmd(self.tl, 'i', 'Search Value: ').send()
            Cmd(self.tl, '0', 'menu item: ').send()
            # return to main menu
            Cmd(self.tl, 'x', 'menu item: ').send()
            # enter the ACU params menu
            Cmd(self.tl, '2', self.resp_termcfgPrompt).send()
            # turn off ACU server
            Cmd(self.tl, 'v', 'ACU Type: ').send()
            Cmd(self.tl, '0', 'menu item: ').send()
            # return to main menu
            Cmd(self.tl, 'x', 'menu item: ').send()
            #===================================================================
            # change FL parameters
            #===================================================================
            # enter the FL params menu
            Cmd(self.tl, '3', self.resp_termcfgPrompt).send()
            Cmd(self.tl, '3', self.resp_termcfgPrompt).send()
            if self.TxrVersion[0] == 'r':
                #implies a 2.5 terminal.  2.5x terminals only support DSSS
                if waveform == 'ORCA':
                    # implies the user is trying to log a 2.5 terminal into an ORCA link
                    # which is not supported.  Default behavior will be to through a warning and
                    # log the terminal into the DSSS link for that hub.
                    print "ORCA is not supported on r252 terminals.  Your terminal will be logged in to the DSSS waveform on your chosen hub of:", HubName
                    forwardLinkID = HubName, 'DSSS'
                    time.sleep(2)
                # set FL freq
                Cmd(self.tl, 'm', 'L-Band Value \(Hz\):').send()
                Cmd(self.tl, ForwardLink[forwardLinkID]['Frequency'], 'menu item: ').send()
                # set data rate
                Cmd(self.tl, 'b', 'Data Rate \(bps\):').send()
                Cmd(self.tl, ForwardLink[forwardLinkID]['Data Rate'], 'menu item: ').send()
                # set spread factor
                Cmd(self.tl, 'd', 'Spread Factor: ').send()
                Cmd(self.tl, ForwardLink[forwardLinkID]['Spread Factor'], 'menu item: ').send()
                # set PN Tap
                Cmd(self.tl, 'e', 'PN Tap \(hex\):').send()
                Cmd(self.tl, ForwardLink[forwardLinkID]['PN Tap'], 'menu item: ').send()
                # set PN Seed
                Cmd(self.tl, 'f', 'PN Seed \(hex\):').send()
                Cmd(self.tl, ForwardLink[forwardLinkID]['PN Seed'], 'menu item: ').send()
                # set Trunc. count
                Cmd(self.tl, 'h', 'Truncation Count:').send()
                Cmd(self.tl, ForwardLink[forwardLinkID]['Truncation Count'], 'menu item: ').send()
            elif self.TxrVersion[0] == '3' and self.TxrVersion[1] < '5':
                #implies a terminal older than 3.5 only supporting DSSS and ORCA, but not VCSM
                if waveform == 'VCSM':
                    print "VCSM is not supported on terminals older than 3.5.  Your terminal will be logged into the DSSS waveform on your chosen hub of:", HubName
                    forwardLinkID = HubName, 'DSSS'
                    time.sleep(2)
				#select common FL parameters
                Cmd(self.tl, 'b', 'menu item: ').send()
                # set FL freq
                Cmd(self.tl, 'c', 'L-Band Value \(Hz\):').send()
                Cmd(self.tl, ForwardLink[forwardLinkID]['Frequency'], 'menu item: ').send()
                # exit the common FL params menu
                Cmd(self.tl, 'x', 'menu item: ').send()
                # enter the waveform type menu
                Cmd(self.tl, 'a', 'Waveform Type: ').send()
                # select the desired waveform for now, choose DSSS

                if waveform == 'ORCA':
                    # choose ORCA waveform
                    Cmd(self.tl, '1', 'menu item: ').send()
                    # open the ORCA waveform menu
                    Cmd(self.tl, 'd', 'menu item: ').send()
                    # set the symbol rate
                    Cmd(self.tl, 'a', 'Symbol Rate \(ksps\):').send()
                    Cmd(self.tl, ForwardLink[forwardLinkID]['Symbol Rate'], 'menu item: ').send()
                    # set code rate
                    Cmd(self.tl, 'd', 'Code Rate Value:').send()
                    # WARNING!  using the index of the codeRates list that was generated at the
                    # top of this function to interact with termcfg is valid with the structure
                    # of the termcfg menu structure as of 5/10/2010.  If this line produces errors
                    # there is probably a mismatch between the codeRates table and the termcfg menu
                    Cmd(self.tl, str(codeRates.index(ForwardLink[forwardLinkID]['Code Rate'])), 'menu item: ').send()
                    # set end to end delay
                    Cmd(self.tl, 'j', 'End Delay \(msecs\): ').send()
                    Cmd(self.tl, ForwardLink[forwardLinkID]['End to End Delay'], 'menu item: ').send()
                    # exit current waveform params menu
                    Cmd(self.tl, 'x', 'menu item: ').send()
                else:
                    # choose DSSS waveform
                    Cmd(self.tl, '0', 'menu item: ').send()
                    # enter the DSSS params menu
                    Cmd(self.tl, 'c', 'menu item: ').send()
                    # set data rate
                    Cmd(self.tl, 'a', 'Data Rate \(bps\):').send()
                    Cmd(self.tl, ForwardLink[forwardLinkID]['Data Rate'], 'menu item: ').send()
                    # set spread factor
                    Cmd(self.tl, 'c', 'Spread Factor: ').send()
                    Cmd(self.tl, ForwardLink[forwardLinkID]['Spread Factor'], 'menu item: ').send()
                    # set PN Tap
                    Cmd(self.tl, 'd', 'PN Tap \(hex\):').send()
                    Cmd(self.tl, ForwardLink[forwardLinkID]['PN Tap'], 'menu item: ').send()
                    # set PN Seed
                    Cmd(self.tl, 'e', 'PN Seed \(hex\):').send()
                    Cmd(self.tl, ForwardLink[forwardLinkID]['PN Seed'], 'menu item: ').send()
                    # set Trunc. count
                    Cmd(self.tl, 'g', 'Truncation Count:').send()
                    Cmd(self.tl, ForwardLink[forwardLinkID]['Truncation Count'], 'menu item: ').send()
                    # exit current waveform params menu
                    Cmd(self.tl, 'x', 'menu item: ').send()

            else:
			##implies a terminal newer than 3.5 supporting DSSS, ORCA and VCSM
			#select common FL parameters
                Cmd(self.tl, 'b', 'menu item: ').send()
                # set FL freq
                Cmd(self.tl, 'c', 'L-Band Value \(Hz\):').send()
                Cmd(self.tl, ForwardLink[forwardLinkID]['Frequency'], 'menu item: ').send()
                # exit the common FL params menu
                Cmd(self.tl, 'x', 'menu item: ').send()
                # enter the waveform type menu
                Cmd(self.tl, 'a', 'Waveform Type: ').send()
                # select the desired waveform for now, choose DSSS
                if waveform == 'DSSS':
                    # choose DSSS waveform
                    Cmd(self.tl, '0', 'menu item: ').send()
                    # enter the DSSS params menu
                    Cmd(self.tl, 'c', 'menu item: ').send()
                    # set data rate
                    Cmd(self.tl, 'a', 'Data Rate \(bps\):').send()
                    Cmd(self.tl, ForwardLink[forwardLinkID]['Data Rate'], 'menu item: ').send()
                    # set spread factor
                    Cmd(self.tl, 'c', 'Spread Factor: ').send()
                    Cmd(self.tl, ForwardLink[forwardLinkID]['Spread Factor'], 'menu item: ').send()
                    # set PN Tap
                    Cmd(self.tl, 'd', 'PN Tap \(hex\):').send()
                    Cmd(self.tl, ForwardLink[forwardLinkID]['PN Tap'], 'menu item: ').send()
                    # set PN Seed
                    Cmd(self.tl, 'e', 'PN Seed \(hex\):').send()
                    Cmd(self.tl, ForwardLink[forwardLinkID]['PN Seed'], 'menu item: ').send()
                    # set Trunc. count
                    Cmd(self.tl, 'g', 'Truncation Count:').send()
                    Cmd(self.tl, ForwardLink[forwardLinkID]['Truncation Count'], 'menu item: ').send()
                    # exit current waveform params menu
                    Cmd(self.tl, 'x', 'menu item: ').send()
                elif waveform == 'ORCA':
                    # choose ORCA waveform
                    Cmd(self.tl, '1', 'menu item: ').send()
                    # open the ORCA waveform menu
                    Cmd(self.tl, 'd', 'menu item: ').send()
                    # set the symbol rate
                    Cmd(self.tl, 'a', 'Symbol Rate \(ksps\):').send()
                    Cmd(self.tl, ForwardLink[forwardLinkID]['Symbol Rate'], 'menu item: ').send()
                    # set code rate
                    Cmd(self.tl, 'd', 'Code Rate Value:').send()
                    # WARNING!  using the index of the codeRates list that was generated at the
                    # top of this function to interact with termcfg is valid with the structure
                    # of the termcfg menu structure as of 5/10/2010.  If this line produces errors
                    # there is probably a mismatch between the codeRates table and the termcfg menu
                    Cmd(self.tl, str(codeRates.index(ForwardLink[forwardLinkID]['Code Rate'])), 'menu item: ').send()
                    # set end to end delay
                    Cmd(self.tl, 'j', 'End Delay \(msecs\): ').send()
                    Cmd(self.tl, ForwardLink[forwardLinkID]['End to End Delay'], 'menu item: ').send()
                    # exit current waveform params menu
                    Cmd(self.tl, 'x', 'menu item: ').send()

                elif waveform == 'VCSM':
                    # choose VCSM waveform
                    Cmd(self.tl, '2', 'menu item: ').send()
                    # enter the DSSS params menu
                    Cmd(self.tl, 'e', 'menu item: ').send()
                    # set the symbol rate
                    Cmd(self.tl, 'a', 'Symbol Rate \(ksps\):').send()
                    Cmd(self.tl, ForwardLink[forwardLinkID]['Symbol Rate'], 'menu item: ').send()
                    # set the SRRC Roll-Off Factor
                    Cmd(self.tl, 'b', 'Roll-Off Factor Value:').send()
					# WARNING!  using the index of the Roll-off factors list that was generated at the
                    # top of this function to interact with termcfg is valid with the structure
                    # of the termcfg menu structure as of 1/13/2012.  If this line produces errors
                    # there is probably a mismatch between the codeRates table and the termcfg menu
                    Cmd(self.tl, str(rolloffFactors.index(ForwardLink[forwardLinkID]['SRRC Roll-off Factor'])), 'menu item: ').send()
					# set the Unique Word TCW
                    Cmd(self.tl, 'c', 'Unique Word TCW \(hex\):').send()
                    Cmd(self.tl, ForwardLink[forwardLinkID]['Unique Word TCW'], 'menu item: ').send()
                    # set the Unique Word ICW
                    Cmd(self.tl, 'd', 'Unique Word ICW \(hex\):').send()
                    Cmd(self.tl, ForwardLink[forwardLinkID]['Unique Word ICW'], 'menu item: ').send()
                    # set the Unique Pilot Overlay Seq TCW
                    Cmd(self.tl, 'e', 'Unique Pilot Overlay Sequence TCW \(hex\):').send()
                    Cmd(self.tl, ForwardLink[forwardLinkID]['Unique Pilot Overlay Seq TCW'], 'menu item: ').send()
                    # set the Unique Pilot Overlay Seq ICW
                    Cmd(self.tl, 'f', 'Unique Pilot Overlay Sequence ICW \(hex\):').send()
                    Cmd(self.tl, ForwardLink[forwardLinkID]['Unique Pilot Overlay Seq ICW'], 'menu item: ').send()
                    # set Scramble
                    Cmd(self.tl, 'g', 'Forward Link Scramble Control:').send()
					# WARNING!  using the index of the Scramble list that was generated at the
                    # top of this function to interact with termcfg is valid with the structure
                    # of the termcfg menu structure as of 1/13/2012.  If this line produces errors
                    # there is probably a mismatch between the Scramble table and the termcfg menu
                    Cmd(self.tl, str(scrambleOptions.index(ForwardLink[forwardLinkID]['Scramble'])), 'menu item: ').send()
                    # set End To End Delay
                    Cmd(self.tl, 'h', 'End To End Delay Options \(msecs\):').send()
					# WARNING!  using the index of the End To End Delay Options list that was generated at the
                    # top of this function to interact with termcfg is valid with the structure
                    # of the termcfg menu structure as of 1/13/2012.  If this line produces errors
                    # there is probably a mismatch between the End To End Delay table and the termcfg menu
                    Cmd(self.tl, ForwardLink[forwardLinkID]['End to End Delay'], 'menu item: ').send()
                    # set FEC Frame Size
                    Cmd(self.tl, 'i', 'FEC Frame Size Options:').send()
			        # WARNING!  using the index of the FEC Frame Size Options list that was generated at the
                    # top of this function to interact with termcfg is valid with the structure
                    # of the termcfg menu structure as of 1/13/2012.  If this line produces errors
                    # there is probably a mismatch between the FEC Frame Size table and the termcfg menu
                    Cmd(self.tl, str(FECFrameSize.index(ForwardLink[forwardLinkID]['FEC Frame Size'])), 'menu item: ').send()
			        # set Pilot Percentage
                    Cmd(self.tl, 'j', 'Pilot Percentage Options:').send()
					# WARNING!  using the index of the Pilot percentages list that was generated at the
                    # top of this function to interact with termcfg is valid with the structure
                    # of the termcfg menu structure as of 1/13/2012.  If this line produces errors
                    # there is probably a mismatch between the pilotPercentage table and the termcfg menu
                    Cmd(self.tl, str(pilotPercentages.index(ForwardLink[forwardLinkID]['Pilot Percentage'])), 'menu item: ').send()
					# set the Spread TCW
                    Cmd(self.tl, 'k', 'Spread TCW \(hex\):').send()
                    Cmd(self.tl, ForwardLink[forwardLinkID]['Spread TCW'], 'menu item: ').send()
                    # set the Spread ICW
                    Cmd(self.tl, 'l', 'Spread ICW \(hex\):').send()
                    Cmd(self.tl, ForwardLink[forwardLinkID]['Spread ICW'], 'menu item: ').send()
                    # exit current waveform params menu
                    Cmd(self.tl, 'x', 'menu item: ').send()

        # exit FL params menu
        Cmd(self.tl, 'x', 'menu item: ').send()
        # exit termcfg
        Cmd(self.tl, 'x', '\(y/n\)\?').send()
        # save values
        Cmd(self.tl, 'y', '\(y/n\)\?').send()
        # do not reboot here
        Cmd(self.tl, 'n', '').send()
        # reboot here
        #self.resetAcu()
        self.reboot()
        self.login()
        self.waitLogin()
        print "\r\n****Terminal logged into ",forwardLinkID,"****\r\n"
        return True

    def setLatLong(self, lat, lon):
        """Set the fixed latitude and longitude of the terminal image and enable sat search
        lat - latitude of the VMT
        lon - longitude of the VMT
        """
        self.termcfg()
        # enter ACU menu
        Cmd(self.tl, '2', self.resp_termcfgPrompt).send()
        # select the Fixed Latitude
        Cmd(self.tl, 't', 'x.xx\):').send()
        Cmd(self.tl, "{}".format(lat), 'menu item: ').send()
        # select the Fixed Longitude
        Cmd(self.tl, 'u', 'x.xx\):').send()
        Cmd(self.tl, "{}".format(lon), 'menu item: ').send()
        # exit the ACU menu
        Cmd(self.tl, 'x', 'menu item: ').send()
        # enter the Satellite menu
        Cmd(self.tl, '1', self.resp_termcfgPrompt).send()
        # select the Satellite Search Setting
        Cmd(self.tl, 'i', 'Search Value:').send()
        # set Satellite Search to "on"
        Cmd(self.tl, '1', 'menu item: ').send()
        # exit the Satellite menu
        Cmd(self.tl, 'x', 'menu item: ').send()
        # exit termcfg
        Cmd(self.tl, 'x', '\(y/n\)\?').send()
        # save the settings
        Cmd(self.tl, 'y', '\(y/n\)\?').send()
        # don't reboot the VMT
        Cmd(self.tl, 'n', self.resp_shellPrompt).send()
        return True

    def changeTxrVersion(self, ftpAddress, imageFileName, versionName, postFlashCmd=None):
        self.termcfg()
        Cmd(self.tl, 'U', self.resp_termcfgPrompt).send()
        Cmd(self.tl, 'A', 'IP address').send()
        Cmd(self.tl, ftpAddress, 'Filename: ').send()
        result = Cmd(self.tl, imageFileName, 'menu item: ', 60).send()
        if result.responseReceived:
            # download succeeded, initiate flashing
            Cmd(self.tl, 'B', 'Image update Successful', 1800).send()
            result = Cmd(self.tl, None, 'menu item: ', 1800).send()
            if result.responseReceived:
                # flashing succeeded
                Cmd(self.tl, 'x', 'menu item: ').send()
                Cmd(self.tl, 'x', '\(y/n\)\?').send()
                Cmd(self.tl, 'y', '\(y/n\)\?').send()
                Cmd(self.tl, 'n', 'termcfg ended').send()
                # execute a command post flash
                if postFlashCmd:
                    Cmd(self.tl, postFlashCmd, self.resp_shellPrompt, 400).send()
                self.resetAcu()
                self.reboot()
                self.waitLogin()
                self.login()
                loadedImage = self.checkTxrVersion()
                if loadedImage == versionName:
                    return True
            else:
                # flashing failed
                self.ctrlC()
        else:
            # download failed
            self.ctrlC()
        return False

    def renameFile(self, source, destination):
        """Rename a file on the terminal.

        Copies the file to its destination, checks for its existence, and deletes the old file
        if the copy was successful.
        """
        if source == destination:
            print 'Rename Error: source and destination files are the same'
            return False
        if (self.verifyFile(source)):
            # copy file
            Cmd(self.tl, 'cp '+source+' '+destination, self.resp_shellPrompt).send()
            # verify copy exists
            if (self.verifyFile(destination)):
                # delete old file
                Cmd(self.tl, 'rm '+source, self.resp_shellPrompt).send()
                return True
            else:
                print 'Rename Error: destination file "'+destination+'" was not created'
        else:
            print 'Rename Error: source file "'+source+'" does not exist'
        return False

    def rmFile(self, target):
        """Remove the target file."""
        # delete old file
        Cmd(self.tl, 'rm '+target, self.resp_shellPrompt).send()
        return True


    def verifyFile(self, filename):
        """Verify the existance of a file on the terminal.

        returns True if file exists, False if not
        """
        tree = filename.split('/')
        (path, filename) = ('/'.join(tree[:-1]),tree[-1])
        result = Cmd(self.tl, 'ls '+path, self.resp_shellPrompt).send()
        if result.reRespSearch(re.escape(filename)):
            return True
        else:
            return False


    def getRLDataRate(self):
        """Get the return link data rate."""
        result = self.termcfgStatus()
        val = result.reRespSearch('Ret Data Rate\s+(\S+)')
        if isinstance(val, bool):
            return (val)
        else:
            return int(val[0])


    def getAttenuator(self):
        """Get the return link attenuator."""
        result = self.termcfgStatus()
        val = result.reRespSearch('Attenuator\s+(\S+)')
        if isinstance(val, bool):
            return val
        else:
            return float(val[0])

    def ctrlC(self):
        return Cmd(self.tl, chr(3), '#', 10).send()

    def ctrlD(self):
        return Cmd(self.tl, chr(4), 'console. ', 3).send()

    def termcfg(self):
        result = Cmd(self.tl, 'termcfg', self.resp_termcfgPrompt).send()
        return result

    def termcfgStatus(self):
        self.termcfg()
        result = termcfgStatus().send()
        self.ctrlC()
        return result

    def termcfgVersion(self):
        self.termcfg()
        result = Cmd(self.tl, 'v', self.resp_termcfgPrompt).send()
        self.ctrlC()
        return result

    def termcfgStatus(self):
        """Get text of termcfg status menu."""
        self.termcfg()
        result = Cmd(self.tl, 's', self.resp_termcfgPrompt).send()
        self.ctrlC()
        return result


    def termcfgRLConfig(self):
        self.termcfg()
        result = Cmd(self.tl, '4', self.resp_termcfgPrompt).send()
        self.ctrlC()
        return result


    def getAttenLimit(self):
        """Get the return link attenuator limit."""
        result = self.termcfgRLConfig()
        val = result.reRespSearch('Power Limit\s+(\S+)')
        if isinstance(val, bool):
            return val
        else:
            defer.returnValure(float(val[0]))

    def showDate(self):
        """Show current date and time on terminal."""
        return Cmd(self.tl, 'date', self.resp_shellPrompt, 5).send()

    def reboot(self):
        """Reboot the terminal and wait for it to log in to hub."""
        result = Cmd(self.tl, 'reboot', None, self.wait_terminalLogin).send()
        time.sleep(self.wait_terminalLogin)
        return result

    def reboot_error(self):
        """Reboot the terminal and wait for it to error due to FLR Mesage Timeout."""
        return Cmd(self.tl, 'reboot', 'FLR Message Timeout', 150).send()

    def catMdlcini(self):
        """Cat MDLC database ini"""
        return Cmd(self.tl, 'cat /etc/mdlc.ini', self.resp_shellPrompt, 5).send()

    def removeMdlcDatabase(self):
        """Remove MDLC database.

        Induces MDLP to download and flash a new terminal image.
        """
        return Cmd(self.tl, 'rm /etc/mdlc.ini', self.resp_shellPrompt, 5).send()

    def resetAcu(self):
        """Reset Antenna Control Unit."""
        return Cmd(self.tl, 'acumsg -r', self.resp_shellPrompt, 5).send()


    def activateDemodulator(self):
        """Activate demodulator.

        Useful for causing the terminal to log in after being logged out by idling the demodulator.
        """
        self.showDate()
        result = Cmd(self.tl, self.flrApp+' -da', self.resp_shellPrompt).send()
        return result


    def idleDemodulator(self):
        """Idle the demodulator.

        Causes terminal to log out.
        """
        self.showDate()
        result = Cmd(self.tl, self.flrApp+' -di', self.resp_terminalLogout).send()
        return result


    def waitTxEnable(self):
        """Wait for terminal transmitter enable."""
        self.showDate()
        result = Cmd(self.tl, None, self.resp_txEnable, 60).send()
        self.showDate()
        return result

    def waitLogin(self):
        """Wait for terminal to log in to hub."""
        return Cmd(self.tl, None, self.resp_terminalLogin, self.wait_terminalLogin).send()


    def checkFileRxInit(self):
        """Wait for terminal to begin receiving image over MDLP.

        returns True if transfer started within timeout, False if not
        """
        result = Cmd(self.tl, None, self.resp_fileRxMsg, self.wait_fileRxMsg).send()
        return result.responseReceived


    def checkFileRxFail(self):
        """Wait for MDLP failure message.

        returns True if failure message received, False if not
        """
        result = Cmd(self.tl, None, self.resp_mdlcFail, self.wait_mdlcFail).send()
        return result.responseReceived


    def checkFileRxReschedule(self):
        """Wait for MDLP image transfer to be rescheduled."""
        result = Cmd(self.tl, None, self.resp_fileAnnounce, self.wait_rxIdleChange).send()
        return result.responseReceived


    def waitFlashBegin(self):
        """Wait for terminal to begin flashing new image."""
        result = Cmd(self.tl, None, self.resp_mdlcFlash, self.wait_rxIdleChange).send()
        return result.responseReceived


    def waitFlashComplete(self, postFlashCmd=None):
        """Wait for terminal to complete flashing new image."""
        result = Cmd(self.tl, None, self.resp_rxIdleChange, self.wait_mdlcFlash).send()
        # execute a command post flash
        if postFlashCmd:
            Cmd(self.tl, postFlashCmd, self.resp_shellPrompt, 400).send()
        return result.responseReceived

    def dynamicFunctionCaller(self, inp):
        """Calls other functions from this class.

        Must be given a string containing the function call as it would be
        written in Python, but without the 'self.' prefix.
        """
        try:
            exec('self.'+inp)
        except:
            sys.stdout.write(inp, ' failed to execute')


    def grepLog(self, target):
        """grep syslogMsgs with a target phrase"""
        Cmd(self.tl, 'grep "'+target+'" /test/syslogMsgs', self.resp_shellPrompt).send()

        return True

    def execCmd(self,cmd,timeout=5):
        """Execute an arbitrary command"""
        return Cmd(self.tl, cmd, self.resp_shellPrompt, timeout).send()


    def wait_Idle40(self):
	Cmd(self.tl,'',"FT:0x40 CHANGE: IDLE",1200).send()


    def termCfgStatusInit(self):
        self.termcfg()
        Cmd(self.tl,'s', self.resp_termcfgPrompt).send()


    def refreshStatus(self):
        result = Cmd(self.tl, '', self.resp_termcfgPrompt).send()
        return result


    def refreshAttenuator(self):
        status = self.refreshStatus()
        val = status.reRespSearch('Attenuator\s+(\S+)')
        if isinstance(val, bool):
            return val
        else:
            return float(val[0])

    def getEth0Availibility(self):
        return Cmd(self.tl, 'ifconfig', 'eth0', 10).send()

    def getEth0Speed(self, speed):
        return Cmd(self.tl, 'ethtool eth0', "Speed: " + speed + "Mb/s", 10).send()

    def getEth0Duplex(self, duplex):
        return Cmd(self.tl, 'ethtool eth0', "Duplex: " + duplex, 10).send()


    def waitCmd(self, time):
        Cmd(self.tl, '', 'NeverMatchThisPhrase', time).send()
        return True

    def getEth0Ping(self, ipPing):
        return Cmd(self.tl, 'ping ' + ipPing, "64 bytes from " + ipPing, 10).send()

    def waitConsoleTerm(self):
        """Reboot the terminal and wait for it to finish its boot process"""
        return Cmd(self.tl, '', 'Please press Enter to activate this console', self.wait_terminalLogin).send()

    def setAntenna(self, antennaType):
        """Set the Antenna Type of the terminal image
        antennaType - id of antenna, e.g. 7 ViaSat VR12 Ka-Band Antenna
        """
        self.termcfg()
        # enter General Parameters menu
        Cmd(self.tl, '0', self.resp_termcfgPrompt).send()
        # select the Antenna Type menu
        Cmd(self.tl, 'I', 'Antenna Type:').send()
        Cmd(self.tl, "{}".format(antennaType), 'Hit Return to continue').send()
        Cmd(self.tl, "", 'menu item: ').send()
        # exit the Antenna menu
        Cmd(self.tl, 'x', 'menu item: ').send()
        # exit termcfg
        Cmd(self.tl, 'x', '\(y/n\)\?').send()
        # save the settings
        Cmd(self.tl, 'y', '\(y/n\)\?').send()
        # don't reboot the VMT
        Cmd(self.tl, 'n', self.resp_shellPrompt).send()
        return True
