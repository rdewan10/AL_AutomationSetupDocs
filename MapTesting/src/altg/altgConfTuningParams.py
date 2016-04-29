#!/usr/bin/env python
from aldbConf import *
from altgScreen import confTuningScreen, changeGroup

data = changeGroup()
screen = confTuningScreen(aldbConf(data['groupId']), data['form'])
screen.tuningChange()
screen.makeSubDict()
screen.printScreen()
