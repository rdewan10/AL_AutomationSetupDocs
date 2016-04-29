#!/usr/bin/env python
from aldbConf import *
from altgScreen import dbExportScreen, changeGroup

data = changeGroup()
screen = dbExportScreen(aldbConf(data['groupId']), data['form'])
screen.printScreen()

