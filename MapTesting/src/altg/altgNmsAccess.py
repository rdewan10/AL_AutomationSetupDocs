#!/usr/bin/env python
from aldbConf import *
from altgScreen import confScreen, changeGroup

data = changeGroup()
screen = confScreen(aldbConf(data['groupId']), data['form'])
screen.nmsAccessChange()
screen.printScreen(screen.makeSubDict())
