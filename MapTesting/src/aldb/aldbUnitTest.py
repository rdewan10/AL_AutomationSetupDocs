from aldbConf import *
from aldbConnConfig import *

# for aldbConf
groupId = 10
try:
    test = aldbConf(groupId)
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
# Test for the MapBun Set
# Set dictionary, just change, what the fields correspond to
# in order to change the test case
setDict = dict(filename = 'test_file1', profile='profile1', script='script1', satname='viasat1')
test.aldbConfMapbunSet(**setDict)
result = test.aldbConfMapbunGet()
print(result)
print(setDict)

if cmp(result, setDict):
    print("MapBun SetNew passed")
else:
    print("MapBun SetNew failed")
test.lockGroup()
result = aldbConf.isLocked(aldbConnParmsGet(), 22)
print(result)
# updateDict = {'filename': 'test_file3', 'profile': 'profile3', \
#     'script': 'script3', 'satname':  'viasat2'}
# test.aldbConfMapbunSet(**updateDict)
# result = test.aldbConfMapbunGet()
# print(result)
# if result == updateDict:
#     print("MapBun SetUpdate passed")
# else:
#     print("MapBun SetUpdate failed")
#
# delete = "DELETE FROM MapBun WHERE groupId=%(groupId)s"
# data = {'groupId':groupId}
# test.generalSet(delete, data)
#
# # Test for the NmsGui Set
# setDict = { 'ip': '192.168.1.1', 'port': 23, 'usern': 'root', 'passw': 'viasat'}
# test.aldbConfNmsGuiSet(**setDict)
# result = test.aldbConfNmsGuiGet()
#
# if result == setDict:
#     print("NmsGui SetNew passed")
# else:
#     print("NmsGui SetNew failed")
#
# # Tests to see if the NmsGui function updates instead of inserting duplicates
# updateDict = { 'ip': '192.168.1.2', 'port': 24, 'usern': 'arclight', \
#     'passw': 'viasat123'}
# test.aldbConfNmsGuiSet(**updateDict)
# result = test.aldbConfNmsGuiGet()
#
# if result == updateDict:
#     print("NmsGui SetUpdate passed")
# else:
#     print("NmsGui SetUpdate failed")
#
# delete = "DELETE FROM NmsGui WHERE groupId=%(groupId)s"
# data = {'groupId':groupId}
# test.generalSet(delete, data)

# Test for the TermGui Set
# setDict = { 'ip': '192.168.1.2', 'port': 24, 'usern': 'arclight', \
#     'passw': 'viasat123', 'name': 'germantown', 'cli': 'SSH', 'consolePort': 'terminal_4'}
# test.aldbConfTermGuiSet(**setDict)
# result = test.aldbConfTermGuiGet()

# if result == setDict:
#     print("TermGui SetNew pased")
# else:
#     print("TermGui SetNew failed")
#
# delete = "DELETE FROM TermGui WHERE groupId=%(groupId)s"
# data = {'groupId':groupId}
# test.generalSet(delete, data)

# Tests to see if the TermGui function updates instead of inserting duplicates
# updateDict = { 'ip': '192.168.1.3', 'port': 30, 'usern': 'arclight', \
#     'passw': 'viasat', 'name': 'carlsbad', 'cli': 'Console',
#     'consolePort': 'terminal_4'}
# test.aldbConfTermGuiSet(**updateDict)
# result = test.aldbConfTermGuiGet()
#
# if result == updateDict:
#     print("TermGui SetUpdate passed")
# else:
#     print("TermGui SetUpdate failed")
#
# # Test for the MapBunDetailed Set
# setDict = { 'sedVersion': '2.3' , 'sscfVersion': '3.5', 'rlcVersion': '4.2',
#     'gdrmVersion': '6.7' }
# test.aldbConfMapbunDetailedSet(True, '2.3', '3.5', '4.2', '6.7')
# result = test.aldbConfMapbunDetailedGet()
#
# if result == setDict:
#     print("MapBunDetailed SetNew pased")
# else:
#     print("MapBunDetailed SetNew failed")
#
# # Test for the MapBunDetailed to see if it update the values instead of
# # inserting duplicates
# updateDict = { 'sedVersion': '2.3' , 'sscfVersion': '3.5', 'rlcVersion': '4.2',
#     'gdrmVersion': None }
# test.aldbConfMapbunDetailedSet(True, '2.3', '3.5', '4.2', None)
# result = test.aldbConfMapbunDetailedGet()
#
# if result == updateDict:
#     print("MapBunDetailed SetUpdate pased")
# else:
#     print("MapBunDetailed SetUpdate failed")
#
# delete = "DELETE FROM MapBunDetailed WHERE groupId=%(groupId)s"
# data = {'groupId':groupId}
# test.generalSet(delete, data)
#
# # Test for the ConfDirs
# setDict = {'baseDir': '/home/arlcight', 'configDir': '/home/arclight/config',
#     'resultDir': '/home/arclight/results'}
# test.aldbConfDirsSet(**setDict)
# result = test.aldbConfDirsGet()
#
# if result == setDict:
#     print("ConfDirs SetNew passed")
# else:
#     print("ConfDirs SetNew failed")
#
# updateDict = {'baseDir': '/arlcight', 'configDir': '/arclight/config',
#     'resultDir': None }
# test.aldbConfDirsSet(**updateDict)
# result = test.aldbConfDirsGet()
#
# if result == updateDict:
#     print("ConfDirs SetUpdate passed")
# else:
#     print("ConfDirs SetUpdate failed")
#
# delete = "DELETE FROM ConfDirs WHERE groupId=%(groupId)s"
# data = {'groupId':groupId}
# test.generalSet(delete, data)
#
# # Test for the TuningConf
# setDict = {'precedenceDur': 500, 'precedenceDwell': 30}
# test.aldbTuningConfSet(**setDict)
# result = test.aldbTuningConfGet()
#
# if result == setDict:
#     print("TuningConf SetNew passed")
# else:
#     print("TuningConf SetNew failed")
#
# updateDict = {'precedenceDur': 200, 'precedenceDwell': 15}
# test.aldbTuningConfSet(**updateDict)
# result = test.aldbTuningConfGet()
#
# if result == updateDict:
#     print("TuningConf SetUpdate passed")
# else:
#     print("TuningConf SetUpdate failed")
#
# delete = "DELETE FROM TuningConf WHERE groupId=%(groupId)s"
# data = {'groupId':groupId}
# test.generalSet(delete, data)

#
# test.aldbConfMapbunDetailedSet(True, '100.43.0', '106.46.0', None, None, 'aldsgjalkjkjae',
#     'adslkjgkw', None, None, 'Name', 42, 5000, 2000, 12, 51)
#
# get = test.aldbConfMapbunDetailedGet()
# print(get)
#
# if get['gdrmVersion']:
#     print("Not None")
# else:
#     print("Was None")
