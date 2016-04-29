#!/usr/bin/env python 

from viasatMysql import vMysql

mysql = vMysql('arclight', 'viasat', 'performance')

groupId=536

result=mysql.getTable('GroupInfo', ['TestCase', 'Description', 'Station'], extraConstraint="WHERE GrpID="+str(groupId))
print("Record BEFORE write is: {}\n".format(result[0]))

setDict = dict( TestCase='T-case', Description='D-crypt-N', Station='stay-shun' )

mysql.updateTable('GroupInfo', setDict, whereDict=dict(GrpID=groupId) )

result=mysql.getTable('GroupInfo', ['TestCase', 'Description', 'Station'], extraConstraint="WHERE GrpID="+str(groupId))
print("Record AFTER write is: {}\n".format(result[0]))

mysql.close()
