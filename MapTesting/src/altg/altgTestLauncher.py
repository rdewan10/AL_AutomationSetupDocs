#!/usr/bin/env python

from aldbConf import *
from string import Template
from cgiSetup import *
from multiprocessing import Process
import datetime, time
import os, re, subprocess
from altgScreen import testLauncher, changeGroup


launcher = testLauncher()
launcher.printScreen()
test = launcher.selectTest()
print("<br><br>")
print(test)
