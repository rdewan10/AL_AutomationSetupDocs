###########################################################################################
###########################################################################################
### algElements Class
###   Derived from ViaSat Selenium Class
###   Class of general methods used for two or more other classes (NMS, EMS, or Terminal)
###   See //Arclight/ArcLight/AcceptanceTest/Automation/MapTesting/Docs/AL_Automation_SDD.docx
###
###########################################################################################
###########################################################################################

from alDefaults import *
from vselMain import *
import re, ast

class algElements(vselenium):
    def __init__(self, resultsDir, pause, brow="chrome"):
        vselenium.__init__(self, brow, resultsDir, pause)
        #vselenium.__init__(self, "firefox", resultsDir, pause)
        self.resultsDir = resultsDir
        self.pause = pause
        # Extension of screenshot filename (ex. ".png" or ".jpg")
        self.ssext = ".png"
        self.algSetVersion()

    ####################################################################################
    ### algLogin()
    ###
    ###   Logs in differently based on defined type 
    ###   (type is defined in initialization of other classes)
    ###
    ####################################################################################
    def algLogin(self):
        self.connectToServer(self.url)
        if self.type == "ems":
            # Clicks EMS radio button
            self.clickElement("xpath=//span[text()='EMS']")
        elif self.type == "term":
            # Clicks on "Configuration" tab
            self.clickElement("xpath=//img[@alt='Configuration']")
            try:
                WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.ID, "txtUser")), "Couldn't find element")
            except:
                self.connectToServer(self.url)
                self.clickElement("xpath=//img[@alt='Configuration']")
                WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.ID, "txtUser")), "Couldn't find element")

        # Fills in username, password, and clicks login button
        time.sleep(1)
        self.setTextField("xpath=//input[@type='text']",self.usern)
        self.setTextField("xpath=//input[@type='password']",self.passw)
        self.clickElement("xpath=//input[@value='Login']")

    ####################################################################################
    ### algLogout()
    ###
    ###   Logs out (only used for NMS and EMS)
    ###   Note that tearDown() still needs to be called afterward.
    ###
    ####################################################################################
    def algLogout(self):
        self.selectMenuOption("class=tabSettingsLink", "link=Logout")

    ####################################################################################
    ### _algSelectTableRow(COLUMN_NUM, "TARGET", "xpath")
    ###
    ###   Inputs:
    ###     COLUMN_NUM - Column number (checkbox column is column 0)
    ###     TARGET - string to be searched for in column COLUMN_NUM
    ###     xpath - xpath that identifies where the target is located
    ###   Sample call (searching for profile 3 in ID column (1st column)): 
    ###     see call in algSelectTableRow
    ###   Traverses rows in table starting from top. 
    ###     Searches for TARGET in column COLUMN_NUM of each row.
    ###   If TARGET is found, the checkbox of the corresponding row is clicked. 
    ###   If TARGET is in more than
    ###     one row, the row that contains the earliest occurrence of TARGET is clicked.
    ###
    ###   Note that the checkboxes are in column 0. If a row is already selected prior to
    ###     calling algSelectTableRow, it will be deselected if TARGET is in that row.
    ###
    ####################################################################################
    def _algSelectTableRow(self, COLUMN_NUM, TARGET, xpath):
        row = 1
        for i in self.findElementsByLocator("xpath=" + xpath):
            if i.text == TARGET:
                if self.version < RELEASE_NMS_42:
                   self.clickElement("xpath=//div[@class='x-grid-row-checker']/../../../..//tr[" + str(row) + "]/td[@cellindex='0']/div/div")
                else:
                   self.clickElement("xpath=//*[@id='gwtDiv']/div/div/div/div[5]/div[2]/div[1]/table/tbody[2]/tr/td[1]/div/div")
                break
            row += 1

    ####################################################################################
    ### algSelectTableRow(COLUMN_NUM, "TARGET")
    ###
    ###   Inputs:
    ###     COLUMN_NUM - Column number (checkbox column is column 0)
    ###     TARGET - string to be searched for in column COLUMN_NUM
    ###       Sample call (searching for profile 3 in ID column (1st column)): algSelectTableRow(1, "3")
    ###
    ###   Calls _algSelectTableRow() to maintain backward compatibility.
    ###      Note: Use algSelectVMT() to select rows in the VMT table.
    ###
    ####################################################################################
    def algSelectTableRow(self, COLUMN_NUM, TARGET):
        self._algSelectTableRow(COLUMN_NUM, TARGET, "//*[@id='gwtDiv']//table/tbody[2]//td[@cellindex='" + str(COLUMN_NUM) + "']")

    ####################################################################################
    ### algSelectVMT(COLUMN_NUM, "TARGET")
    ###
    ###   Inputs:
    ###     COLUMN_NUM - Column number (checkbox column is column 0)
    ###     TARGET - string to be searched for in column COLUMN_NUM
    ###
    ###   Traverses rows in table starting from top. Searches for TARGET in column COLUMN_NUM of each row.
    ###   If TARGET is found, the checkbox of the corresponding row is clicked. If TARGET is in more than
    ###     one row, the row that contains the earliest occurrence of TARGET is clicked.
    ###   Note that the checkboxes are in column 0. Also note that if a row is already selected prior to
    ###     calling algSelectTableRow, it will be deselected if TARGET is in that row.
    ###
    ####################################################################################
    def algSelectVMT(self, COLUMN_NUM, TARGET):
        self._algSelectTableRow(COLUMN_NUM, TARGET, "//*[@id='gwtDiv']/div/div/div/div[3]/div[2]/div[3]/div/div[3]/div[1]/div[2]/div[3]/div[1]/table/tbody[2]//td[@cellindex='" + str(COLUMN_NUM) + "']")

    ####################################################################################
    ### algScreenShot("filename")
    ###
    ###   Input:
    ###     filename - name of screenshot file (without extension)
    ###       Sample call: algScreenShot("myfile")
    ###
    ###   Takes screenshot of current page and saves it with path self.resultsDir and
    ###     filename [filename + self.ssext] where self.ssext is the extension
    ###       Ex. /tmp + myfile + .jpg = /tmp/myfile.jpg
    ###
    ####################################################################################
    def algScreenShot(self, filename):
        self.saveScreenshot(self.resultsDir + "/" + filename + self.ssext)

    ####################################################################################
    ### algClickMenuTab("TAB")
    ###
    ###   Input:
    ###     TAB - link name of tab
    ###       Sample element that works:
    ###         <a href= ... >
    ###           <span class="txt15Reg">"SDL Management"</span>
    ###       Corresponding call: algClickMenuTab("SDL Management")
    ###
    ###   Clicks on tab along top of screen with text "TAB"
    ###   Note: Only works for NMS and EMS
    ####################################################################################
    def algClickMenuTab(self, TAB):
        self.clickElement("link=" + TAB)

    ####################################################################################
    ### algClickSubMenuLink("LINK")
    ###
    ###   Input:
    ###     LINK - link name of submenu tab/hyperlink
    ###       Sample element that works for NMS/EMS: <div ... title="Forward Links">
    ###      Sample element that works for Terminal: <a href= ... >Forward Links</a>
    ###       Corresponding call (for either): algClickSubMenuLink("Forward Links")
    ###
    ###   Clicks on clickable submenu tab/hyperlink on left-hand side of screen with text "LINK"
    ###   Note: Terminal sidebar uses hyperlink text whereas NMS and EMS sidebars use tabs
    ####################################################################################
    def algClickSubMenuLink(self, LINK):
        if self.type == "term":
            self.clickElement("link=" + LINK)
        else:
            self.clickElement("xpath=//div[@title='" + LINK + "']")

    ############################################################################
    ### algStatusBasic1()
    ###   Input:
    ###      delim - delimiter string between tag/value
    ###
    ###   ALG Status, Basic Algorithm 1
    ###   Grabs every tag/value string displayed that contains specified 
    ###   delimiter, e.g. ": " and puts it in a dictionary.
    ###   Strips special characters from keys for easy conversion into SQL table
    ###
    ############################################################################
    def algStatusBasic1(self, delim=': '):

        elements = self.findElementsByLocator("xpath=//div[@style='display: inline;'][contains(text(),'"+ delim + "')]")

        # use get_attribute() instead of .text - DOM/Python-XML parser bug?
        basicDict = dict((element.get_attribute("innerHTML").split(delim, 1) for element in elements))

        # Strips out spaces, parentheses, and slashes from keys
        basicDict = {key.replace(' ','').replace('(','').replace(')','').replace('/',''): item for key, item in basicDict.items()}

        return basicDict


    ############################################################################
    ### algStatusBasic2()
    ###   Input:
    ###      delim - delimiter string between tag/value
    ###      tagname - Name of field (minus delimiter which is added back)
    ###      valpath - relative path from key where the value element is
    ###
    ###   ALG Status, Basic Algorithm 2
    ###   Locates key based on <tagname>+<delim> 
    ###   Makes <tagname> only the key of dictionary returned
    ###   Gets value from valpath, relative to tag location
    ###   Returms Tag/Value dictionary
    ###
    ############################################################################
    def algStatusBasic2(self, tagname, delim=':', valpath="/../../td[2]/div"):

        key = self.findElementByLocator("xpath=//div[text()='" + tagname + delim + "']")
        value = self.findElementByLocator("xpath=//div[text()='" + tagname + delim + "']"+ valpath)

        dictVal = dict(zip([key.text.replace(delim,'')],[value.text]))

        # Strips out spaces, parentheses, and slashes from key
        dictVal = {key.replace(' ','').replace('(','').replace(')','').replace('/',''): item for key, item in dictVal.items()}

        return dictVal
   
    ############################################################################
    ### algSetVersion()
    ###    set self.version for the object
    ###    has knowledge to decode NMS and Term strings and create an version
    ###    integer of format  MMnnPPbbb, representing major.minor.patch.build
    ###
    ############################################################################
    def algSetVersion(self):

        # Go to screen containing version and grab the version string
        self.connectToServer(self.url)
        values = []
        self.termIsMbr = False
        if self.type == "term":
            time.sleep(8)

            # Determine the Term Type
            try:
                self.scrollToText("Terminal Type")
                element = self.findElementByLocator("xpath=//span[@vid='termType']")
                if "MBR-4020" in element.text:
                    self.termIsMbr = True
            except:
                pass

            # Determine the Software Version
            try:
                self.scrollToText("VMT Software Version")
                element = self.findElementByLocator("xpath=//span[@vid='sysVersion']")
                values.append(element.text)
            except:
                pass
        else:
            element = self.findElementByLocator("xpath=//span[contains(text(),'Application Version: ')]")
            values.append(element.text)

        self.version = 0
        vstr=str(values[0])
        if self.type == "term":
            ver = vstr.split(".")
            major = int(ver[0])
            minor = int(ver[1])
            patch = int(ver[2])
            build = int(ver[3])
        else:
            # Fix build string to get MM.mm.bbb and avoid octal
            fix1=vstr.split(":")
            fix2 = fix1[1].split()
            ver = fix2[0].split(".")
            major = int(ver[0])
            minor = int(ver[1])
            patch = 0
            build = int(ver[2].lstrip("0"))

        self.version = (major * 10000000) + (minor * 100000) + (patch * 1000) + build


    ############################################################################
    ### algNmsGetVersion()
    ###    returns integer version of format MMnnPPbbb, 
    ###    representing major.minor.patch.build can be used in 
    ###    conjunction with RELEASE_NMS/TERM/_XXXX with  >,<,== comparators
    ###
    ############################################################################
    def algGetVersion(self):
        return self.version

    ############################################################################
    ### algStatusTableToDict("keyLocator","valueLocator","prefixName")
    ###
    ###   Inputs:
    ###     keyLocator - locator for key (eg. "xpath=//...")
    ###     valueLocator - locator for value relative to key (eg. "../td[2]/span[1]")
    ###     prefixName - prefix to be put before the key name in 
    ###       case of duplicate key names from different sections
    ###
    ###   Strips special characters from the key names and appends the prefix
    ###   Zips the keys and vlaues into a dictionary and returns the dictionary
    ###
    ###   NOTE: value must be obtained from element to correctly pair
    ###         since order in findElements not guaranteed to match
    ###
    ############################################################################
    def algStatusTableToDict(self,keyLocator,valueLocator,prefixName):
        keys = []
        values = []
        elements = self.findElementsByLocator(keyLocator)
        for element in elements:
            string = element.text
            for ch in [' ','(',')','/','.','-','&']:
                if ch in string:
                    string = string.replace(ch,'')
            string = string.replace('#','Num')
            if len(string) == 0:
                print "Field name is null\n"
                continue
            keys.append(prefixName+'_'+string)

            try:
                velement = element.find_element_by_xpath(valueLocator)
                values.append(velement.text)   
            except:
                values.append(string)

        tblDict = dict(zip(keys, values))

        return tblDict

####################################################################################
####################################################################################
### algNms Class
###   Class of methods used only for NMS; derived from algElements
###   See //Arclight/ArcLight/AcceptanceTest/Automation/MapTesting/Docs/AL_Automation_SDD.docx
### algNms("url", "usern", "passw", "resultsDir")
###
###   Inputs:
###     url - url of the website to open up to
###     usern - username
###     passw - password
###     resultsDir - path where screenshots will be located (ex. /tmp)
###
####################################################################################
####################################################################################
class algNms(algElements):
    def __init__(self, url, usern, passw, resultsDir):
        self.url = url
        self.usern = usern
        self.passw = passw
        self.type = "nms"
        algElements.__init__(self, resultsDir, vselPause)

    ####################################################################################
    ### algNmsLogin()
    ###
    ####################################################################################
    def algNmsLogin(self):
        self.algLogin()

    ####################################################################################
    ### algNmsLogout()
    ###
    ####################################################################################
    def algNmsLogout(self):
        self.algLogout()

    ####################################################################################
    ### algNmsDnldMapUpload("file", True/False, "antennaType")
    ###
    ###   Inputs:
    ###     file - path and name of the file you want to choose (ex. "/home/arclight/Gui/alGui.py")
    ###     isSigned - True to check the box, False to uncheck the box
    ###     antennaType - Antenna type to select from pulldown menu
    ###
    ###   Navigates to the "New File Upload" page: File Downloads -> File Upload -> Add
    ###   Fills out form and uploads it.
    ###
    ####################################################################################
    def algNmsDnldMapUpload(self, file, isSigned, antennaType):
        self.algClickMenuTab("File Downloads")
        self.algClickSubMenuLink("File Upload")
        self.clickButton("Add")
        self.selectPulldownOption("File Type:", "Map File")
        self.chooseFile("uploadedfile", file)
        self.clickCheckbox("Signed:", isSigned)
        self.setTextField("xpath=//label[text()='Antenna Type:']/..//input", antennaType)
        self.clickButton("Upload")

    ####################################################################################
    ### algNmsDnldMapProfile("profileName", True/False, defBitRate, True/False, 
    ###    "fileName", "script", "fl", dnldBitRatePercent, ['vmtList'])
    ###
    ###   Inputs:
    ###     profileName - Custom name given to profile
    ###     isEnabled - True to check the box, False to uncheck the box
    ###     defBitRate - Default Bitrate (kbps) entered as a number
    ###     isSigned - True to check the box, False to uncheck the box
    ###     fileName - Name of file (or start of name) to select from pulldown menu
    ###     script - Name of install script (or start of name) to select from pulldown menu
    ###     fl - Name (excluding [number]) of the forward link to fill in in the 
    ###        Download Bitrate field (under the Download Bitrates subtab)
    ###     dnldBitRatePercent - Entered as number: Download Bitrate = 
    ###         Max Control TX Bitrate * dnldBitRatePercent / 100
    ###     vmtList - Array of VMT Names to move to the Receiver List VMTs column 
    ###         (under the VMTs subtab)
    ###
    ###   Navigates to the "New Download Profile" page: File Downloads -> Download Profiles -> Add
    ###   Fills in information under each tab: General, Download Bitrates, and VMTs
    ###
    ####################################################################################
    def algNmsDnldMapProfile(self, profileName, isEnabled, defBitRate, isSigned, fileName, 
        script, fl, dnldBitRatePercent, vmtList):
        self.algClickMenuTab("File Downloads")
        self.algClickSubMenuLink("Download Profiles")
        self.clickButton("Add")
        self.setTextField("xpath=//label[text()='Name:']/..//input", profileName)
        self.clickCheckbox("Enabled:", isEnabled)
        self.setTextField("xpath=//label[text()='Default Bitrate (kbps):']/..//input", str(defBitRate))
        self.clickCheckbox("Signed:", isSigned)
        # Automatically selects "Map Bundle File" bundle type
        self.selectPulldownOption("Bundle Type:", "Map Bundle File")
        self.selectPulldownStartsWith("File Name:", fileName)
        self.selectPulldownStartsWith("Install Script Name:", script)
        self.clickButton("Download Bitrates")
        row = 1
        flRegex = re.compile("{}\s+\[\d+\]".format(fl))
        for i in self.findElementsByLocator("xpath=//td[@cellindex='1']/div"):
            # Finds the row with the Forward Link fl and fills in the Download Bitrate field
            if flRegex.match(i.text):
                maxBitrate = self.findElementByLocator("xpath=//tr[" + str(row) + "]/td[@cellindex='4']")
                dnldBitRate = int(maxBitrate.text) * dnldBitRatePercent / 100
                self.setTextField("xpath=//tr[" + str(row) + "]/td[@cellindex='5']//input", str(dnldBitRate))
                break
            row += 1
        self.clickButton("VMTs")
        # Selects all VMTs listed in the array vmtList
        for vmt in vmtList:
            self.algSelectVMT(1, vmt)

        # Clicks the right arrow to move all selected VMTs to Receiver List VMT column
        self.clickElement("xpath=//*[@id='gwtDiv']/div/div/div/div[3]/div[2]/div[3]/div/div[3]/div[2]/div/div[2]")
        self.clickButton("Save")

    ####################################################################################
    ### algNmsDnldMapStatus(ID)
    ###
    ###   Input:
    ###     ID - Profile of ID to obtain status from
    ###
    ###   Gets status from row with specified ID
    ###   Note: No return link yet, currently not used or tested
    ###
    ####################################################################################
    def algNmsDnldMapStatus(self):
        self.algClickMenuTab("File Downloads")
        self.algClickSubMenuLink("Download Profiles")
        self.clickButton("Status")

    ####################################################################################
    ### algNmsDisableDnldProfiles()
    ###
    ###   Navigates to the "Download Profile" page: File Downloads -> Download Profiles
    ###   Disables all profiles on page.
    ###
    ####################################################################################
    def algNmsDisableDnldProfiles(self):
        self.algClickMenuTab("File Downloads")
        self.algClickSubMenuLink("Download Profiles")
        COLUMN_NUM = 5
        profileNums = len(self.findElementsByLocator("xpath=//*[@id='gwtDiv']//table/tbody[2]//td[@cellindex='" + str(COLUMN_NUM) + "']"))
        for i in range(profileNums):
            row = 1
            for j in self.findElementsByLocator("xpath=//*[@id='gwtDiv']//table/tbody[2]//td[@cellindex='" + str(COLUMN_NUM) + "']"):
                if j.text == "Yes":
                    self.clickElement("xpath=//div[@class='x-grid-row-checker']/../../../..//tr[" + str(row) + "]/td[@cellindex='0']/div/div")
                    self.clickButton("Edit")
                    self.clickCheckbox("Enabled:", False)
                    self.clickButton("Save")
                    break
                row += 1



    ####################################################################################
    ### algNmsVmtReboot()
    ###
    ###   Inputs:
    ###       vmt - Terminal Name
    ###       hub - Hub name where terminal is located
    ###
    ###    Issue the VMT Reboot command for the specifiedn Terminal through the NMS
    ####################################################################################
    def algNmsVmtReboot(self, vmt, hub):

        if self.version < RELEASE_NMS_42:
          command = "Reboot"
        else:
          command = "VMT Reboot"

        self.algNmsVmtCommand(vmt, hub, command)

    ####################################################################################
    ### algNmsVmtLogout()
    ###
    ###   Inputs:
    ###       vmt - Terminal Name
    ###       hub - Hub name where terminal is located
    ###
    ###    Issue the VMT Logout command for the specifiedn Terminal through the NMS
    ####################################################################################
    def algNmsVmtLogout(self, vmt, hub):

        if self.version < RELEASE_NMS_42:
          command = "Logout"
        else:
          command = "VMT Logout"

        self.algNmsVmtCommand(vmt, hub, command)

    ####################################################################################
    ### algNmsVmtRelogin()
    ###
    ###   Inputs:
    ###       vmt - Terminal Name
    ###       hub - Hub name where terminal is located
    ###
    ###    Issue the VMT Relogin command for the specifiedn Terminal through the NMS
    ####################################################################################
    def algNmsVmtRelogin(self, vmt, hub):

        if self.version < RELEASE_NMS_42:
          command = "Relogin"
        else:
          command = "VMT Relogin"

        self.algNmsVmtCommand(vmt, hub, command)

    ####################################################################################
    ### algNmsVmtCommand()
    ###
    ###   Inputs:
    ###       vmt - Terminal Name
    ###       hub - Hub name where terminal is located
    ###       command - Logout, Relogin, Reboot, Beam Redirect
    ###
    ###   Issues specified command for the VMT associated with groupId
    ###
    ####################################################################################
    def algNmsVmtCommand(self, vmt, hub, command):
        self.algClickMenuTab("VMT Fleet")
        self.algClickSubMenuLink("VMT Configuration")

        searchLocator = "xpath=//input[@type='text']"
        self.setTextField(searchLocator, vmt)
        element = self.findElementByLocator(searchLocator)
        element.send_keys(Keys.RETURN)
        self.setTextField(searchLocator, '')

        self.algSelectTableRow(2, vmt)
        self.clickButton("Commands")
        self.clickElement("xpath=//span[text()='"+command+"']")

        if self.version < RELEASE_NMS_42:
            self.clickElement("xpath=//div[contains(text(),'"+hub+"')]")
            self.clickButton("OK")
        else:
            self.clickButton("Yes")

        if self.version < RELEASE_NMS_42:
            self.clickElement("xpath=//div[contains(text(),'Command:')]")
        self.clickButton("OK")


####################################################################################
####################################################################################
### algEms Class
###   Class of methods used only for EMS
###   See //Arclight/ArcLight/AcceptanceTest/Automation/MapTesting/Docs/AL_Automation_SDD.docx
###
### algEms("url", "user", "pw", "resultsDir")
###   Inputs:
###     url - url of the website to open up to
###     user - username
###     pw - password
###     resultsDir - path where screenshots will be located (ex. /tmp)
###
####################################################################################
####################################################################################
class algEms(algElements):
    def __init__(self, url, user, pw, resultsDir):
        self.url = url
        self.usern = user
        self.passw = pw
        self.type = "ems"
        algElements.__init__(self, resultsDir, vselPause)

    ####################################################################################
    ### algEmsLogin()
    ###
    ####################################################################################
    def algEmsLogin(self):
        self.algLogin()

    ####################################################################################
    ### algEmsLogout()
    ###
    ####################################################################################
    def algEmsLogout(self):
        self.algLogout()

    ####################################################################################
    ### algEmsAcsmFlUpdate("profileName", "hub", txIf, rxFreq, chip)
    ###
    ###   Inputs:
    ###     profileName - corresponds to the FL Name field
    ###     hub - Hub name (or partial name) from hub pulldown menu
    ###     txIf - corresponds to the Hub FL Center Tx IF Frequency field
    ###     rxFreq - corresponds to the Terminal FL Center Rx Frequency field
    ###     chip - corresponds to the Chip Rate field
    ###
    ###     Navigates to the "Edit ACSM Forward Link" page: SDL Management -> Forward Links -> Edit ACSM
    ###     Edits part of the form and saves revisions.
    ###        Note: hub cannot actually be changed
    ###
    ####################################################################################
    def algEmsAcsmFlUpdate(self, profileName, hub, txIf, rxFreq, chip):
        self.algClickMenuTab("SDL Management")
        self.algClickSubMenuLink("Forward Links")
        self.algEmsAcsmFlSelectProfile(profileName)
        self.clickButton("Edit")
        self.algEmsAcsmFlName(profileName)
        self.algEmsAcsmFlHub(hub)
        self.algEmsAcsmFlHubCenterFreq(txIf, rxFreq)
        self.algEmsAcsmFlChipRate(chip)
        self.clickButton("Save")

    ####################################################################################
    ### algEmsAcsmFlSelectProfile(TARGET_FL_PROFILE)
    ###
    ###   Input:
    ###     TARGET_FL_PROFILE - Name of the profile to be selected from the table
    ###
    ###   Calls algSelectTableRow()
    ###
    ####################################################################################
    def algEmsAcsmFlSelectProfile(self, TARGET_FL_PROFILE):
        self.algSelectTableRow(2, str(TARGET_FL_PROFILE))

    ####################################################################################
    ### algEmsAcsmFlName("FL_PROFILE")
    ###
    ###   Input:
    ###     FL_PROFILE - corresponds to the FL Name field
    ###
    ###   Inserts FL_PROFILE into FL Name text field on New/Edit "ACSM Forward Link" page.
    ###   Note: Used by algEmsAcsmFlUpdate
    ###
    ####################################################################################
    def algEmsAcsmFlName(self, FL_PROFILE):
        self.setTextField("xpath=//label[text()='FL Name:']/..//input", FL_PROFILE)

    ####################################################################################
    ### algEmsAcsmFlHub("HUB_NAME")
    ###
    ###   Input:
    ###     HUB_NAME - Hub name (or partial name) from hub pulldown menu
    ###
    ###   Selects HUB_NAME (or whichever option starts with HUB_NAME) from the hub pulldown menu
    ###     on New/Edit "ACSM Forward Link" page.
    ###   Note: Used by algEmsAcsmFlUpdate
    ###
    ####################################################################################
    def algEmsAcsmFlHub(self, HUB_NAME):
        self.selectPulldownStartsWith("Hub:", HUB_NAME)

    ####################################################################################
    ### algEmsAcsmFlHubCenterFreq(HUB_FL_CENTER, TERM_FL_CENTER)
    ###
    ###   Inputs:
    ###     HUB_FL_CENTER - corresponds to the Hub FL Center Tx IF Frequency field
    ###     TERM_FL_CENTER - corresponds to the Terminal FL Center Rx Frequency field
    ###
    ###   Fills out the Hub FL Center Tx and Rx frequency fields with HUB_FL_CENTER and TERM_FL_CENTER respectively
    ###     on New/Edit "ACSM Forward Link" page.
    ###   Note: Used by algEmsAcsmFlUpdate
    ###
    ####################################################################################
    def algEmsAcsmFlHubCenterFreq(self, HUB_FL_CENTER, TERM_FL_CENTER):
        # Convert last digit to decimal 
        hubFreq = float(HUB_FL_CENTER) / 10.0
        termFreq = float(TERM_FL_CENTER) / 10.0
        self.setTextField("xpath=//label[text()='Hub FL Center Tx IF Frequency (MHz):']/..//input", str(hubFreq))
        self.setTextField("xpath=//label[text()='Terminal FL Center Rx Frequency (MHz):']/..//input", str(termFreq))

    ####################################################################################
    ### algEmsAcsmFlRfBand("RF_BAND")
    ###
    ###   Input:
    ###     RF_BAND - Selects an option from RF Band pulldown menu (based on full band name or start of name)
    ###
    ###   Selects RF_BAND from RF Band list on New/Edit "ACSM Forward Link" page.
    ###   Note: Use after calling algEmsAcsmFlUpdate or after clicking "Add" on the "Forward Links" page.
    ###
    ####################################################################################
    def algEmsAcsmFlRfBand(self, RF_BAND):
        self.selectPulldownStartsWith("RF Band:", RF_BAND)

    ####################################################################################
    ### algEmsAcsmFlChipRate(chip)
    ###
    ###   Input:
    ###     chip - corresponds to the Chip Rate field
    ###
    ###   Fills in the Chip Rate text field with chip on New/Edit "ACSM Forward Link" page.
    ###   Note: Used by algEmsAcsmFlUpdate
    ###
    ####################################################################################
    def algEmsAcsmFlChipRate(self, FL_CHIP_RATE):
        self.setTextField("xpath=//label[text()='Chip Rate (Kcps):']/..//input", str(FL_CHIP_RATE))

    ####################################################################################
    ### algEmsAcsmFlRolloffFactor(ROLLOFF)
    ###
    ###   Input:
    ###     ROLLOFF - corresponds to Rolloff Factor pulldown menu
    ###
    ###   Selects ROLLOFF from Rolloff Factor pulldown menu on New/Edit "ACSM Forward Link" page.
    ###   Note: Use after calling algEmsAcsmFlUpdate or after clicking "Add" on the "Forward Links" page.
    ###
    ####################################################################################
    def algEmsAcsmFlRolloffFactor(self, ROLLOFF):
        self.selectPulldownOption("Rolloff Factor:", str(ROLLOFF))

    ####################################################################################
    ### algEmsAcsmFlPilot(PILOT)
    ###
    ###   Input:
    ###     PILOT - corresponds to Piloting pulldown menu
    ###
    ###   Selects PILOT from Piloting (%) pulldown menu on New/Edit "ACSM Forward Link" page.
    ###   Note: Use after calling algEmsAcsmFlUpdate or after clicking "Add" on the "Forward Links" page.
    ###
    ####################################################################################
    def algEmsAcsmFlPilot(self, PILOT):
        self.selectPulldownOption("Piloting (%):", str(PILOT))

    ####################################################################################
    ### algEmsAcsmFlPbr(PBR_IP_1, PBR_IP_2, PBR_IP_3, PBR_IP_4)
    ###
    ###   Inputs:
    ###     PRB_IP_1.PBR_IP_2.PBR_IP_3.PBR_IP_4 - PBR Data IP Address
    ###
    ###   Fills in all four PBR Data IP Address fields on New/Edit "ACSM Forward Link" page.
    ###   Note: Use after calling algEmsAcsmFlUpdate or after clicking "Add" on the "Forward Links" page.
    ###
    ####################################################################################
    def algEmsAcsmFlPbr(self, PBR_IP_1, PBR_IP_2, PBR_IP_3, PBR_IP_4):
        locator = "xpath=//label[text()='PBR Data IP Address:']/..//"
        self.setTextField(locator + "input[1]", str(PBR_IP_1))
        self.setTextField(locator + "input[2]", str(PBR_IP_2))
        self.setTextField(locator + "input[3]", str(PBR_IP_3))
        self.setTextField(locator + "input[4]", str(PBR_IP_4))

    ####################################################################################
    ### algEmsAcsmFlMcast(MCAST_IP)
    ###
    ###   Input:
    ###     MCAST_IP - corresponds to last byte of the Control Traffic IP Multicast Address
    ###
    ###   Fills in last field of Ctrl Traffic IP Multicast Address on New/Edit "ACSM Forward Link" page.
    ###   Note: Use after calling algEmsAcsmFlUpdate or after clicking "Add" on the "Forward Links" page.
    ###
    ####################################################################################
    def algEmsAcsmFlMcast(self, MCAST_IP):
        self.setTextField("xpath=//label[text()='Ctrl Traffic IP Multicast Address:']/..//input[4]", str(MCAST_IP))

    ####################################################################################
    ### algEmsAcsmFlState(True/False)
    ###
    ###   Input:
    ###     ACSM_ADAPT - True to check the box, False to uncheck the box
    ###
    ###   Allows you to choose state of ACSM Adaptation Enabled checkbox (True or False)
    ###     on New/Edit "ACSM Forward Link" page in Basic Settings section.
    ###   Note: Use after calling algEmsAcsmFlUpdate or after clicking "Add" on the "Forward Links" page.
    ###
    ####################################################################################
    def algEmsAcsmFlState(self, ACSM_ADAPT):
        self.clickCheckbox("ACSM Adaptation Enabled:", ACSM_ADAPT)

    ####################################################################################
    ### algEmsAcsmFlModcode("MODCODE")
    ###
    ###   Input:
    ###     MODCODE - corresponds to Control Traffic Modcode pulldown menu (based on full band name or start of name)
    ###
    ###   Selects MODCODE from Control Traffic Modcode list on New/Edit "ACSM Forward Link" page in Basic Settings section.
    ###   Note: Use after calling algEmsAcsmFlUpdate or after clicking "Add" on the "Forward Links" page.
    ###
    ####################################################################################
    def algEmsAcsmFlModcode(self, MODCODE):
        self.selectPulldownStartsWith("Control Traffic Modcode:", MODCODE)

    ####################################################################################
    ### algEmsAcsmFlExpandAdvanced()
    ###
    ###   Expands Advanced Settings window on New/Edit "ACSM Forward Link" page.
    ###   Note: Use after calling algEmsAcsmFlUpdate or after clicking "Add" on the "Forward Links" page.
    ###
    ####################################################################################
    def algEmsAcsmFlExpandAdvanced(self):
        self.clickElement("xpath=//span[text()='Advanced Settings']/../div/div")

    ####################################################################################
    ### algEmsFlEnable("HubName")
    ###
    ###   Input:
    ###     HubName - name of hub to have its EFLM enabled
    ###
    ###   Calls algEmsFlState in order to enable the EFLM of HubName
    ###
    ####################################################################################
    def algEmsFlEnable(self, HubName):
        self.algEmsFlState(HubName, True)

    ####################################################################################
    ### algEmsFlDisable("HubName")
    ###
    ###   Input:
    ###     HubName - name of hub to have its EFLM disabled
    ###
    ###   Calls algEmsFlState in order to disable the EFLM of HubName
    ###
    ####################################################################################
    def algEmsFlDisable(self, HubName):
        self.algEmsFlState(HubName, False)

    ####################################################################################
    ### algEmsFlState("HubName",True/False)
    ###
    ###   Input:
    ###     HubName - name of hub to have its EFLM disabled
    ###    txState - True if enable, false if disable
    ###
    ###   Navigates to the "TA Hub EMS - Components" page: Hubs -> Components
    ###   Selects HubName and enables/disables its EFLM based on txState
    ###   Notes: Gets called by algEmsFlEnable/Disable
    ###
    ####################################################################################
    def algEmsFlState(self, HubName, txState):
        self.algClickMenuTab("Hubs")
        self.algSelectTableRow(2, HubName)
        self.clickButton("Components")
        self.algSelectTableRow(1, "EFLM")
        self.clickButton("Commands")
        if txState==True:
            self.clickElement("xpath=//span[text()='EFLM Tx Enable']")
        elif txState==False:
            self.clickElement("xpath=//span[text()='EFLM Tx Disable']")

        self.clickElement("xpath=//div[contains(text(),'command will be sent to TA EFLM. Proceed?')]/../..//div[text()='Yes']")
        self.clickButton("OK")

####################################################################################
####################################################################################
### algTerm Class
###   Class of methods used only for Terminal
###   See //Arclight/ArcLight/AcceptanceTest/Automation/MapTesting/Docs/AL_Automation_SDD.docx
###
### algTerm("url", "user", "pw", "resultsDir")
###
###   Inputs:
###     url - url of the website to open up to
###     user - username for Configuration tab
###     pw - password for Configuration tab
###     resultsDir - path where screenshots will be located (ex. /tmp)
###
####################################################################################
####################################################################################
class algTerm(algElements):
    def __init__(self, url, user, pw, resultsDir, pause=vselPause):
        self.url = url
        self.usern = user
        self.passw = pw
        self.type = "term"
        algElements.__init__(self, resultsDir, pause, brow="firefox")

    ####################################################################################
    ### algTermGoToPage()
    ###
    ###   Calls connectToServer in order to go to the initialized url since connectToServer cannot be called from algUnitTest.py.
    ###   Note: Called by algTermStatusFLLock and algTermStatusVersion.
    ###
    ####################################################################################
    def algTermGoToPage(self):
        self.connectToServer(self.url)

    ####################################################################################
    ### algTermLogin()
    ###
    ####################################################################################
    def algTermLogin(self):
        self.algLogin()

    ####################################################################################
    ### algTermLogout()
    ###
    ###   Note: Never used (Terminal has no logout button)
    ####################################################################################
    def algTermLogout(self):
        pass

    ####################################################################################
    ### algTermMapUpload("sedfile", "sscffile", "rlcfile" or None, "gdrmfile" or None)
    ###
    ###   Inputs:
    ###     sedfile - full filepath name of sed file
    ###     sscffile - full filepath name of sscf file
    ###     rlcfile - full filepath name of rlc file (or None if no file will be uploaded)
    ###     gdrmfile - full filepath name of gdrm file (or None if no file will be uploaded)
    ###
    ###   Navigates to "Satellite Configuration" page: Configuration -> Satellite
    ###   Uploads SED and SSCF files or uploads all four files.
    ###   Note: Must be logged into Configuration and on Configuration tab to use.
    ###
    ####################################################################################
    def algTermMapUpload(self, sedfile, sscffile, rlcfile, gdrmfile):
        self.algClickSubMenuLink("Satellite")
        self.chooseFile("sedFile", sedfile)
        self.chooseFile("sscfFile", sscffile)

        if rlcfile and gdrmfile:
            self.clickElement("link=Add RLC + GDRM...")
            time.sleep(1)
            self.chooseFile("rlcFile", rlcfile)
            self.chooseFile("gdrmFile", gdrmfile)

        self.clickElement("id=uploadButton")
        # Waits up to specified timeout for all two or four files to be uploaded 
                # so algTermConfVersion can be run immediately afterward
        # Displays error message if times out
        try:
            WebDriverWait(self.driver, 180).until(EC.visibility_of_element_located((By.ID, "saveButton")), "Took more than 3 minutes to upload files")
        except:
            self.algScreenShot("algTermUploadTimeout")
            time.sleep(2)
            raise

    ####################################################################################
    ### algTermConfVersion()
    ###
    ###   Grabs current version of all file types on the "Satellite Configuration" page and puts them into a data dictionary that is returned.
    ###   Note: Call this method after using algTermMapUpload
    ###
    ####################################################################################
    def algTermConfVersion(self):
        # Get the version number for each file from the "New" column
        element = self.findElementByLocator("id=newSed")
        sedver = element.text
        element = self.findElementByLocator("id=newSscf")
        sscfver = element.text
        element = self.findElementByLocator("id=newRlc")
        rlcver = element.text
        element = self.findElementByLocator("id=newGdrm")
        gdrmver = element.text
        # If rlc and gdrm files were not uploaded
        if rlcver == "(Delete)" and gdrmver == "(Delete)":
            # Put sed and sscf file version numbers into a data dictionary 
            #   and put "" (empty string) for rlc and gdrm
            data_dict = {
                'sedVersion': sedver,
                'sscfVersion': sscfver,
                'rlcVersion': "",
                'gdrmVersion': "",
                }
        # Else put all file version numbers into a data dictionary
        else:
            data_dict = {
                'sedVersion': sedver,
                'sscfVersion': sscfver,
                'rlcVersion': rlcver,
                'gdrmVersion': gdrmver,
                }
        return data_dict

    ####################################################################################
    ### algTermConfVerSave()
    ###
    ###   Clicks the "Save files" button on the "satellite Configuration" page and waits at least 3 minutes for the files to be saved
    ###   Displays error message if it takes more than 3 minutes
    ###   Note: Do not use this method until algTermConfVersion confirms that the versions are correct
    ###
    ####################################################################################
    def algTermConfVerSave(self):
        #self.clickButton("'Save files'")
        self.clickElement("id=saveButton")
        WebDriverWait(self.driver, 180).until(EC.element_to_be_clickable((By.ID, "rebootButton")), "Took more than 3 minutes to save files")

    ####################################################################################
    ### algTermConfVerReboot()
    ###
    ###   Reboots the system with the files that were just saved by algTermConfVersionSave
    ###   Note: Only works immediately after calling algTermConfVersionSave
    ###
    ####################################################################################
    def algTermConfVerReboot(self):
        #self.clickButton("Reboot")
        self.clickElement("id=rebootButton")


    ####################################################################################
    ### algTermConfVerCancel()
    ###
    ###   Cancels the uploading of files by refreshing the page, thus clearing the uploaded files
    ###   Note: Use after algTermConfVersion if version numbers are incorrect
    ###
    ####################################################################################
    def algTermConfVerCancel(self):
        self.driver.refresh()

    ####################################################################################
    ### algTermStatusFLLock()
    ###
    ###   Grabs certain information from "Forward Link Status" page and puts it into a data dictionary that is returned:
    ###     FL Waveform/ID, State, Downlink Frequency, Es/No, Amplitude, AGC, Modcode, Modulation,
    ###       L-Band Frequency, LNB LO Frequency, and Rx Frequency Offset
    ###   Note: Do not need to be logged in. Page is accessed automatically (no open window or navigation required).
    ###
    ####################################################################################
    def algTermStatusFLLock(self):

        # Terminal sometimes needs 2 tries
        try:
            self.algTermGoToPage()
            self.algClickSubMenuLink("Forward Link")
            element = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//span[@vid='rxFreqOff']")), "Couldn't find element")
        except:
            self.algTermGoToPage()
            self.algClickSubMenuLink("Forward Link")
            element = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//span[@vid='rxFreqOff']")), "Couldn't find element")

        element = self.findElementByLocator("xpath=//span[@vid='flType']")
        element2 = self.findElementByLocator("xpath=//span[@vid='flId']")
        waveform = element.text + " / " + element2.text
        element = self.findElementByLocator("xpath=//span[@vid='flState']")
        flState = element.text
        element = self.findElementByLocator("xpath=//span[@vid='downlinkFreq']")
        dlFreq = int(element.text.replace(',','')) # +  " Hz"
        #element = self.findElementByLocator("xpath=//span[@vid='flEsNo']")
        #esno = float(element.text) # + " dB"
        #element = self.findElementByLocator("xpath=//span[@vid='flAmp']")
        #amplitude = float(element.text) # + " dB"
        #element = self.findElementByLocator("xpath=//span[@vid='flAgc']")
        #agc = element.text #agc = int(element.text) once changed from hex to int
        #element = self.findElementByLocator("xpath=//span[@vid='modCode']")
        #modcod = int(re.compile("\d+").match(element.text).group(0))
        #element = self.findElementByLocator("xpath=//span[@vid='modulation'][@sec='acsm']")
        #modul = element.text
        element = self.findElementByLocator("xpath=//span[@vid='lbandFreq']")
        lbandFreq = int(element.text.replace(',','')) # + " Hz"
        element = self.findElementByLocator("xpath=//span[@vid='lnbLoFreq']")
        lnbloFreq = int(element.text.replace(',','')) # + " Hz"
        element = self.findElementByLocator("xpath=//span[@vid='rxFreqOff']")
        rxFreqOff = int(element.text.replace(',','')) # + " Hz"

        # Don't really need these and problem with new terminal , so just zero
        esno = 0 
        amplitude = 0
        agc = 0 
        modcod = 0
        modul = 0

        # Adjust Frequencies to MHZ x 10
        data_dict = {
            'waveForm': waveform,
            'flState': flState,
            'dlFreq': (dlFreq/100000),
            'esno': esno,
            'amplitude': amplitude,
            'agc': agc,
            'modcod': modcod,
            'modul': modul,
            'lbandFreq': (lbandFreq/100000),
            'lnbloFreq': (lnbloFreq/100000),
            'rfFreqOff': rxFreqOff
        }
        return data_dict


    ####################################################################################
    ### algTermStatusVersion()
    ###
    ###   Grabs file statuses from "General Status" page in the Version Status subsection and puts it into a data dictionary that is returned.
    ###   Note: Do not need to be logged in. Page is accessed automatically (no open window or navigation required).
    ###
    ####################################################################################
    def algTermStatusVersion(self):
        self.algTermGoToPage()
        element = self.findElementByLocator("xpath=//span[@vid='sedVersion']")
        sedver = element.text
        element = self.findElementByLocator("xpath=//span[@vid='sscfVersion']")
        sscfver = element.text
        element = self.findElementByLocator("xpath=//span[@vid='rlcVersion']")
        rlcver = element.text
        element = self.findElementByLocator("xpath=//span[@vid='gdrmVersion']")
        gdrmver = element.text
        data_dict = {
            'sedVersion': sedver,
            'sscfVersion': sscfver,
            'rlcVersion': rlcver,
            'gdrmVersion': gdrmver,
        }
        return data_dict

    ####################################################################################
    ### algTermRestore("binFile")
    ###
    ###   Inputs:
    ###     binFile - Configuration file to be used to restore the system.
    ###
    ###   Clicks on Save & Restore submenu link.
    ###   Uploads binFile.
    ###   Applies and imports the configuration.
    ###
    ####################################################################################
    def algTermRestore(self, binFile):
        self.algClickSubMenuLink("Save & Restore")
        time.sleep(3)
        self.chooseFile("importCfgFileName", binFile)

        time.sleep(5)
        self.clickElement("id=uploadCfgButton")
        time.sleep(3)
        WebDriverWait(self.driver, 180).until(EC.element_to_be_clickable((By.ID, "importCfgApplyBtn")), "Took more than 3 minutes to upload file")

        self.clickElement("id=importCfgApplyBtn")
        time.sleep(3)
        WebDriverWait(self.driver, 180).until(EC.element_to_be_clickable((By.ID, "importCfgConfirmBtn")), "Took more than 3 minutes for confirm button")

        self.clickElement("id=importCfgConfirmBtn")

    ############################################################################
    ### More generic function to grab section headers and first three letters 
    ###  of sections headers for prefixes automatically
    ############################################################################
    #def algTermStatus(self,subtabLink):
    #    self.algClickSubMenuLink(subtabLink)
    #    sections = []
    #    sectionElements = self.findElementsByLocator("xpath=//div[@id='mainContent']/div[@class='sectionHeader']")
    #    for sectionElement in sectionElements:
    #        sections.append(sectionElement.text)
    #    print sections
    #    prefixNames = []
    #    for section in sections:
    #        prefixNames.append(section[:3])
    #    print prefixNames
    #
    #    return self.algTermStatusTable(sections,prefixNames)

    ############################################################################
    ### algTermStatusGeneral()
    ###
    ###   Clicks on "General" submenu link.
    ###   Calls algTermStatusTable with hardcoded section names and prefixes
    ###   Sample: To get the values of DOS Velocity under the Return Link (Transmit)
    ###     Status section (which has the prefix 'RL'), type the following:
    ###       sampleDict = algTermStatusGeneral()
    ###       print sampleDict['RL_DOSVelocity']
    ###
    ###   Note: May want to consider using algTermStatus at some point instead
    ###
    ############################################################################
    def algTermStatusGeneral(self):
        self.algClickSubMenuLink("General")
        if self.version < RELEASE_TERM_55:
             sections = ['TERMINAL STATUS', 'Forward Link (Receive) Status', 'Return Link (Transmit) Status', 'Positional', 'Hardware', 'VERSION STATUS', 'LAN Status'] 
        else:
             sections = ['VMBR TERMINAL STATUS', 'VMBR Forward Link (Receive) Status', 'VMBR Return Link (Transmit) Status', 'Positional', 'Hardware', 'VERSION STATUS', 'LAN Status'] 
        prefixNames = ['TS', 'FL', 'RL', 'Pos', 'HW', 'VS', 'LS']

        return self.algTermStatusTable(sections, prefixNames)

    ############################################################################
    ### algTermStatusFL()
    ###
    ###   Clicks on "Forward Link" submenu link.
    ###   Calls algTermStatusTable with hardcoded section names and prefixes
    ###   Note: See algTermStatusGeneral() for tips on how to use this function
    ###
    ###   Note: May want to consider using algTermStatus at some point instead
    ###
    ############################################################################
    def algTermStatusFL(self):
        self.algClickSubMenuLink("Forward Link")

        if self.termIsMbr:
            #TODO - Fix when MBR-4020 gets section header fixed
            #sections = ['Forward Link (Receive) Status', 'IP Packet Receive Statistics'] 
            sections = ['Forward Link (Receive) Status']
            prefixNames = ['FLS']
        else:
            sections = ['Forward Link (Receive) Status', 'FLR'] 
            prefixNames = ['FLS', 'FLR']

        return self.algTermStatusTable(sections, prefixNames)

    ###########################################################################
    ### algTermStatusRL()
    ###
    ###   Clicks on "Return Link" submenu link.
    ###   Calls algTermStatusTable with hardcoded section names and prefixes
    ###   Note: See algTermStatusGeneral() for tips on how to use this function
    ###
    ###   Note: May want to consider using algTermStatus at some point instead
    ###
    ############################################################################
    def algTermStatusRL(self):
        self.algClickSubMenuLink("Return Link")

        if self.termIsMbr:
            sections = ['Return Link (Transmit) Status', 'IP Packet Transmit Statistics'] 
        else:
            sections = ['Return Link (Transmit) Status', 'TXR'] 
        prefixNames = ['RLS', 'TXR']

        return self.algTermStatusTable(sections, prefixNames)

    ############################################################################
    ### algTermStatusACU()
    ###
    ###   Clicks on "ACU / Antenna" submenu link.
    ###   Calls algTermStatusTable with hardcoded section names and prefixes
    ###   Note: See algTermStatusGeneral() for tips on how to use this function
    ###
    ###   Note: May want to consider using algTermStatus at some point instead
    ###
    ############################################################################
    def algTermStatusACU(self):

        self.algClickSubMenuLink("ACU / Antenna")
        if self.version < RELEASE_TERM_55:
            sections = ['ACU', 'Antenna'] 
            prefixNames = ['ACU', 'Ant']
            option = 0
        else:
            sections = ['ACU', 'Antenna', 'Navigation'] 
            prefixNames = ['ACU', 'Ant', 'Nav']
            option = 1

        return self.algTermStatusTable(sections, prefixNames, option)

    ############################################################################
    ### algTermStatusTable([sections],[prefixNames])
    ###
    ###   Inputs:
    ###     sections - sections on given page to collect information from
    ###     prefixNames - nicknames for sections to be put before each key in 
    ###       case of duplicate key names from different sections
    ###
    ###   Finds the key and value within each section and calls algStatusTableToDict
    ###     in order to turn it into a dictionary entry.
    ###   Appends everything into a single dictionary and returns it.
    ###
    ############################################################################
    def algTermStatusTable(self,sections,prefixNames,option=0):
        i = 0;
        tblDict = {}

        for secName in sections:
            if option == 1:
                # Fix for 5.5 ACU/Antenna page 
                keyLocator = "xpath=//div[@class='sectionHeader']/table/tbody/tr/td[text()='"+secName+"']//../../../../following-sibling::table[1]/tbody/tr/td/table/tbody/tr[@style='display: table-row;']/td[1]"
            else:
                keyLocator = "xpath=//div[text()='"+secName+"']/following-sibling::table[1]//table/tbody/tr[@style='display: table-row;']/td[1]"
            valueLocator = "../td[2]/span[1]"
            tblDict.update(self.algStatusTableToDict(keyLocator,valueLocator,prefixNames[i]))
            i += 1 

        return tblDict


############################################################################
############################################################################
### algNmspm Class
###   Class of methods used only for NMSPM
###   See //Arclight/ArcLight/AcceptanceTest/Automation/MapTesting/Docs/AL_Automation_SDD.docx
###
### algNmspm("url", "user", "pw", "resultsDir")
###
###   Inputs:
###     url - url of the website to open up to
###     user - username for Configuration tab
###     pw - password for Configuration tab
###     resultsDir - path where screenshots will be located (ex. /tmp)
###
############################################################################
class algNmspm(algElements):
    def __init__(self, url, user, pw, resultsDir):
        self.url = url
        self.usern = user
        self.passw = pw
        self.type = "nms"
        algElements.__init__(self, resultsDir, vselPauseNlg, brow="firefox")

    ############################################################################
    ### algNmspmLogin()
    ###
    ###   Goes to URL, clicks on "Map" tab, and switches to the map iframe 
    ###     in order to interact with it
    ###   CAVEAT - using knowledge that there is 1 iframe with 2 tags, use 2nd
    ###     i.e. iframeList[1]
    ###
    ############################################################################
    def algNmspmLogin(self):
        self.algLogin()
        self.algClickMenuTab("Map")
        iframeList = self.driver.find_elements_by_tag_name("iframe")
        self.driver.switch_to.frame(iframeList[1])

    ############################################################################
    ### algNmspmLogout()
    ###
    ###   Switches back to main iframe in order to interact with logout button
    ###
    ############################################################################
    def algNmspmLogout(self):
        self.driver.switch_to_default_content()
        self.algLogout()

    ############################################################################
    ### algNmspmSearchVMT("searchText")
    ###
    ###   Inputs:
    ###     searchText - text to be search for
    ###
    ###   Navigates to VMT List page and types searchText into the search field located at searchLocator
    ###   Double clicks on first result, which takes user to "VMT Information" page.
    ### 
    ############################################################################
    def algNmspmSearchVmt(self, searchText):
        self.clickButton("Map")
        self.clickButton("VMT List")

        searchLocator = "xpath=//input[@placeholder='Search VMT List']"
        self.setTextField(searchLocator, searchText)
        element = self.findElementByLocator(searchLocator)
        element.send_keys(Keys.RETURN)


    ############################################################################
    ### Return a dictionary containing VMT List for terminal
    ############################################################################
    def algNmspmGetVmtlist(self, vmtName):
        prefixName="VL"
        keys = []
        values = []
        for i in range(1, 27):
            self.driver.set_window_size(4096, 4096)
            if i == 1:
                try:
                    self.scrollToText("VMT Name")
                except:
                    pass
            elif i == 7:
                try:
                    self.scrollToText("Longitude")
                except:
                    pass
            elif i == 12:
                try:
                    self.scrollToText("SED Version")
                except:
                    pass
            elif i == 19:
                try:
                    self.scrollToText("RL Name")
                except:
                    pass
            elif i == 25:
                try:
                    self.scrollToText("RL Current CRL Adaptation")
                except:
                    pass

            element = self.findElementByLocator('xpath=//*[@id="abstractPanel"]/div/div[2]/div[2]/div/div[1]/div/table/tbody[2]/tr/td['+str(i)+']/div/span')
            string = element.text
            for ch in [' ','(',')','/','.','-','&']:
                if ch in string:
                    string = string.replace(ch,'')
            string = string.replace('#','Num')
            if len(string) == 0:
                print "Field name is null\n"
                continue
            keys.append(prefixName+'_'+string)

            try:
                velement = element.find_element_by_xpath('../../../../../../../../div[2]/div/table/tbody[2]/tr/td['+str(i)+']/div/span')
                values.append(velement.text)   
            except:
                values.append(string)

        tblDict = dict(zip(keys, values))

        return tblDict

    ############################################################################
    ### Goto VMT Basic screen; called after algNmspmGetVmtlist and
    ###   before algNmspmGetBasic()
    ############################################################################
    def algNmspmGotoBasic(self, vmtName):
        self.doubleClickElement("xpath=//span[text()='"+vmtName+"']")
        try:
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[text()='Basic']")), "Couldn't find element")
        except:
            pass
        self.driver.set_window_size(2048, 2048)

    ############################################################################
    ### algNmspmGetBasic()
    ###
    ###   Grabs every piece of information displayed that contains a colon and 
    ###   puts it in a dictionary
    ###   Strips special characters from keys for easy conversion into SQL table
    ###
    ###   Note: Can only be used after calling algNmspmSearchVMT() 
    ###      (navigating to "VMT Information" screen)
    ###
    ############################################################################
    def algNmspmGetBasic(self):

        basicDict = self.algStatusBasic1(': ')

        if self.version < RELEASE_NMS_42:
            # Other keys/tags that don't follow pattern 
            #  of the Basic1 key+delim+value 
            basicDict.update(self.algStatusBasic2('Uptime'))
            basicDict.update(self.algStatusBasic2('Status'))
            basicDict.update(self.algStatusBasic2('Last Login'))

        return basicDict
   
    ############################################################################
    ### algNmspmChartScreenShots("chartPrefix", duration)
    ###
    ###   Input:
    ###     chartPrefix - starting string of chartname
    ###       Ex. algNmspmChartScreenShots("FL") to take a screenshot of all 
    ###        charts starting with FL
    ###     duration - length of test in seconds to adjust zoom
    ###
    ###   Takes a screenshot of all charts whose names start with chartPrefix 
    ###   Note: Can only be used after calling algNmspmSearchVMT() (navigating to "VMT Information" screen)
    ###
    ############################################################################
    def algNmspmChartScreenShots(self,chartPrefix, duration=0):

        self.clickButton("Charts")

        # Select Chart Range for this Group; if 0, use default (currently 24 Huors)
        # Workaround - Resize window to force iframe to reconfigure
        self.driver.set_window_size(1280, 1024)
        if duration != 0 :
            hours = duration/60/60 
            if hours < 1 :
                zoomtxt= "1 Hour"
                zoom = 1
            elif hours < 4 :
                zoomtxt= "4 Hours"
                zoom = 2
            elif hours < 8 :
                zoomtxt= "8 Hours"
                zoom = 3
            elif hours < 24 :
                zoomtxt= "24 Hours"
                zoom = 4
            elif hours < 120 :
                zoomtxt= "5 Days"
                zoom = 5
            elif hours < 360 :
                zoomtxt= "15 Days"
                zoom = 6
            elif hours < 720 :
                zoomtxt= "1 Month"
                zoom = 7
            else :
                zoomtxt= "3 Month"
                zoom = 8
        
            self.clickElement("xpath=//div[@id='chartPanel']/div/div/div/div[4]/div/table/tbody/tr[2]/td[2]/div/div/table/tbody/tr/td/div")
            #cmd = "xpath=//div["+str(zoom)+"]/div/span"
            #self.clickElement(cmd)
            #self.clickElement(cmd)
            cmd="xpath=//span[text()='"+zoomtxt+"']"
            self.clickElement(cmd)

        # Collect all option elements from first dropdown menu starting with chartPrefix
        elements = self.findElementsByLocator("xpath=//*[@id='chartPanel']/div[1]/div/div/select[1]/option[starts-with(text(), '"+chartPrefix+"')]") 

        for element in elements:
            self.algNmspmChartScreenShot(element.text)

    ############################################################################
    ### algNmspmChartScreenShot("fileName","chartName1","chartName2")
    ###
    ###   Inputs:
    ###     fileName - name of screenshot (do not include extension)
    ###     chartName1 - chart option to be selected from first dropdown menu
    ###     chartName2 - chart option to be selected from second dropdown menu (optional)
    ###       Ex. To save a screenshot called fileName of a graph of Altitude (feet), type:
    ###         algNmspmChartScreenShot("fileName", "Altitude (feet)")
    ###       Ex. To save a screenshot called fileName of a graph of Altitude (feet) vs. Velocity (knots), type:
    ###         algNmspmChartScreenShot("fileName", "Altitude (feet)", "Velocity (knots)")
    ###
    ###   Takes a screenshot of the specified graph and saves it as fileName
    ###   Note: Can only be used after calling algNmspmSearchVMT() (navigating to "VMT Information" screen)
    ###   Note: Called by algNmspmChartScreenShots() to take multiple screenshots (fileName is autogenerated)
    ###
    ############################################################################
    def algNmspmChartScreenShot(self, fileName, chartName1=None, chartName2=None):

        # Go to Charts page if chartName specified (not necessary when called by algNmspmChartScreenShots())
        if chartName1:        
           self.clickButton("Charts")

        select1 = Select(self.findElementByLocator("tag=select"))

        # Select chartName1 if specified
        if chartName1:
            select1.select_by_visible_text(chartName1)
        # Select chartName2 if specified
        if chartName2:
            select2 = Select(self.findElementByLocator("xpath=//select[2]"))
            select2.select_by_visible_text(chartName2)
        # Otherwise select based on the fileName given (should only be used by algNmspmChartScreenShots())
        else:
            select1.select_by_visible_text(fileName)
            for ch in [' ', '(', ')', '/' ]:
                if ch in fileName:
                    fileName = fileName.replace(ch, '')

        # Wait for the graph to appear
        for i in range(0, 5):
            time.sleep(10)
            element = self.findElementByLocator("xpath=//*[@class='highcharts-loading']/div/span")
            if not element:
                break
            if element.text != "Loading..." :
                break
            if not element.is_displayed:
                break

        self.algScreenShot(fileName)

    ############################################################################
    ### algNmspmGetTrace("fileName")
    ###
    ###   Input:
    ###     fileName - name of screenshot (do not include extension)
    ###
    ###   Takes a screenshot of RL and FL on the Trace screen
    ###   Screenshots are named RL_<fileName> and FL_<fileName> respectively
    ###   Note: Can only be used after calling algNmspmSearchVMT() (navigating to "VMT Information" screen)
    ###   Note: Capabilities to close white box that pops up and covers trace have been commented out
    ###
    ############################################################################
    def algNmspmGetTrace(self, fileName):
        self.clickButton("Trace")

        self.clickElement("xpath=//label[text()='RL']/../input")
        #Use to get rid of white box on trace
        #self.clickElement("xpath=//img[@src='http://maps.gstatic.com/mapfiles/api-3/images/mapcnt6.png']/..")
        self.algScreenShot("RL_"+fileName)  

        self.clickElement("xpath=//label[text()='FL']/../input")
        #Use to get rid of white box on trace
        #self.clickElement("xpath=//img[@src='http://maps.gstatic.com/mapfiles/api-3/images/mapcnt6.png']/..")
        self.algScreenShot("FL_"+fileName)

    ############################################################################
    ### algNmspmGetFlightHistory("duration", rowNum)
    ###
    ###   Inputs:
    ###     duration - Period of time you want to look at
    ###       Current options: Past 24 Hours, Past week, Past month, Past 2 months, Past 3 months
    ###     rowNum - row number to collect data from
    ###        Note: 1 by default unless otherwise specified
    ###
    ###   Navigates to "Flight Quality Tracker" page, clicks on "Flight History", changes search duration
    ###
    ############################################################################
#### HAS NOT BEEN TESTED###FLIGHT HISTORY DOES NOT EXIST#######
    def algNmspmGetFlightHistory(self, duration, rowNum=1):
        self.clickButton("Go To")
        self.clickImage("http://192.168.136.51:8080/nmspm/nmspm/clear.cache.gif")
        self.clickElement("xpath=//span[text()='Flight Quality Tracker']")
        self.clickButton("Flight History")

        #This line probably won't work
        self.selectPulldownOption("Search since:",duration)
        flightDict = self.algNmspmFlightHistoryRow(rowNum)

        return flightDict
        
    ############################################################################
    ### algNmspmGetFlightHistoryRow(rowNum)
    ###
    ###   Input:
    ###     rowNum - row number to collect data from
    ###        Note: 1 by default unless otherwise specified
    ###       Current options: Past 24 Hours, Past week, Past month, Past 2 months, Past 3 months
    ###
    ###   Navigates to "Flight Quality Tracker" page, clicks on "Flight History", changes search duration
    ###   Note: called by algNmspmGetFlightHistory()
    ###
    ############################################################################
#### HAS NOT BEEN FULLY TESTED###FLIGHT HISTORY DOES NOT EXIST#######
    def algNmspmFlightHistoryRow(self, rowNum=1):
        headerRowLocator = "xpath=//*[@id='fqtTabsPanel']/div[2]/div/div[2]/div[3]/div/div[1]/div/table/tbody[2]/tr"  
        rowLocator = "xpath=//*[@id='fqtTabsPanel']/div[2]/div/div[2]/div[3]/div/div[2]/div[1]/table/tbody[2]/tr["+str(rowNum)+"]"

        return self.algNmspmGetRow(headerRowLocator, rowLocator)

    ############################################################################
    ### algNmspmGetRow("headerRowLocator","rowLocator")
    ###
    ###   Inputs:
    ###     headerRowLocator - Locator for row of column names
    ###     rowLocator - Locator for row you want to extract
    ###       
    ###   Sets all headers as keys and sets the row content to corresponding values
    ###   Makes a dictionary
    ###   Note: called by algNmspmGetFlightHistoryRow()
    ###
    ############################################################################
    def algNmspmGetRow(self, headerRowLocator, rowLocator):
        elements = self.findElementsByLocator(headerRowLocator+"/td/div/span")
        keys = []
        for element in elements:
            size = element.size
            width = size['width']
            # Moves the cursor to the next header to bring it into view of the webdriver
            ActionChains(self.driver).move_to_element_with_offset(element,width,0).perform()
            keys.append(element.text)
        
        elements = self.findElementsByLocator(rowLocator+"/td/div")
        values = []
        for element in elements:
            size = element.size
            width = size['width']
            # Moves the cursor to the next value to bring it into view of the webdriver
            ActionChains(self.driver).move_to_element_with_offset(element,width,0).perform()
            values.append(element.text)
        
        return dict(zip(keys,values))

