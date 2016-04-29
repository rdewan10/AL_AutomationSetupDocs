#!/usr/bin/env python
from altgScreen import confScreen, changeGroup
from aldbConf import *
from alamMain import alam
import datetime, time, subprocess, sys

data = changeGroup()
conf = aldbConf(data['groupId'])

screen = confScreen(conf, data['form'])
screen.printScreen()

# subprocess.call(["./testLauncher.sh {} {} >>{} 2>&1  &".format(data['groupId'], None, None)], shell=True)

resultDir = conf.aldbConfDirsGet()['resultDir']
results = open("{}results".format(resultDir), "a+")
results.write("Results from Configuration Lock on {}\n".format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))
results.flush()
oldstdout = sys.stdout
sys.stdout = results

conf.lockGroup()
test = alam(data['groupId'], lock=True)

sys.stdout.flush()
sys.stdout = oldstdout
print "Locked\n"
