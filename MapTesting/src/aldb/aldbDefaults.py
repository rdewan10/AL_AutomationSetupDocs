CONFIG_DIR = "/var/www/html/results"
BASE_DIR = "/var/www/html/results"
RESULT_DIR = "/var/www/html/results"

mapbun = {
    'filename': 'datafile',
    'profile': 'SL-ACSM',
    'script': 'scriptReboot-1.0.0.3.sh',
    'satName': 'Viasat1',
    'bundleVersion' : '1.0'
}

nmsGui = {
    'ip': '192.168.111.254',
    'port': 9090,
    'usern': 'altest',
    'passw': 'viasat123'
}

termGui = {
    'ip': '192.168.111.254',
    'port': 80,
    'usern': 'altest',
    'passw': 'viasat123',
    'name': 'Terminal 04 - 82.1',
    'cli' : 'SSH',
    'consolePort': 'terminal_4'
}

tuningParams = {
    'precedenceDwell': 60,
    'defaultBitRate': 1000,
    'dnldBitRatePercent': 50,
    'hubName': 'TA Hub EMS',
    'flRxFreq': 0
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

matlabLibPath = "/usr/local/MATLAB/MATLAB_Compiler_Runtime/v83"
stationName = "Arclight_TA"


# Our golden config to reset to after a forwardLink
# config from our random point in china with one beam map version 106.46
# Hub config: Tx: 1828 Rx: 14240 Chiprate: 25050
# Terminal config: Lat: 33 Long: 107 Antenna: 51
baselineBin = "/var/www/cgi-bin/baseline.bin"
hubConfig = {'txFreq': 1828, 'rxFreq': 12428, 'chiprate': 25050}
