#!/usr/bin/env python
from altgScreen import confScreen, changeGroup
from aldbConf import *

data = changeGroup()
screen = confScreen(aldbConf(data['groupId']), data['form'])
screen.resetConf()
screen.printScreen()
