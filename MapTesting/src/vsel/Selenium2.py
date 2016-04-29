#---------------------------------------------------------------
#
# File:  Selenium2.py
#
# Classification:  UNCLASSIFIED
#
# Copyright (C) 2013 ViaSat, Inc.
#
# All rights reserved.
# The information in this software is subject to change without notice and
# should not be construed as a commitment by ViaSat, Inc.
#
# ViaSat Proprietary
# The information provided herein is proprietary to ViaSat and
# must be protected from further distribution and use. Disclosure to others,
# use or copying without express written authorization of ViaSat, is strictly
# prohibited.
#
#---------------------------------------------------------------

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import MoveTargetOutOfBoundsException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
import time
import sys
import os

class Selenium2:
    driver = None

    def __init__(self, browserType, testResultsDir, pause=10):
	self.pause = pause
        if browserType == "firefox":
            downloadDir = testResultsDir + "/downloads"
            try:
                os.mkdir(downloadDir)
            except OSError:
                pass
            fp = webdriver.FirefoxProfile()
            fp.set_preference("browser.download.folderList",2)
            fp.set_preference("browser.download.manager.showWhenStarting",False)
            fp.set_preference("browser.download.dir", downloadDir)
            fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/ms-excel")
            self.driver = webdriver.Firefox(firefox_profile=fp)
        elif browserType == "chrome":
           self.driver = webdriver.Chrome()
        else:
            assert 0, "Browser type is not supported"

    def findElementByLocator (self, locator):
        element = False
        locatorType = locator[:locator.find("=")]
        if locatorType == "":
            #assert 0, "No locator type specified"
            return element
        locatorValue = locator[locator.find("=") + 1:]
        try:
            if locatorType == 'xpath':
                element = self.driver.find_element_by_xpath(locatorValue)
            elif locatorType == 'css':
                element = self.driver.find_element_by_css_selector(locatorValue)
            elif locatorType == 'id':
                element = self.driver.find_element_by_id(locatorValue)
            elif locatorType == 'name':
                element = self.driver.find_element_by_name(locatorValue)
            elif locatorType == 'link':
                element = self.driver.find_element_by_link_text(locatorValue)
            elif locatorType == 'partlink':
                element = self.driver.find_element_by_partial_link_text(locatorValue)
            elif locatorType == 'tag':
                element = self.driver.find_element_by_tag_name(locatorValue)
            elif locatorType == 'class':
                element = self.driver.find_element_by_class_name(locatorValue)
            else:
                #assert 0, "Specified locator type not supported"
                pass
        except NoSuchElementException:
            #assert 0, "Can't find specified element"
            pass
        return element

    def findClickableElement (self, locator):
        element = False
        locatorType = locator[:locator.find("=")]
        if locatorType == "":
            #assert 0, "No locator type specified"
            return element
        locatorValue = locator[locator.find("=") + 1:]
        
        wait = WebDriverWait(self.driver, 10)

        try:
            if locatorType == 'xpath':
                element = wait.until(EC.element_to_be_clickable((By.XPATH, locatorValue)))
            elif locatorType == 'css':
                element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, locatorValue)))
            elif locatorType == 'id':
                element = wait.until(EC.element_to_be_clickable((By.ID, locatorValue)))
            elif locatorType == 'name':
                element = wait.until(EC.element_to_be_clickable((By.NAME, locatorValue)))
            elif locatorType == 'link':
                element = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, locatorValue)))
            elif locatorType == 'partlink':
                element = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, locatorValue)))
            elif locatorType == 'tag':
                element = wait.until(EC.element_to_be_clickable((By.TAG_NAME, locatorValue)))
            elif locatorType == 'class':
                element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, locatorValue)))
            else:
                #assert 0, "Specified locator type not supported"
                pass
        except:
            #assert 0, "Can't find specified element"
            pass
        return element

    def clickElement (self, locator):
        element = False
        element = self.findClickableElement(locator)
        if element != False:
            try:
                element.location_once_scrolled_into_view
                actionChains = ActionChains(self.driver)
                actionChains.click(element).perform()
                time.sleep(self.pause)
                try: 
                    alert = self.driver.switch_to_alert()
                    alert.dismiss()
                except:
                    pass
            except:
                return 0
            return 1
        else:
            return 0

    def doubleClickElement (self, locator):
        element = False
        element = self.findClickableElement(locator)
        if element != False:
            try:
                element.location_once_scrolled_into_view
                actionChains = ActionChains(self.driver)
                actionChains.double_click(element).perform()
                time.sleep(self.pause) 
                try: 
                    alert = self.driver.switch_to_alert()
                    alert.dismiss()
                except:
                    pass
                return 1
            except MoveTargetOutOfBoundsException:
                return 0
            except ElementNotVisibleException:
                return 0
        else:
            return 0

    def isElementPresent(self, locator):
        element = False
        element = self.findElementByLocator(locator)
        if element != False:
            element.location_once_scrolled_into_view
            return 1
        else:
            return 0

    def isTextPresent(self, text):
        if str(text) in self.driver.page_source:
            return 1
        else:
            return 0

    def connectToServer(self, url, titleString):
        # Load  main page
        self.driver.get(url)
        time.sleep(self.pause)
        assert titleString in self.driver.title
        self.driver.maximize_window()

    def saveScreenshot(self, filename):
        self.driver.get_screenshot_as_file(filename)

    def disconnectFromServer(self):
        self.driver.close()

    def searchByText(self, locator, searchString):
        element = False
        element = self.findElementByLocator(locator)
        if element != False:
            element.clear()
            element.send_keys(searchString)
            element.send_keys(Keys.RETURN)
            time.sleep(self.pause) 
            return 1
        else:
            return 0

    def closeOpenedTabs(self):
        closeElements = self.driver.find_elements_by_xpath("//img[contains(@src,'close.png')]")  
        for element in closeElements:
            try:
                actionChains = ActionChains(self.driver)
                actionChains.click(element).perform()
            except MoveTargetOutOfBoundsException:
                pass

    def setTextField(self, locator, textString):
        element = False
        element = self.findElementByLocator(locator)
        if element != False:
            element.clear()
            element.send_keys(textString)
            return 1
        else:
            return 0

    def submitForm(self, locator):
        element = False
        element = self.findElementByLocator(locator)
        if element != False:
            try:
                element.submit()
                time.sleep(self.pause)
                return 1
            except NoSuchElementException:
                return 0
        else:
            return 0

    def selectMenuOption(self, menuLocator, optionLocator):
        menuElement = False
        menuElement = self.findClickableElement(menuLocator)
        if menuElement != False:
            try:
                menuElement.click()
                optionElement = self.findElementByLocator(optionLocator)
                optionElement.click()
                return 1
            except:
                return 0
        else:
            return 0

    def isTextPresentInTextField(self, locator, textString):
        element = False
        element = self.findElementByLocator(locator)
        if element != False:
            element.location_once_scrolled_into_view
            if str(textString) in element.get_attribute("value"):
                return 1
            else:
                return 0
        else:
            return 0

    def findElementsByLocator (self, locator):
        elements = {}
        locatorType = locator[:locator.find("=")]
        if locatorType == "":
            #assert 0, "No locator type specified"
            return elements
        locatorValue = locator[locator.find("=") + 1:]
        try:
            if locatorType == 'xpath':
                elements = self.driver.find_elements_by_xpath(locatorValue)
            elif locatorType == 'css':
                elements = self.driver.find_elements_by_css_selector(locatorValue)
            elif locatorType == 'id':
                elements = self.driver.find_elements_by_id(locatorValue)
            elif locatorType == 'name':
                elements = self.driver.find_elements_by_name(locatorValue)
            elif locatorType == 'link':
                elements = self.driver.find_elements_by_link_text(locatorValue)
            elif locatorType == 'partlink':
                elements = self.driver.find_elements_by_partial_link_text(locatorValue)
            elif locatorType == 'tag':
                elements = self.driver.find_elements_by_tag_name(locatorValue)
            elif locatorType == 'class':
                elements = self.driver.find_elements_by_class_name(locatorValue)
            else:
                #assert 0, "Specified locator type not supported"
                pass
        except NoSuchElementException:
            #assert 0, "Can't find specified element"
            pass
        return elements

    def clickElementFromList(self, commonLocator, position):
        elements = self.findElementsByLocator(commonLocator)  
        if len(elements) != 0:
            try:
                actionChains = ActionChains(self.driver)
                actionChains.click(elements[position]).perform()
                return 1
            except:
                return 0
        else:
            return 0


