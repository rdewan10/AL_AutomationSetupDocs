CONFIG_DIR = "/var/www/html/results"
BASE_DIR = "/var/www/html/results"
RESULT_DIR = "/var/www/html/results"

mapbun = {
    'filename': 'datafile',
    'profile': 'SL-ACSM',
    'script': 'scriptReboot-1.1.0.2.sh',
    'satName': 'Viasat1',
    'bundleVersion' : '1.0'
}

nmsGui = {
    'ip': '192.168.136.142',
    'port': 9090,
    'usern': 'wolf',
    'passw': 'wolf'
}

termGui = {
    'ip': '192.168.94.1',
    'port': 80,
    'usern': 'root',
    'passw': 'saf&scur/4OH1',
    'name': 'Terminal 05 - 94.1',
    'cli' : 'SSH',
    'consolePort': 'terminal_5'
}

rtnms = {
    'ip': '192.168.142.8',
    'hubName': "TA Hub EMS",
    'usern': 'root',
    'passw': 'Viasat123'
}

hubs = {
    'hub1Name': "TA Hub EMS",
    'hub2Name': ""
}

tuningParams = {
    'precedenceDwell': 30,
    'defaultBitRate': 1000,
    'dnldBitRatePercent': 50,
    'flRxFreq': 0
}

grp = {
    'TestCase': "", 
    'Description': "",
    'StationName': ""
}

sedFile = "sed.csv.agt"
sscfFile = "sscf.csv.agt"
gdrmFile = "gdrm.txt.agt"
rlcFile = "rlc.txt.agt"

sednomd5File = "sed.csv"
sscfnomd5File = "sscf.csv"
gdrmnomd5File = "gdrm.txt"
rlcnomd5File = "rlc.txt"

precVerifyLogFn = 'mapbunPrecVerify.log'
precVerifyErrFn = 'mapbunPrecVerifyErrors.log'
termPrecLogFn = 'termPrec.log'
termFLLockFn = 'termFLLock.log'
termUploadFn = 'termUpload.log'
termTrickleFn = 'termTrickle.log'
termSyslogFn = 'termSyslog.log'
termSyslogEventFn = 'termSyslog.csv'
termSyslog0Fn = 'termSyslog0.log'
termSyslog0EventFn = 'termSyslog0.csv'
rtnms0SyslogFn = 'rtnms0Syslog.log'
rtnms0SyslogEventFn = 'rtnms0Syslog.csv'
mapTestReportFn = '/results/util/mapTestReport.txt'

matlabLibPath = "/usr/local/MATLAB/MATLAB_Compiler_Runtime/v83"


antennaNamesDict = {'1':'Rantec11.5', '2':'Rantec11.5-NarrowFit', '3': 'VR-12T', '4': 'VR-12H', '5': 'VR-12HS', 
    '6': 'VR-12Ku-HP', '7': 'VR-12Ka', '8': 'KuKarray', '10':'HMSA', '11':'KVH-V7', '12':'KVH-V3', 
    '13':'KVH-V11', '21':'Tracstar', '31':'RayStat', '51':'TECOM-KuStream-1500', '52':'TECOM-KuStream-1015'}



# Our golden config to reset to after a forwardLink
# config from our random point in china with one beam map version 106.46
# Hub config: Tx: 1828 Rx: 14240 Chiprate: 25050
# Terminal config: Lat: 33 Long: 107 Antenna: 51
baselineBin = "/var/www/cgi-bin/baseline.bin"
hubConfig_terminal_5 = {'txFreq': 18280, 'rxFreq': 124280, 'chiprate': 25050}
hubConfig_terminal_12 = {'txFreq': 20400, 'rxFreq': 126400, 'chiprate': 24000}
hubConfig_terminal_16 = {'txFreq': 18280, 'rxFreq': 124280, 'chiprate': 25050}
hubConfig = {'terminal_5': hubConfig_terminal_5, 'terminal_12': hubConfig_terminal_12, 'terminal_16': hubConfig_terminal_16}

termConfig_terminal_5 = {'path': '/test', 'logMD5': True, 'trickle': True}
#termConfig_terminal_5 = {'path': '/etc', 'logMD5': True, 'trickle': True}
termConfig_terminal_12 = {'path': '/etc', 'logMD5': True, 'trickle': True}
termConfig_terminal_16 = {'path': '/etc', 'logMD5': True, 'trickle': False}
termConfig = {'terminal_5': termConfig_terminal_5, 'terminal_12': termConfig_terminal_12, 'terminal_16': termConfig_terminal_16}

# Selenium Customizations
vselPause=8
vselPauseMap=8
vselPauseNlg=8
vselPauseNlgTerm=5

# NLG  Customizations
defNlgTimeoutTerm=60
defNlgTimeoutNmspm=90


# Spectral Inversion LBand Value (MHzX10) - Low end to get lowest Signal Generator value
specInverLband=9500

# Mixer LBand Value (MHzX10) - Hi end to get lowest Signal Generator value
maxEflmLband=21500
maxFlmLband=14500
mixerAl2Lband=maxFlmLband

# Release Versions
RELEASE_NMS_41  = int(40100007)
RELEASE_NMS_42  = int(40200010)
RELEASE_NMS_43  = int(40300000)
RELEASE_TERM_55 = int(50500017)
RELEASE_TERM_4012 = int(40001002)
RELEASE_TERM_5016 = int(50001006)
RELEASE_TERM_52027 = int(50200027)
RELEASE_TERM_5130 = int(50103000)
RELEASE_TERM_55019 = int(50500019)

