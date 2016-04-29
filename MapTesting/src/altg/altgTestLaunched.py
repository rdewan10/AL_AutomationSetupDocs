#!/usr/bin/env python

from aldbConf import *
from alamMain import *
from altgEnv import setEnv
import sys, ast

setEnv()

sys.stdout.flush()
groupId = int(sys.argv[1])
tests = (sys.argv[2])
conf = aldbConf(groupId)
conf.lockGroup()
test = alam(groupId)

# TestId needs to be corrected, currently it is fixed to 1
if tests:

    # Create a list and convert to a dictionary of  alam parameters
    try: 
        tests.index('[')
    except:
        tests = "['"+tests+"']"
    testList = ast.literal_eval(tests)
    testDict = {}
    for key in testList:
        testDict[key] = True

    test.alamTestStart(testId=1, **testDict)
