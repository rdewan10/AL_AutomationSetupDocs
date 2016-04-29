###########################################################################################
### vselenium Class
###   Derived from Selenium2.py created by //Broadband
###   collection of additional methods (extensions) expected in a ViaSat browser based GUI 
###   also improves some Selenium2 items
###
###   See //Arclight/ArcLight/AcceptanceTest/Automation/MapTesting/Docs/AL_Automation_SDD.docx
###
############################################################################################

from Selenium2 import *

class vselenium(Selenium2):

    #######################################################################################
    ### vselenium()
    ###   Instantiate the Viasat Selenium class
    ###   Sample call used in ../alg/algMain.py: vselenium.__init__(...)
    ###
    ###   Inputs:
    ###    browserType - Browser type i.e., "chrome", "firefox"
    ###    resultsDir - Path where you want to put your screenshots
    ###    pause- number of seconds to sleep when doing certain known actions needing delay
    ###
    #######################################################################################
    def __init__(self, browserType, resultsDir, pause=10):
        Selenium2.__init__(self, browserType, resultsDir, pause)

    #######################################################################################
    #######################################################################################
    ### "Fixes" to Selenium2 package
    #######################################################################################
    #######################################################################################

    #######################################################################################
    ### NOTE: Edited Selenium2.py with updated Selenium2.__init__() containing pause; 
    ###        fully backward compatable.
    #######################################################################################

    #######################################################################################
    ### connectToServer(url, titleString)
    ###   Improves existing Selenium2 method by only verifying title if specified
    ###
    ###   Inputs:
    ###    url - URL of server you want to connect to
    ###     titleString - Title of URL (can be read from tab or <title> section of <head> in source code)
    ###      Note: titleString does not need to be used, only included to replicate structure from Selenium2
    ###      Sample call: connectToServer("http://192.168.136.142:9090", "ArcLight NMS")
    ###      Sample call: connectToServer("http://192.168.136.142:9090")
    ###
    ###   Opens up new window (if first time calling connecToServer in test), goes to url, and maximizes window.
    ###   If not first time calling connectToServer, the url of the current page will change to url.
    ###   If titleString is specified, a check will be made to verify that the title matches the expected title
    ###
    #######################################################################################
    def connectToServer(self, url, titleString=None):
        self.driver.switch_to.active_element
        self.driver.get(url)
        time.sleep(self.pause)
        if titleString:
            assert titleString in self.driver.title
        self.driver.maximize_window()

    #######################################################################################
    ### disconnectFromServer(self)
    ###    Improves existing by using quit(), rather than close(), so that 
    ###    all browser driver elements are freed
    ###
    #######################################################################################
    def disconnectFromServer(self):
        self.driver.close()
        self.driver.quit()
    

    #######################################################################################
    #######################################################################################
    ### "Extensions" to Selenium2 package
    #######################################################################################
    #######################################################################################


    #######################################################################################
    ### timestamp()
    ###
    ###   Retuns a timestamp
    #######################################################################################
    def timestamp(self):
        return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S')

    #######################################################################################
    ### clickButton("TEXT")
    ###
    ###   Inputs:
    ###    TEXT - Text in source code that is displayed on button
    ###      Sample element that works: <div class="GL4UTHNCON">Add</div>
    ###      Corresponding call: clickButton("Add")
    ###
    ###   Clicks clickable element that has TEXT displayed on it.
    ###
    #######################################################################################
    def clickButton(self, TEXT):
        self.clickElement("xpath=//div[text()='" + TEXT + "']")


    #######################################################################################
    ### clickCheckbox("checkboxName", state)
    ###
    ###   Inputs:
    ###    checkboxName - Name of checkbox (must include ':' if part of name)
    ###      Sample element that works: <label for="x-widget-1-input" ... >Enabled:</label>
    ###      Corresponding call (for ON state): clickCheckbox("Enabled:", True)
    ###
    ###   Clicks checkbox with name checkboxName if necessary to get it to specified state
    ###   Locates checkbox by finding label named checkboxName, looking at its parent,
    ###    and then finding a descendant input of type checkbox
    ###
    #######################################################################################
    def clickCheckbox(self, checkboxName, state):
        box = "xpath=//label[text()='" + checkboxName + "']/..//input[@type='checkbox']"
        if state:
            if self.findElementByLocator(box).is_selected():
                pass
            else:
                self.clickElement(box)
        else:
            if self.findElementByLocator(box).is_selected():
                self.clickElement(box)
            else:
                pass

    #######################################################################################
    ### selectPulldownOption("pulldownName", "pulldownOption")
    ###
    ###   Inputs:
    ###    pulldownName - Name of pulldown (must include ':' if part of name)
    ###      Sample element that works: <label for="x-auto-6-input" ... >File Name:</label>
    ###    pulldownOption - Name of option to select from pulldown list
    ###      Sample element that works: <option value="v106.46.zip [31]">v106.46.zip [31]</option>
    ###      Corresponding call: selectPulldownOption("File Name:", "v106.46.zip [31]")
    ###
    ###   Selects pulldownOption from the pulldown list called pulldownName
    ###   Selects option by finding label named pulldownName, looking at its parent,
    ###     finding a decendant select tag, and then finding a child option named pulldownOption
    ###
    #######################################################################################
    def selectPulldownOption(self, pulldownName, pulldownOption):
        menu = "xpath=//label[text()='" + pulldownName + "']/..//select"
        self.selectMenuOption(menu, menu + "/option[text()='" + pulldownOption + "']")

    #######################################################################################
    ### selectPulldownStartsWith("pulldownName", "pulldownOption")
    ###
    ###   Inputs:
    ###    pulldownName - Same as selectPulldownOption
    ###    pulldownOption - Similar to selectPulldownOption, but can be just the beginning of the option
    ###      Sample call: selectPulldownStartsWith("File Name:", "v106.46")
    ###
    ###   Very similar to selectPulldownOption
    ###
    #######################################################################################
    def selectPulldownStartsWith(self, pulldownName, pulldownOption):
        menu = "xpath=//label[text()='" + pulldownName + "']/..//select"
        self.selectMenuOption(menu, menu + "/option[starts-with(text(), '"+ pulldownOption + "')]")

    #######################################################################################
    ### selectPulldownContains("pulldownName", "pulldownOption")
    ###
    ###   Inputs:
    ###    pulldownName - Same as selectPulldownOption
    ###    pulldownOption - Similar to selectPulldownOption, but can just be a substring of the option
    ###      Sample call: selectPulldownStartsWith("File Name:", "106.46")
    ###
    ###   Very similar to selectPulldownOption
    ###
    #######################################################################################
    def selectPulldownContains(self, pulldownName, pulldownOption):
        menu = "xpath=//label[text()='" + pulldownName + "']/..//select"
        self.selectMenuOption(menu, menu + "/option[contains(text(), '"+ pulldownOption + "')]")

    #######################################################################################
    ### chooseFile("nameLocator", "file")
    ###
    ###   Inputs:
    ###    nameLocator - name of Choose File button in source code
    ###      Sample element that works: <input type="file" name="sedFile">
    ###    file - fullpath of file to be chosen
    ###      Corresponding call: chooseFile("sedFile", "/home/arclight/Maps/sed.csv")
    ###
    ###   Selects file for any Choose File button with element name nameLocator
    ###
    #######################################################################################
    def chooseFile(self, nameLocator, file):
        element = self.findElementByLocator("name=" + nameLocator)
        element.send_keys(file)

    ######################################################################################
    ### scrollToText("text")
    ###
    ###   Inputs:
    ###    text - td text that is being scrolled to
    ###      Sample element that works: <td class="lc">GDRM File Version</td>
    ###       Corresponding call: scrollToText("GDRM File Version")
    ###
    ###   Scrolls down until the specified text is visible for a screenshot
    ###
    #######################################################################################
    def scrollToText(self, text):
        #element = self.driver.find_element_by_xpath("//td[text()='{}']".format(text))
        element = self.driver.find_element_by_xpath("//*[text()='{}']".format(text))
        self.driver.execute_script("return arguments[0].scrollIntoView();", element)

    #######################################################################################
    ### __enter__()
    ###
    ###  Used by with statements to open a URL
    ###
    #######################################################################################
    def __enter__(self):
        return self

    #######################################################################################
    ### __exit__()
    ###
    ###  Used by with statements to close a URL
    ###
    #######################################################################################
    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnectFromServer()

    #######################################################################################
    ### clickImage("imageURL")
    ###
    ###   Input:
    ###    imageURL - URL of clickable element on screen
    ###      Sample element that works: <img class="gwt-Image" src="img/navUncollapse.png" 
    ###         style="cursor: pointer; padding-left: 8px; padding-top: 8px; width: 16px; 
    ###         height: 16px; z-index: 0; position: absolute; left: 0px; top: 0px;"> 
    ###      Corresponding call: clickImage("img/navUncollapse.png")
    ###
    ###   Clicks clickable element that has TEXT displayed on it.
    ###
    #######################################################################################
    def clickImage(self, imageURL):
        self.clickElement("xpath=//img[@src='" + imageURL + "']")

