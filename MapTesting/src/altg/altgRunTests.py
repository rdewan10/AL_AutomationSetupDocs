#!/usr/bin/env python

from altgScreen import makeGroupList
from aldbConf import *
import sys, re, datetime, time, subprocess

groupIds = sys.argv[1]
groupList = makeGroupList(groupIds)

testList = sys.argv[2]

for i in groupList:
    groupId = "{}".format(i)
    args = [groupId, testList]
    resultDir = aldbConf(groupId).aldbConfDirsGet()['resultDir']
    results = open("{}results".format(resultDir), "a+")
    results.write("Results from {} test on {}\n".format(testList, datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))
    results.flush()
    cmd = ['/var/www/cgi-bin/altgTestLaunched.py {} \"{}\" >>{} 2>&1'.format(groupId, testList, results.name)]
    #print cmd
    subprocess.call(cmd, shell=True)
    results.close()
    time.sleep(15)
