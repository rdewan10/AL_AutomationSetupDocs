#!/usr/bin/env python
# from selenium import webdriver
# from pyvirtualdisplay import Display
from mapbunMain import *
import cgiSetup, os


# display = Display(visible=False, size=(800,600))
# display.start()
#
# browser = webdriver.Chrome()
# browser.get("http://google.com")

map = mapbun(6)
map.mapbunConf()
#print(map.mapbunUpload(1))
print("Content-type: text/html\n\n")
#print(map.mapbunUpload(1))
#print(map.mapbunTrickle(1))
#map.mapbunFLLock(1)
# print(browser.title)
# print(os.environ)
#
# display.stop()
# termVerStatus = self.term.algTermStatusVersion()
# if termVerStatus['sedVersion'] == self.termMapverConf['sedVersion'] \
    # and termVerStatus['sscfVersion'] == self.termMapverConf['sscfVersion'] \
    # and termVerStatus['rlcVersion'] == self.termMapverConf['rlcVersion'] \
    # and termVerStatus['gdrmVersion'] == self.termMapverConf['gdrmVersion']:
    # result = "PASSED"
# else:
    # result = "FAILED"
# print(result)

# Test the mapbunPrecedence sub-features
#print (map.mapbunPrecedenceVerify('/home/arclight/test/install/www/cgi-bin/results/4/coords_precname_v106.46.csv', '/home/arclight/test/install/www/cgi-bin/results/4/testvecBAD_v106.46.csv', '/home/arclight/test/install/www/cgi-bin/results/4/verify_error.log'))

