from redaConfig import *
from datetime import datetime
from viasatMysql import vMysql
import mysql.connector

class redaLib(vMysql):

    def __init__(self, deleteDbLog):
        self.id = {'user':dbLogin, 'password':dbPass, 'database':dbName,
            'host':dbIp, 'port': dbPort}
        vMysql.__init__(self, **self.id)

        self.grabLastInsert = "ORDER BY GrpID DESC LIMIT 1"
        if deleteDbLog:
            pass

    def addGroup(self, groupId, groupName, testStation, description):
        now = datetime.utcnow()
        setDict = dict(Datetime=now, StationName=testStation, TestCase=groupName, Description=description, GrpID=groupId)
        self.setTable('GroupInfo', setDict)
        groupId = self.getTable('GroupInfo', ['GrpID'], extraConstraint=self.grabLastInsert)[0]['GrpID']
        return groupId

    def updateGroupConfig(self, groupId, setDict={}):
        ###self.updateTable('GroupInfo', setDict, whereDict=dict(GrpID=groupId) )
        now = datetime.utcnow()
        setDict.update(dict(Datetime=now))
        updDict = setDict.copy()
        setDict.update(dict(GrpID=groupId))
        self.setTable('GroupInfo', setDict, updDict)
        return groupId

    def addTest(self, grpid, testName, status):
        now = datetime.utcnow()
        setDict = dict(GrpID=grpid, Status=status, Datetime=now)
        self.setTable('TestInfo', setDict)
        testId = self.reda.getTable('TestInfo', ['TestID'],  extraConstraint=self.grabLastInsert)[0]['TestID']
        return testId

    # def updateTestConfig(self, grpid, tstid, fields):
    #     generalUpdate(grpid, fields, tstid)
    # def updateTestResult(self, grpid, tstid, fields):
    #
    #
    # def getTestSpecPassFail(self, grpId):
    # def getGroupNames(self):
    # def getTestNames(self):
    # def addGroupName(self, gName):
