from __future__ import print_function
from datetime import date, datetime, timedelta
from alDefaults import *
from viasatMysql import vMysql
from RedaLibrary import redaLib
from aldbConnConfig import *
import mysql.connector, os, copy, csv


#############################################################################
# Gets the Parameters for the mysql connection from the aldbConnConfig files
# and puts them into a dictionary which is then used to make the conneciton
#############################################################################
def aldbConnParmsGet():
    return {'user':dbuser, 'password':dbpassw, 'database':dbname,
        'host':dbhostname, 'port': dbportnum}

#############################################################################
# aldbConf Class 
# Currently derived from redaLib->vMysql
# redaLib defines self.id to the same dictionary as aldbConnParmsGet(), so
#   need to fix/resolve 
#############################################################################
class aldbConf(redaLib):

    def __init__(self, groupId = None):
        redaLib.__init__(self, False)
        if groupId:
            self.groupId = groupId
            self.locked = aldbConf.isLocked(self.id, groupId)
        else:
            self.groupId = aldbConf.getGroup(self.id, False)
            self.locked = False
        cmd = "mkdir" + " -p " + CONFIG_DIR + "/" + str(self.groupId)
        os.system(cmd)


    ############################################################################
    # Queries the database to see if the given group is already locked
    ############################################################################
    @staticmethod
    def isLocked(connParms, groupId):
        mysql = vMysql(**connParms)
        result = mysql.getTable("GroupInfo", ["GrpID"], dict(GrpID=groupId))
        if result:
            return True
        else:
            return False

    ############################################################################
    # Gets the next unlocked groupId from the mysql database, pass a boolean for
    # isLocked, if false it will get the next unlocked group, if true it will
    # get the latest locked group
    ############################################################################
    @staticmethod
    def getGroup(connParms, isLocked):
        mysql = vMysql(**connParms)
        result  = mysql.getTable("GroupInfo", ["GrpID"], None, "ORDER BY GrpID DESC LIMIT 1")
        if result and isLocked:
            return result[0]['GrpID']
        elif result:
            return result[0]['GrpID'] + 1
        elif not(isLocked):
            return 0
        else:
            return 1

    ############################################################################
    # Locks the group, so it cannot be altered in any table
    ############################################################################
    def lockGroup(self):
        if not(aldbConf.isLocked(self.id, self.groupId)):
            #reda = redaLib(False)
            mapbun = self.aldbConfMapbunGet()
            nms = self.aldbConfNmsGuiGet()
            term = self.aldbConfTermGuiGet()
            hubs = self.aldbConfHubsGet()
            if nms['ip'] == "192.168.136.142":
                summ = "{}_{}".format(mapbun['bundleVersion'], mapbun['satName'])
                description = "Map Bundle Version:{} Beam:{} NMS/EMS IP:{} Terminal IP:{}".format(mapbun['bundleVersion'], mapbun['satName'], nms['ip'], term['ip'])
                station="{}_MAP".format(term['consolePort'])
            elif nms['ip'] == "192.168.136.35":
                summ = "{}".format(term['consolePort'])
                description = "NMS/EMS IP:{} {} IP:{}".format(mapbun['bundleVersion'], mapbun['satName'], nms['ip'], term['consolePort'], term['ip'])
                station="{}".format(term['consolePort'])
            else:
                summ = "{}".format(term['consolePort'])
                description = "NMS/EMS IP:{} {} IP:{}".format(mapbun['bundleVersion'], mapbun['satName'], nms['ip'], term['consolePort'], term['ip'])
                station="{}".format(term['consolePort'])

            self.addGroup(self.groupId, "{}".format(summ), station, description)

    ############################################################################
    # generalSet() is used by all the other set methods, just pass in the
    # statement that you want mysql to execute and the parmeters (variables)
    # that are needed by that statement, ex: using %(name)s , you would put
    # name in params like {'name': 'bob'}
    ############################################################################
    def generalSet(self, tableName, setDict, detailed):
        #if not(self.locked) or detailed:
            updateDict = copy.deepcopy(setDict)
            updateDict.pop('groupId', None)
            self.setTable(tableName, setDict, updateDict)

    ############################################################################
    # generalGet() is used by all the other get methods, just pass in the
    # statement that you want myslq to execute and it will return the row
    # as a dictionary, with the each key being its corresponding column name
    ############################################################################
    def generalGet(self, tableName, getDict, default):
        result = self.getTable(tableName, getDict, dict(groupId=self.groupId))
        if len(result):
            return result[0]
        else:
            return default

    ############################################################################
    # Sets the Map Bundle configuration in the database
    ############################################################################
    def aldbConfMapbunSet(self, filename=mapbun['filename'],
        profile=mapbun['profile'],script=mapbun['script'],
        satname=mapbun['satName'], bundleVersion=mapbun['bundleVersion']):

        data_mapbun_conf = {'groupId' : self.groupId, 'filename': filename, 'profile': profile, 'script': script, 'satname': satname, 'bundleVersion' : bundleVersion}

        self.generalSet('MapBun', data_mapbun_conf, False)

    ############################################################################
    # Gets and returns the Map Bundle configuration from the database
    # Converts the list of the satellite(beam) names from pure text form,
    # the way they are stored in the db, to an array of names
    ############################################################################
    def aldbConfMapbunGet(self):
        return self.generalGet('MapBun', ['filename', 'profile', 'script', 'satName', 'bundleVersion'], mapbun)

    ############################################################################
    # Sets the configuration for the NMS/EMS Gui in the database
    ############################################################################
    def aldbConfNmsGuiSet(self, ip=nmsGui['ip'], port=nmsGui['port'],
        usern=nmsGui['usern'], passw=nmsGui['passw']):
        data_NmsGui = {
                'groupId': self.groupId,
                'ip': ip,
                'port': port,
                'usern': usern,
                'passw': passw,
        }
        self.generalSet('NmsGui', data_NmsGui, False)

    ############################################################################
    # Gets and returns the configuration for the NMS/EMS Gui form the database
    ############################################################################
    def aldbConfNmsGuiGet(self):
        return self.generalGet('NmsGui', ['ip', 'port', 'usern', 'passw'], nmsGui)

    ############################################################################
    # Sets the configuaration for the Terminal Gui in the database
    ############################################################################
    def aldbConfTermGuiSet(self, ip=termGui['ip'], port=termGui['port'],
        usern=termGui['usern'], passw=termGui['passw'], name=termGui['name'],
        cli=termGui['cli'], consolePort=termGui['consolePort']):
        data_TermGui = {
            'groupId': self.groupId,
            'ip': ip,
            'port': port,
            'usern': usern,
            'passw': passw,
            'name': name,
            'cli' : cli,
            'consolePort': consolePort
        }
        self.generalSet('TermGui', data_TermGui, False)

    ############################################################################
    # Gets the configuration for the Terminal Gui from the database
    ############################################################################
    def aldbConfTermGuiGet(self):
        getList = ['ip', 'port', 'usern', 'passw', 'name', 'cli', 'consolePort']
        return self.generalGet('TermGui', getList , termGui)


    ############################################################################
    # Sets the configuration for the Hubs in the database
    ############################################################################
    def aldbConfHubsSet(self, hubname1=hubs['hub1Name'], hubname2=hubs['hub2Name']):
        data_Hubs = {
                'groupId': self.groupId,
                'hub1Name': hubname1,
                'hub2Name': hubname2,
        }
        self.generalSet('Hubs', data_Hubs, False)

    ############################################################################
    # Gets and returns the configuration for the NMS/EMS Gui form the database
    ############################################################################
    def aldbConfHubsGet(self):
        return self.generalGet('Hubs', ['hub1Name', 'hub2Name'], hubs)

    ############################################################################
    # Sets the configuration for the Map Bundle details in the database. Note
    # that 'signed' is a boolean so just use True or False
    ############################################################################
    def aldbConfMapbunDetailedSet(self, signed, sedVersion, sscfVersion, rlcVersion, gdrmVersion, sedmd5, sscfmd5, rlcmd5, gdrmmd5, satName, satId, flTxFreq, flRxFreq, flChipRate, antennaType, satLong, polarity, pilot, rolloff):
        data_mapbun_detailed = {
            'groupId': self.groupId, 'signed': signed, 'sedVersion': sedVersion, 'sscfVersion': sscfVersion, 'rlcVersion': rlcVersion, 'gdrmVersion': gdrmVersion, 'sedmd5': sedmd5, 'sscfmd5': sscfmd5, 'rlcmd5': rlcmd5, 'gdrmmd5': gdrmmd5, 'satName': satName, 'satId': satId, 'flTxFreq': flTxFreq, 'flRxFreq' : flRxFreq, 'flChipRate': flChipRate, 'antennaType': antennaType, 'satLong': satLong, 'polarity': polarity, 'pilot':pilot, 'rolloff':rolloff }
        self.generalSet('MapBunDetailed', data_mapbun_detailed, True)

    ############################################################################
    # Gets the configuration for the map Bundle details form the database
    ############################################################################
    def aldbConfMapbunDetailedGet(self):
        default = {

        }
        getList = ['signed', 'sedVersion', 'sscfVersion', 'rlcVersion', 'gdrmVersion', 'sedmd5', 'gdrmmd5', 'sscfmd5', 'rlcmd5', 'satName', 'satId', 'flTxFreq', 'flRxFreq', 'flChipRate', 'antennaType', 'satLong', 'polarity', 'pilot', 'rolloff']
        return self.generalGet('MapBunDetailed', getList, default)


    ############################################################################
    # Gets the directories for the files based on the groupId, these directories
    # are calculated during init and never saved in the database
    ############################################################################
    def aldbConfDirsGet(self):
        groupFolder = "/" + str(self.groupId) + "/"
        return {'groupId':self.groupId, 'baseDir': BASE_DIR + groupFolder,
            'resultDir': RESULT_DIR + groupFolder,
            'configDir': CONFIG_DIR + groupFolder }

    ############################################################################
    # Sets the tuning configuaration parameters in the database
    ############################################################################
    def aldbTuningConfSet(self, precedenceDwell=tuningParams['precedenceDwell'], defbitrate=tuningParams['defaultBitRate'],
        dnldBitRatePercent=tuningParams['dnldBitRatePercent'], flrxfreq=tuningParams['flRxFreq']):

        tuning_data = {'groupId': self.groupId, 'precedenceDwell': precedenceDwell, 'defaultBitRate': defbitrate,
            'dnldBitRatePercent': dnldBitRatePercent, 'flRxFreq':flrxfreq }
        #self.generalSet('TuningConf', tuning_data, False)
        self.generalSet('TuningConf', tuning_data, True)

    ############################################################################
    # Gets the tuning configuration parameters from the database
    ############################################################################
    def aldbTuningConfGet(self):
        getList = ['precedenceDwell', 'defaultBitRate', 'dnldBitRatePercent', 'flRxFreq']
        return self.generalGet('TuningConf', getList, tuningParams)


    ############################################################################
    # Sets the NmsPm VMT List Item Status in the database
    ############################################################################
    def aldbStatusNmspmVmtlistSet(self, pollTime, 
        VL_RLWaveformType='',
        VL_RLCRMAModcodebps='',
        VL_FTI='',
        VL_FLEsNodB='',
        VL_Status='',
        VL_FLACSMModcode='',
        VL_LastLogin='',
        VL_FLACSMAdaptation='',
        VL_RLCRLModcode='',
        VL_RLCRLEsNodB='',
        VL_Longitude='',
        VL_Latitude='',
        VL_SEDVersion='',
        VL_LastActiveatHub='',
        VL_VMTName='',
        VL_BandwidthClass='',
        VL_SSCFVersion='',
        VL_RLCurrentCRLAdaptation='',
        VL_FLName='',
        VL_AntennaType='',
        VL_ModemType='',
        VL_SWVersion='',
        VL_RLCurrentCRMAAdaptation='',
        VL_RLName='',
        VL_RLCRMAEbNodB='',
        VL_RLAttenSetdB='',
        **kwargs):
            
        data_nmspm_vmtlist = {'groupId' : self.groupId, 'pollTime': pollTime, 
            'VL_RLWaveformType': VL_RLWaveformType,
            'VL_RLCRMAModcodebps': VL_RLCRMAModcodebps,
            'VL_FTI': VL_FTI,
            'VL_FLEsNodB': VL_FLEsNodB,
            'VL_Status': VL_Status,
            'VL_FLACSMModcode': VL_FLACSMModcode,
            'VL_LastLogin': VL_LastLogin,
            'VL_FLACSMAdaptation': VL_FLACSMAdaptation,
            'VL_RLCRLModcode': VL_RLCRLModcode,
            'VL_RLCRLEsNodB': VL_RLCRLEsNodB,
            'VL_Longitude': VL_Longitude,
            'VL_Latitude': VL_Latitude,
            'VL_SEDVersion': VL_SEDVersion,
            'VL_LastActiveatHub': VL_LastActiveatHub,
            'VL_VMTName': VL_VMTName,
            'VL_BandwidthClass': VL_BandwidthClass,
            'VL_SSCFVersion': VL_SSCFVersion,
            'VL_RLCurrentCRLAdaptation': VL_RLCurrentCRLAdaptation,
            'VL_FLName': VL_FLName,
            'VL_AntennaType': VL_AntennaType,
            'VL_ModemType': VL_ModemType,
            'VL_SWVersion': VL_SWVersion,
            'VL_RLCurrentCRMAAdaptation': VL_RLCurrentCRMAAdaptation,
            'VL_RLName': VL_RLName,
            'VL_RLCRMAEbNodB': VL_RLCRMAEbNodB,
            'VL_RLAttenSetdB': VL_RLAttenSetdB
            }

        self.generalSet('NmsPmVmtStatus', data_nmspm_vmtlist, False)

        if len(kwargs):
            print ("\nWarning: Detected new NMSPM VMT List paramters [{}]\n".format(kwargs))

    ############################################################################
    # Gets and returns the VMT VMT List Item Status from the database
    ############################################################################
    def aldbStatusNmspmVmtlistGet(self):
        return self.generalGet('NmsPmVmtStatus', ['pollTime', 
            'VL_RLWaveformType',
            'VL_RLCRMAModcodebps',
            'VL_FTI',
            'VL_FLEsNodB',
            'VL_Status',
            'VL_FLACSMModcode',
            'VL_LastLogin',
            'VL_FLACSMAdaptation',
            'VL_RLCRLModcode',
            'VL_RLCRLEsNodB',
            'VL_Longitude',
            'VL_Latitude',
            'VL_SEDVersion',
            'VL_LastActiveatHub',
            'VL_VMTName',
            'VL_BandwidthClass',
            'VL_SSCFVersion',
            'VL_RLCurrentCRLAdaptation',
            'VL_FLName',
            'VL_AntennaType',
            'VL_ModemType',
            'VL_SWVersion',
            'VL_RLCurrentCRMAAdaptation',
            'VL_RLName',
            'VL_RLCRMAEbNodB'
            'VL_RLAttenSetdB'], 
            termGui)

    ############################################################################
    # Sets the NmsPm VMT Basic Status in the database
    ############################################################################
    def aldbStatusNmspmBasicSet(self, pollTime, 
        ACUType='', Altitude='', AntennaTypeACUReported='', AntennaTypetermcfg='',
        APRBlanking='', BandwidthClass='', BlackFGPAVersion='', Customer='', CustomerType='',
        DOSVelocity='', FailedLogins='', FLACSMModcodeAdaptation='', FLNameEsNo='',
        FLRACSMVersionDecoderDemod='', FLRDSSSVersionDecoderDemod='', HandoffDist='',
        Hub='', LastLogin='', Latitude='', LoginAttempts='', Longitude='', ModemFGPAVersion='',
        ModemType='', PlatformType='', PlatformTypecfg='', PriorityLevel='', RedFGPAVersion='',
        RLModcodeAdaptation='', RLNameEbNo='', RLNameEsNo='', RLPowerControl='',
        RLRateAdaptation='', RLTargetRate='', RLWaveformType='', 
        SEDFileVersion='', SSCFFileVersion='', Status='', Uptime='',
        Velocity='', VMTName='', VMTSWVersion='',
        **kwargs):
            
        data_nmspm_basic = {'groupId' : self.groupId, 'pollTime': pollTime, 
            'ACUType': ACUType,
            'Altitude': Altitude,
            'AntennaTypeACUReported': AntennaTypeACUReported,
            'AntennaTypetermcfg': AntennaTypetermcfg,
            'APRBlanking': APRBlanking,
            'BandwidthClass': BandwidthClass,
            'BlackFGPAVersion': BlackFGPAVersion,
            'Customer': Customer,
            'CustomerType': CustomerType,
            'DOSVelocity': DOSVelocity,
            'FailedLogins': FailedLogins,
            'FLACSMModcodeAdaptation': FLACSMModcodeAdaptation,
            'FLNameEsNo': FLNameEsNo,
            'FLRACSMVersionDecoderDemod': FLRACSMVersionDecoderDemod,
            'FLRDSSSVersionDecoderDemod': FLRDSSSVersionDecoderDemod,
            'HandoffDist': HandoffDist,
            'Hub': Hub,
            'LastLogin': LastLogin,
            'Latitude': Latitude,
            'LoginAttempts': LoginAttempts,
            'Longitude': Longitude,
            'ModemFGPAVersion': ModemFGPAVersion,
            'ModemType': ModemType,
            'PlatformType': PlatformType,
            'PlatformTypecfg': PlatformTypecfg,
            'PriorityLevel': PriorityLevel,
            'RedFGPAVersion': RedFGPAVersion,
            'RLModcodeAdaptation': RLModcodeAdaptation,
            'RLNameEbNo': RLNameEbNo,
            'RLNameEsNo': RLNameEsNo,
            'RLPowerControl': RLPowerControl,
            'RLRateAdaptation': RLRateAdaptation,
            'RLTargetRate': RLTargetRate,
            'RLWaveformType': RLWaveformType,
            'SEDFileVersion': SEDFileVersion,
            'SSCFFileVersion': SSCFFileVersion,
            'Status': Status,
            'Uptime': Uptime,
            'Velocity': Velocity,
            'VMTName': VMTName,
            'VMTSWVersion': VMTSWVersion
            }

        self.generalSet('NmsPmVmtStatus', data_nmspm_basic, False)

        if len(kwargs):
            print ("\nWarning: Detected new NMSPM VMT status paramters [{}]\n".format(kwargs))

    ############################################################################
    # Gets and returns the VMT Basic Status from the database
    ############################################################################
    def aldbStatusNmspmBasicGet(self):
        return self.generalGet('NmsPmVmtStatus', ['pollTime', 
            'ACUType',
            'Altitude',
            'AntennaTypeACUReported',
            'AntennaTypetermcfg',
            'APRBlanking',
            'BandwidthClass',
            'BlackFGPAVersion',
            'Customer',
            'CustomerType',
            'DOSVelocity',
            'FailedLogins',
            'FLACSMModcodeAdaptation',
            'FLNameEsNo',
            'FLRACSMVersionDecoderDemod',
            'FLRDSSSVersionDecoderDemod',
            'HandoffDist',
            'Hub',
            'LastLogin',
            'Latitude',
            'LoginAttempts',
            'Longitude',
            'ModemFGPAVersion',
            'ModemType',
            'PlatformType',
            'PlatformTypecfg',
            'PriorityLevel',
            'RedFGPAVersion',
            'RLModcodeAdaptation',
            'RLNameEbNo',
            'RLNameEsNo',
            'RLPowerControl',
            'RLRateAdaptation',
            'RLTargetRate',
            'RLWaveformType',
            'SEDFileVersion',
            'SSCFFileVersion',
            'Status',
            'Uptime',
            'Velocity',
            'VMTName',
            'VMTSWVersion'],
             termGui)

    ############################################################################
    # Sets the Terminal Gen Status in the database
    ############################################################################
    def aldbStatusTerminalGenSet(self, pollTime, 
        FL_AGC='', FL_Amplitude='', FL_ChannelBandwidth='', FL_DownlinkFrequency='', 
        FL_DroppedCRC='', FL_EbNo='', FL_EsNo='',
        FL_FLRPacketsRx='', FL_FLState='', FL_IPPacketsRx='', FL_Waveform='', 
        HW_ACUAlarmStatus='', HW_ACUTemperature='', 
        HW_AntennaTemperature='', HW_AntennaType='', HW_BootCount='',
        HW_CPUTemperature='',
        HW_FLRBootFails='', HW_FLRFPGA1Fails='', HW_FLRFPGA2Fails='', HW_FLRTablesFails='',
        HW_HPATemperature='', HW_POSTStatus='', HW_SerialNumber='',
        HW_TerminalType='', HW_TXRBootCount='', HW_TXRFanSpeed='',
        HW_TXRSerialNumber='', HW_TXRTemperature='', HW_VMTChassisTemperature='',
        LS_Eth0RxBytes='', LS_Eth0RxPackets='', LS_Eth0RxPacketsDropped='',
        LS_Eth0TxBytes='', LS_Eth0TxPackets='', LS_Eth0TxPacketsDropped='',
        Pos_Altitude='', Pos_ATIDistance='', Pos_CurrentSatellite='',
        Pos_FootprintBoundaryDistance='', Pos_Latitude='', Pos_Longitude='',
        Pos_SatelliteHandoffStatus='', Pos_SatelliteLongitude='', Pos_Velocity='',
        RL_Attenuation='', RL_AttenuationLimit='', RL_AttenuationLowerLimit='', RL_DataRate='',
        RL_DefaultAttenuation='', RL_DopplerFrequencyOffset='', RL_IPPacketsTx='',
        RL_SymbolRate='',
        RL_TotalAttenuation='', RL_TxDisable='', RL_TxDisableCount='',
        RL_TxDisableTime='', RL_UplinkFrequency='', RL_Waveform='', 
        TS_ACUState='', 
        TS_AttemptedBRLLoginsSinceBoot='', TS_AttemptedBRLLoginsthisSatellite='',
        TS_AttemptedLogins='', TS_BBMessagesRx='', TS_ETI='', 
        TS_HubMode='', TS_InternalLogging='', TS_LastLogin='', TS_LoginState='', TS_LoginStateTime='', 
        TS_SatelliteIPAddr='', TS_State='', TS_SuccessfulBRLLogins='', 
        TS_SuccessfulLogins='', TS_SystemTime='', 
        TS_TerminalControllerState='',
        TS_TerminalUpTime='', TS_Time='', TS_TransmitState='',
        VS_ACSMDecoderVersion='', VS_ACSMDemodVersion='', VS_ACUBlockageDataFileVersion='',
        VS_ACUSoftwareVersion='', VS_ACUSquintDataFileVersion='', 
        VS_BlackFPGAVersion='', VS_DSSSDecoderVersion='',
        VS_DSSSDemodVersion='', VS_FLRBootVersion='', VS_FLRDSPVersion='',
        VS_FLRTablesVersion='', VS_GDRMFileVersion='', 
        VS_ModemFPGAVersion='', VS_RedFPGAVersion='', VS_RLCFileVersion='',
        VS_SEDFileVersion='', VS_SSCFFileVersion='', VS_TXRFPGAVersion='',
        VS_TXRHWType='', VS_VMTBootloaderSWVersion='', VS_VMTSoftwareVersion='',
        FL_GSESegmentsRx='', TS_AttemptedTransitionstoCRL='', 
        TS_LastCRLTransition='', TS_SuccessfulTransitionstoCRL='',
        TS_ContinuousReturnMessagesRx='',
        **kwargs):

        data_terminal_gen ={ 'groupId' : self.groupId, 'pollTime': pollTime, 
            'FL_AGC': FL_AGC,
            'FL_Amplitude': FL_Amplitude,
            'FL_ChannelBandwidth': FL_ChannelBandwidth,
            'FL_DownlinkFrequency': FL_DownlinkFrequency,
            'FL_DroppedCRC': FL_DroppedCRC,
            'FL_EbNo': FL_EbNo,
            'FL_EsNo': FL_EsNo,
            'FL_FLRPacketsRx': FL_FLRPacketsRx,
            'FL_FLState': FL_FLState,
            'FL_IPPacketsRx': FL_IPPacketsRx,
            'FL_Waveform': FL_Waveform,
            'HW_ACUAlarmStatus': HW_ACUAlarmStatus,
            'HW_ACUTemperature': HW_ACUTemperature,
            'HW_AntennaTemperature': HW_AntennaTemperature,
            'HW_AntennaType': HW_AntennaType,
            'HW_BootCount': HW_BootCount,
            'HW_CPUTemperature': HW_CPUTemperature,
            'HW_FLRBootFails': HW_FLRBootFails,
            'HW_FLRFPGA1Fails': HW_FLRFPGA1Fails,
            'HW_FLRFPGA2Fails': HW_FLRFPGA2Fails,
            'HW_FLRTablesFails': HW_FLRTablesFails,
            'HW_HPATemperature': HW_HPATemperature,
            'HW_POSTStatus': HW_POSTStatus,
            'HW_SerialNumber': HW_SerialNumber,
            'HW_TerminalType': HW_TerminalType,
            'HW_TXRBootCount': HW_TXRBootCount,
            'HW_TXRFanSpeed': HW_TXRFanSpeed,
            'HW_TXRSerialNumber': HW_TXRSerialNumber,
            'HW_TXRTemperature': HW_TXRTemperature,
            'HW_VMTChassisTemperature': HW_VMTChassisTemperature,
            'LS_Eth0RxBytes': LS_Eth0RxBytes,
            'LS_Eth0RxPackets': LS_Eth0RxPackets,
            'LS_Eth0RxPacketsDropped': LS_Eth0RxPacketsDropped,
            'LS_Eth0TxBytes': LS_Eth0TxBytes,
            'LS_Eth0TxPackets': LS_Eth0TxPackets,
            'LS_Eth0TxPacketsDropped': LS_Eth0TxPacketsDropped,
            'Pos_Altitude': Pos_Altitude,
            'Pos_ATIDistance': Pos_ATIDistance,
            'Pos_CurrentSatellite': Pos_CurrentSatellite,
            'Pos_FootprintBoundaryDistance': Pos_FootprintBoundaryDistance,
            'Pos_Latitude': Pos_Latitude,
            'Pos_Longitude': Pos_Longitude,
            'Pos_SatelliteHandoffStatus': Pos_SatelliteHandoffStatus,
            'Pos_SatelliteLongitude': Pos_SatelliteLongitude,
            'Pos_Velocity': Pos_Velocity,
            'RL_Attenuation': RL_Attenuation,
            'RL_AttenuationLimit': RL_AttenuationLimit,
            'RL_AttenuationLowerLimit': RL_AttenuationLowerLimit, 
            'RL_DataRate': RL_DataRate,
            'RL_DefaultAttenuation': RL_DefaultAttenuation,
            'RL_DopplerFrequencyOffset': RL_DopplerFrequencyOffset,
            'RL_IPPacketsTx': RL_IPPacketsTx,
            'RL_SymbolRate': RL_SymbolRate,
            'RL_TotalAttenuation': RL_TotalAttenuation,
            'RL_TxDisable': RL_TxDisable,
            'RL_TxDisableCount': RL_TxDisableCount,
            'RL_TxDisableTime': RL_TxDisableTime,
            'RL_UplinkFrequency': RL_UplinkFrequency,
            'RL_Waveform': RL_Waveform,
            'TS_ACUState': TS_ACUState,
            'TS_AttemptedBRLLoginsSinceBoot': TS_AttemptedBRLLoginsSinceBoot, 
            'TS_AttemptedBRLLoginsthisSatellite': TS_AttemptedBRLLoginsthisSatellite,
            'TS_AttemptedLogins': TS_AttemptedLogins,
            'TS_BBMessagesRx': TS_BBMessagesRx,
            'TS_ETI': TS_ETI,
            'TS_HubMode': TS_HubMode,
            'TS_InternalLogging': TS_InternalLogging,
            'TS_LastLogin': TS_LastLogin,
            'TS_LoginState': TS_LoginState,
            'TS_LoginStateTime': TS_LoginStateTime,
            'TS_LoginState': TS_LoginState,
            'TS_SatelliteIPAddr': TS_SatelliteIPAddr,
            'TS_State': TS_State,
            'TS_SuccessfulBRLLogins': TS_SuccessfulBRLLogins,
            'TS_SuccessfulLogins': TS_SuccessfulLogins,
            'TS_SystemTime': TS_SystemTime,
            'TS_TerminalControllerState': TS_TerminalControllerState,
            'TS_TerminalUpTime': TS_TerminalUpTime,
            'TS_Time': TS_Time,
            'TS_TransmitState': TS_TransmitState,
            'VS_ACSMDecoderVersion': VS_ACSMDecoderVersion,
            'VS_ACSMDemodVersion': VS_ACSMDemodVersion,
            'VS_ACUBlockageDataFileVersion': VS_ACUBlockageDataFileVersion,
            'VS_ACUSoftwareVersion': VS_ACUSoftwareVersion,
            'VS_ACUSquintDataFileVersion': VS_ACUSquintDataFileVersion,
            'VS_BlackFPGAVersion': VS_BlackFPGAVersion,
            'VS_DSSSDecoderVersion': VS_DSSSDecoderVersion,
            'VS_DSSSDemodVersion': VS_DSSSDemodVersion,
            'VS_FLRBootVersion': VS_FLRBootVersion,
            'VS_FLRDSPVersion': VS_FLRDSPVersion,
            'VS_FLRTablesVersion': VS_FLRTablesVersion,
            'VS_GDRMFileVersion': VS_GDRMFileVersion,
            'VS_ModemFPGAVersion': VS_ModemFPGAVersion,
            'VS_RedFPGAVersion': VS_RedFPGAVersion,
            'VS_RLCFileVersion': VS_RLCFileVersion,
            'VS_SEDFileVersion': VS_SEDFileVersion,
            'VS_SSCFFileVersion': VS_SSCFFileVersion,
            'VS_TXRFPGAVersion': VS_TXRFPGAVersion,
            'VS_TXRHWType': VS_TXRHWType,
            'VS_VMTBootloaderSWVersion': VS_VMTBootloaderSWVersion,
            'VS_VMTSoftwareVersion': VS_VMTSoftwareVersion,
            'FL_GSESegmentsRx': FL_GSESegmentsRx,
            'TS_AttemptedTransitionstoCRL': TS_AttemptedTransitionstoCRL,
            'TS_LastCRLTransition': TS_LastCRLTransition,
            'TS_SuccessfulTransitionstoCRL': TS_SuccessfulTransitionstoCRL,
            'TS_ContinuousReturnMessagesRx': TS_ContinuousReturnMessagesRx
            } 

        self.generalSet('TerminalStatus', data_terminal_gen, False)

        if len(kwargs):
            print ("\nWarning: Detected new Terminal Gen status paramters [{}]\n".format(kwargs))

    ############################################################################
    # Gets and returns the VMT Basic Status from the database
    ############################################################################
    def aldbStatusTerminalGenGet(self):
        return self.generalGet('TerminalStatus', ['pollTime', 
            'FL_AGC',
            'FL_Amplitude',
            'FL_ChannelBandwidth',
            'FL_DownlinkFrequency',
            'FL_DroppedCRC',
            'FL_EbNo',
            'FL_EsNo',
            'FL_FLRPacketsRx',
            'FL_FLState',
            'FL_IPPacketsRx',
            'FL_Waveform',
            'HW_ACUAlarmStatus',
            'HW_ACUTemperature',
            'HW_AntennaTemperature',
            'HW_AntennaType',
            'HW_BootCount',
            'HW_CPUTemperature',
            'HW_FLRBootFails',
            'HW_FLRFPGA1Fails',
            'HW_FLRFPGA2Fails',
            'HW_FLRTablesFails',
            'HW_HPATemperature',
            'HW_POSTStatus',
            'HW_SerialNumber',
            'HW_TerminalType',
            'HW_TXRBootCount',
            'HW_TXRFanSpeed',
            'HW_TXRSerialNumber',
            'HW_TXRTemperature',
            'HW_VMTChassisTemperature',
            'LS_Eth0RxBytes',
            'LS_Eth0RxPackets',
            'LS_Eth0RxPacketsDropped',
            'LS_Eth0TxBytes',
            'LS_Eth0TxPackets',
            'LS_Eth0TxPacketsDropped',
            'Pos_Altitude',
            'Pos_ATIDistance',
            'Pos_CurrentSatellite',
            'Pos_FootprintBoundaryDistance',
            'Pos_Latitude',
            'Pos_Longitude',
            'Pos_SatelliteHandoffStatus',
            'Pos_SatelliteLongitude',
            'Pos_Velocity',
            'RL_Attenuation',
            'RL_AttenuationLimit',
            'RL_AttenuationLowerLimit', 
            'RL_DataRate',
            'RL_DefaultAttenuation',
            'RL_DopplerFrequencyOffset',
            'RL_IPPacketsTx',
            'RL_SymbolRate',
            'RL_TotalAttenuation',
            'RL_TxDisable',
            'RL_TxDisableCount',
            'RL_TxDisableTime',
            'RL_UplinkFrequency',
            'RL_Waveform',
            'TS_ACUState',
            'TS_AttemptedBRLLoginsSinceBoot',
            'TS_AttemptedBRLLoginsthisSatellite',
            'TS_AttemptedLogins',
            'TS_BBMessagesRx',
            'TS_ETI',
            'TS_HubMode',
            'TS_InternalLogging',
            'TS_LastLogin',
            'TS_LoginState',
            'TS_LoginStateTime',
            'TS_SatelliteIPAddr',
            'TS_State',
            'TS_SuccessfulBRLLogins',
            'TS_SuccessfulLogins',
            'TS_SystemTime',
            'TS_TerminalControllerState',
            'TS_TerminalUpTime',
            'TS_Time',
            'TS_TransmitState',
            'VS_ACSMDecoderVersion',
            'VS_ACSMDemodVersion',
            'VS_ACUBlockageDataFileVersion',
            'VS_ACUSoftwareVersion',
            'VS_ACUSquintDataFileVersion',
            'VS_BlackFPGAVersion',
            'VS_DSSSDecoderVersion',
            'VS_DSSSDemodVersion',
            'VS_FLRBootVersion',
            'VS_FLRDSPVersion',
            'VS_FLRTablesVersion',
            'VS_GDRMFileVersion',
            'VS_ModemFPGAVersion',
            'VS_RedFPGAVersion',
            'VS_RLCFileVersion',
            'VS_SEDFileVersion',
            'VS_SSCFFileVersion',
            'VS_TXRFPGAVersion',
            'VS_TXRHWType',
            'VS_VMTBootloaderSWVersion',
            'VS_VMTSoftwareVersion',
            'FL_GSESegmentsRx',
            'TS_AttemptedTransitionstoCRL',
            'TS_LastCRLTransition',
            'TS_SuccessfulTransitionstoCRL',
            'TS_ContinuousReturnMessagesRx'
            ],termGui)

    ############################################################################
    # Sets the Terminal FL Status in the database
    ############################################################################
    def aldbStatusTerminalFLSet(self, pollTime, 
        FLR_AGC='', FLR_AttenuationFactor='', FLR_AverageByteRate='',
        FLR_DualAGC='', FLR_Errors='', FLR_FLRLFLR='',
        FLR_FLRPacketsRx='', FLR_HWType='', 
        FLR_IPPacketsRx='', FLR_L7093MHzLock='',
        FLR_L70LO2Lock='', FLR_LNBVoltage='', FLR_MaxByteRate='',
        FLR_PacketsDroppedCRC='', FLR_PacketsDroppedFiltered='',
        FLR_PacketsDroppedFull='', FLR_PacketsDroppedLength='', FLR_Rx18VAlarm='', 
        FLR_RxBytes='', FLR_SpectralInversion='', FLR_SynLock='', 
        FLR_InstantByteRate='', FLR_MinByteRate='', FLS_RevertTimeRemaining='',
        FLS_Amplitude='', FLS_AverageEsNo='',  FLS_BandwidthEfficiency='',
        FLS_CenterFrequencyOffset='', FLS_ChannelBandwidth='', FLS_ChipRate='',
        FLS_DataRate='', FLS_DataRateFactor='', FLS_DownlinkFrequency='', 
        FLS_EbNo='', FLS_EbNoRequired='', FLS_Encodedbitspersymbol='', 
        FLS_EndtoEndDelay='', FLS_EsNo='', FLS_EsNoRequired='',
        FLS_EsNoStdDeviation='', FLS_FECCodeRate='', 
        FLS_FECFrameSizeCfg='', FLS_FECFrameSizeModCode='', FLS_FLWaveformID='',
        FLS_ICWordPNSeed='', FLS_IterationNumber='', FLS_LBandFrequency='', FLS_LNBLOFrequency='',
        FLS_Modcode='', FLS_Modulation='', FLS_PilotPercentage='', 
        FLS_PPMOffset='',
        FLS_RxChipRate='', FLS_RxFrequencyOffset='', 
        FLS_SRRCRolloffFactor='', FLS_SRRCRollloffFactor='', FLS_Scrambling='',
        FLS_SpreadingFactor='', FLS_SpreadWordInitial='', FLS_SpreadWordTab='', FLS_SpreadWordTap='',
        FLS_State='', FLS_TCWordPNTap='', FLS_TruncationCount='',
        FLS_SymbolRate='', FLS_UniquePilotInitial='',
        FLS_UniquePilotTab='', FLS_UniquePilotTap='', FLS_UniqueWordInitial='', 
        FLS_UniqueWordPreamble='', FLS_UniqueWordTap='',
        **kwargs):

        data_terminal_FL ={ 'groupId' : self.groupId, 'pollTime': pollTime, 
            'FLR_AGC': FLR_AGC,
            'FLR_AttenuationFactor': FLR_AttenuationFactor,
            'FLR_AverageByteRate': FLR_AverageByteRate,
            'FLR_DualAGC': FLR_DualAGC,
            'FLR_Errors': FLR_Errors,
            'FLR_FLRLFLR': FLR_FLRLFLR,
            'FLR_FLRPacketsRx': FLR_FLRPacketsRx,
            'FLR_HWType': FLR_HWType,
            'FLR_InstantByteRate': FLR_InstantByteRate,
            'FLR_IPPacketsRx': FLR_IPPacketsRx,
            'FLR_L7093MHzLock': FLR_L7093MHzLock,
            'FLR_L70LO2Lock': FLR_L70LO2Lock,
            'FLR_LNBVoltage': FLR_LNBVoltage,
            'FLR_MaxByteRate': FLR_MaxByteRate,
            'FLR_MinByteRate': FLR_MinByteRate, 
            'FLR_PacketsDroppedCRC': FLR_PacketsDroppedCRC,
            'FLR_PacketsDroppedFiltered': FLR_PacketsDroppedFiltered,
            'FLR_PacketsDroppedFull': FLR_PacketsDroppedFull,
            'FLR_PacketsDroppedLength': FLR_PacketsDroppedLength,
            'FLR_Rx18VAlarm': FLR_Rx18VAlarm,
            'FLR_RxBytes': FLR_RxBytes,
            'FLR_SpectralInversion': FLR_SpectralInversion,
            'FLR_SynLock': FLR_SynLock,
            'FLS_Amplitude': FLS_Amplitude,
            'FLS_AverageEsNo': FLS_AverageEsNo,
            'FLS_BandwidthEfficiency': FLS_BandwidthEfficiency,
            'FLS_CenterFrequencyOffset': FLS_CenterFrequencyOffset,
            'FLS_ChannelBandwidth': FLS_ChannelBandwidth,
            'FLS_ChipRate': FLS_ChipRate,
            'FLS_DataRate': FLS_DataRate,
            'FLS_DataRateFactor': FLS_DataRateFactor,
            'FLS_DownlinkFrequency': FLS_DownlinkFrequency,
            'FLS_EbNo': FLS_EbNo,
            'FLS_EbNoRequired': FLS_EbNoRequired,
            'FLS_Encodedbitspersymbol': FLS_Encodedbitspersymbol,
            'FLS_EndtoEndDelay': FLS_EndtoEndDelay,
            'FLS_EsNo': FLS_EsNo,
            'FLS_EsNoRequired': FLS_EsNoRequired,
            'FLS_EsNoStdDeviation': FLS_EsNoStdDeviation,
            'FLS_FECCodeRate':  FLS_FECCodeRate,
            'FLS_FECFrameSizeCfg': FLS_FECFrameSizeCfg,
            'FLS_FECFrameSizeModCode': FLS_FECFrameSizeModCode,
            'FLS_FLWaveformID': FLS_FLWaveformID,
            'FLS_ICWordPNSeed': FLS_ICWordPNSeed,
            'FLS_IterationNumber': FLS_IterationNumber,
            'FLS_LBandFrequency': FLS_LBandFrequency,
            'FLS_LNBLOFrequency': FLS_LNBLOFrequency,
            'FLS_Modcode': FLS_Modcode,
            'FLS_Modulation': FLS_Modulation,
            'FLS_PilotPercentage': FLS_PilotPercentage,
            'FLS_PPMOffset': FLS_PPMOffset,
            'FLS_RevertTimeRemaining': FLS_RevertTimeRemaining,
            'FLS_RxChipRate': FLS_RxChipRate,
            'FLS_RxFrequencyOffset': FLS_RxFrequencyOffset,
            'FLS_Scrambling': FLS_Scrambling,
            'FLS_SpreadWordInitial': FLS_SpreadWordInitial,
            'FLS_SpreadWordTab': FLS_SpreadWordTab,
            'FLS_SpreadWordTap': FLS_SpreadWordTap,
            'FLS_SRRCRolloffFactor': FLS_SRRCRolloffFactor,
            'FLS_SRRCRollloffFactor': FLS_SRRCRollloffFactor,
            'FLS_SpreadingFactor': FLS_SpreadingFactor,
            'FLS_State': FLS_State,
            'FLS_SymbolRate': FLS_SymbolRate,
            'FLS_TCWordPNTap': FLS_TCWordPNTap,
            'FLS_TruncationCount': FLS_TruncationCount,
            'FLS_UniquePilotInitial': FLS_UniquePilotInitial,
            'FLS_UniquePilotTab': FLS_UniquePilotTap,
            'FLS_UniquePilotTap': FLS_UniquePilotTap,
            'FLS_UniqueWordInitial': FLS_UniqueWordInitial,
            'FLS_UniqueWordPreamble': FLS_UniqueWordPreamble,
            'FLS_UniqueWordTap': FLS_UniqueWordTap
            } 

        self.generalSet('TerminalStatus', data_terminal_FL, False)

        if len(kwargs):
            print ("\nWarning: Detected new Terminal FL status paramters [{}]\n".format(kwargs))

    ############################################################################
    # Gets and returns the Terminal FL Status from the database
    ############################################################################
    def aldbStatusTerminalFLGet(self):
        return self.generalGet('TerminalStatus', ['pollTime', 
            'FLR_AGC',
            'FLR_AttenuationFactor',
            'FLR_AverageByteRate',
            'FLR_DualAGC',
            'FLR_Errors',
            'FLR_FLRLFLR',
            'FLR_FLRPacketsRx',
            'FLR_HWType',
            'FLR_IPPacketsRx',
            'FLR_L7093MHzLock',
            'FLR_L70LO2Lock',
            'FLR_LNBVoltage',
            'FLR_MaxByteRate',
            'FLR_PacketsDroppedCRC',
            'FLR_PacketsDroppedFiltered',
            'FLR_PacketsDroppedFull',
            'FLR_PacketsDroppedLength',
            'FLR_Rx18VAlarm',
            'FLR_RxBytes',
            'FLR_SpectralInversion',
            'FLR_SynLock',
            'FLR_InstantByteRate', 
            'FLR_MinByteRate', 
            'FLS_RevertTimeRemaining',
            'FLS_Amplitude',
            'FLS_AverageEsNo',
            'FLS_BandwidthEfficiency',
            'FLS_CenterFrequencyOffset',
            'FLS_ChannelBandwidth' ,
            'FLS_ChipRate',
            'FLS_DataRate',
            'FLS_DataRateFactor',
            'FLS_DownlinkFrequency',
            'FLS_EbNo',
            'FLS_EbNoRequired',
            'FLS_Encodedbitspersymbol',
            'FLS_EndtoEndDelay',
            'FLS_EsNo',
            'FLS_EsNoRequired',
            'FLS_EsNoStdDeviation',
            'FLS_FECCodeRate',
            'FLS_FECFrameSizeCfg',
            'FLS_FECFrameSizeModCode',
            'FLS_FLWaveformID',
            'FLS_ICWordPNSeed',
            'FLS_IterationNumber',
            'FLS_LBandFrequency',
            'FLS_LNBLOFrequency',
            'FLS_Modcode',
            'FLS_Modulation',
            'FLS_PilotPercentage',
            'FLS_PPMOffset',
            'FLS_RxChipRate',
            'FLS_RxFrequencyOffset',
            'FLS_Scrambling',
            'FLS_SpreadWordInitial',
            'FLS_SpreadWordTab',
            'FLS_SpreadWordTap',
            'FLS_SRRCRolloffFactor',
            'FLS_SRRCRollloffFactor',
            'FLS_SpreadingFactor',
            'FLS_State',
            'FLS_SymbolRate',
            'FLS_TCWordPNTap',
            'FLS_TruncationCount',
            'FLS_UniquePilotInitial',
            'FLS_UniquePilotTab',
            'FLS_UniquePilotTap',
            'FLS_UniqueWordInitial',
            'FLS_UniqueWordPreamble',
            'FLS_UniqueWordTap'
            ],termGui)


    ############################################################################
    # Sets the Terminal RL Status in the database
    ############################################################################
    def aldbStatusTerminalRLSet(self, pollTime, 
        RLS_ATIDisableDistance='', RLS_Attenuation='', 
        RLS_AttenuationLimit='', RLS_AttenuationLowerLimit='', 
        RLS_CableLossAttenuationOffset='', RLS_ChipRate='', RLS_ChipRateOffset='', RLS_ChipRatio='',
        RLS_CongestionControlGroup='', RLS_CongestionControlThreshold='', 
        RLS_DataRate='', RLS_DataRateOffset='',
        RLS_DefaultAttenuation='', RLS_DopplerFrequency='', RLS_DOSVelocity='',
        RLS_FootprintBoundaryDistance='', RLS_HubFrequencyOffset='', RLS_LBandFrequency='',
        RLS_LoginAttenuation='', RLS_LoginFrequencyOffset='', 
        RLS_LongPNSeed='', RLS_LongPNTap='', RLS_NominalAttenuation='',
        RLS_PacketSize='', RLS_PNPreamble='', RLS_RLWaveformID='',
        RLS_SatelliteHandoffStatus='', RLS_ShortPNSeed='', RLS_ShortPNTap='',
        RLS_TotalAttenuation='', RLS_TotalFrequencyOffset='', RLS_TXBFrequency='',
        RLS_TxDisable='', RLS_TxInhibitLogoutTimeout='', RLS_UplinkFrequency='',
        RLS_EbNoRequired='',
        RLS_EsNoRequired='',
        RLS_SRRCRollofffactor='',
        RLS_Modulation='',
        RLS_EndtoEndDelay='',
        RLS_Scrambling='',
        RLS_SpreadWordInitial='',
        RLS_BandwidthEfficiency='',
        RLS_SpreadingFactor='',
        RLS_SymbolRate='',
        RLS_DataRateFactor='',
        RLS_Encodedbitspersymbol='',
        RLS_SpreadWordTap='',
        RLS_UniquePilotTap='',
        RLS_FECCodeRate='',
        RLS_PilotPercentage='',
        RLS_UniquePilotInitial='',
        RLS_Modcode='',
        RLS_FECFrameSize='',
        RLS_ChannelBandwidth='',
        RLS_UniqueWordInitial='',
        RLS_UniqueWordTap='',
        TXR_300MHzLock='', TXR_BootCount='', TXR_ChassisTemperature='',
        TXR_Errors='', TXR_ETI='', TXR_HWType='', TXR_IPPacketsTx='', 
        TXR_LOLock='', TXR_PowerFail='', TXR_PowerOverTemperature='', 
        TXR_Rx18VAlarm='', TXR_Tx18VAlarm='', TXR_TxBytes='',
        TXR_TxPacketsDropped='', TXR_TxPacketsDroppedCongestionCtrl='', 
        TXR_TxQueueDropsBufferOverflow='',
        RLS_ATIConfig='', 
        TXR_AverageByteRate='', TXR_FanSpeed='', TXR_FanStatus='', 
        TXR_InstantByteRate='', TXR_MaxByteRate='', 
        TXR_MinByteRate='', TXR_TXRTemperature='',
        **kwargs):


        data_terminal_RL ={ 'groupId' : self.groupId, 'pollTime': pollTime, 
            'RLS_ATIDisableDistance': RLS_ATIDisableDistance,
            'RLS_Attenuation': RLS_Attenuation,
            'RLS_AttenuationLimit': RLS_AttenuationLimit,
            'RLS_AttenuationLowerLimit': RLS_AttenuationLowerLimit,
            'RLS_CableLossAttenuationOffset': RLS_CableLossAttenuationOffset,
            'RLS_ChipRate': RLS_ChipRate,
            'RLS_ChipRateOffset': RLS_ChipRateOffset,
            'RLS_ChipRatio': RLS_ChipRatio,
            'RLS_CongestionControlGroup': RLS_CongestionControlGroup,
            'RLS_CongestionControlThreshold': RLS_CongestionControlThreshold,
            'RLS_DataRate': RLS_DataRate,
            'RLS_DataRateOffset': RLS_DataRateOffset,
            'RLS_DefaultAttenuation': RLS_DefaultAttenuation,
            'RLS_DopplerFrequency': RLS_DopplerFrequency,
            'RLS_DOSVelocity': RLS_DOSVelocity,
            'RLS_FootprintBoundaryDistance': RLS_FootprintBoundaryDistance,
            'RLS_HubFrequencyOffset': RLS_HubFrequencyOffset,
            'RLS_LBandFrequency': RLS_LBandFrequency,
            'RLS_LoginAttenuation': RLS_LoginAttenuation,
            'RLS_LoginFrequencyOffset': RLS_LoginFrequencyOffset,
            'RLS_LongPNSeed': RLS_LongPNSeed,
            'RLS_LongPNTap': RLS_LongPNTap,
            'RLS_NominalAttenuation': RLS_NominalAttenuation,
            'RLS_PacketSize': RLS_PacketSize,
            'RLS_PNPreamble': RLS_PNPreamble,
            'RLS_RLWaveformID': RLS_RLWaveformID,
            'RLS_SatelliteHandoffStatus': RLS_SatelliteHandoffStatus,
            'RLS_ShortPNSeed': RLS_ShortPNSeed,
            'RLS_ShortPNTap': RLS_ShortPNTap,
            'RLS_TotalAttenuation': RLS_TotalAttenuation,
            'RLS_TotalFrequencyOffset': RLS_TotalFrequencyOffset,
            'RLS_TXBFrequency': RLS_TXBFrequency,
            'RLS_TxDisable': RLS_TxDisable,
            'RLS_TxInhibitLogoutTimeout': RLS_TxInhibitLogoutTimeout,
            'RLS_UplinkFrequency': RLS_UplinkFrequency,
            'RLS_EbNoRequired' : RLS_EbNoRequired,
            'RLS_EsNoRequired' : RLS_EsNoRequired,
            'RLS_SRRCRollofffactor' : RLS_SRRCRollofffactor,
            'RLS_Modulation' : RLS_Modulation,
            'RLS_EndtoEndDelay' : RLS_EndtoEndDelay,
            'RLS_Scrambling' : RLS_Scrambling,
            'RLS_SpreadWordInitial' : RLS_SpreadWordInitial,
            'RLS_BandwidthEfficiency' : RLS_BandwidthEfficiency,
            'RLS_SpreadingFactor' : RLS_SpreadingFactor,
            'RLS_SymbolRate' : RLS_SymbolRate,
            'RLS_DataRateFactor' : RLS_DataRateFactor,
            'RLS_Encodedbitspersymbol' : RLS_Encodedbitspersymbol,
            'RLS_SpreadWordTap' : RLS_SpreadWordTap,
            'RLS_UniquePilotTap' : RLS_UniquePilotTap,
            'RLS_FECCodeRate' : RLS_FECCodeRate,
            'RLS_PilotPercentage' : RLS_PilotPercentage,
            'RLS_UniquePilotInitial' : RLS_UniquePilotInitial,
            'RLS_Modcode' : RLS_Modcode,
            'RLS_FECFrameSize' : RLS_FECFrameSize,
            'RLS_ChannelBandwidth' : RLS_ChannelBandwidth,
            'RLS_UniqueWordInitial' : RLS_UniqueWordInitial,
            'RLS_UniqueWordTap' : RLS_UniqueWordTap,
            'TXR_300MHzLock': TXR_300MHzLock,
            'TXR_BootCount': TXR_BootCount,
            'TXR_ChassisTemperature': TXR_ChassisTemperature,
            'TXR_Errors': TXR_Errors,
            'TXR_ETI': TXR_ETI,
            'TXR_HWType': TXR_HWType,
            'TXR_IPPacketsTx': TXR_IPPacketsTx,
            'TXR_LOLock': TXR_LOLock,
            'TXR_PowerFail': TXR_PowerFail,
            'TXR_PowerOverTemperature': TXR_PowerOverTemperature,
            'TXR_Rx18VAlarm': TXR_Rx18VAlarm,
            'TXR_Tx18VAlarm': TXR_Tx18VAlarm,
            'TXR_TxBytes': TXR_TxBytes,
            'TXR_TxPacketsDropped': TXR_TxPacketsDropped,
            'TXR_TxPacketsDroppedCongestionCtrl': TXR_TxPacketsDroppedCongestionCtrl,
            'TXR_TxQueueDropsBufferOverflow': TXR_TxQueueDropsBufferOverflow,
            'RLS_ATIConfig': RLS_ATIConfig,
            'TXR_AverageByteRate': TXR_AverageByteRate,
            'TXR_FanSpeed': TXR_FanSpeed,
            'TXR_FanStatus': TXR_FanStatus,
            'TXR_InstantByteRate': TXR_InstantByteRate,
            'TXR_MaxByteRate': TXR_MaxByteRate,
            'TXR_MinByteRate': TXR_MinByteRate,
            'TXR_TXRTemperature': TXR_TXRTemperature
            } 

        self.generalSet('TerminalStatus', data_terminal_RL, False)

        if len(kwargs):
            print ("\nWarning: Detected new Terminal RL status paramters [{}]\n".format(kwargs))


    ############################################################################
    # Gets and returns the Terminal RL Status from the database
    ############################################################################
    def aldbStatusTerminalRLGet(self):
        return self.generalGet('TerminalStatus', [ 'pollTime', 
            'RLS_ATIDisableDistance',
            'RLS_Attenuation',
            'RLS_AttenuationLimit',
            'RLS_AttenuationLowerLimit',
            'RLS_CableLossAttenuationOffset',
            'RLS_ChipRate',
            'RLS_ChipRateOffset',
            'RLS_ChipRatio',
            'RLS_CongestionControlGroup',
            'RLS_CongestionControlThreshold',
            'RLS_DataRate',
            'RLS_DataRateOffset',
            'RLS_DefaultAttenuation',
            'RLS_DopplerFrequency',
            'RLS_DOSVelocity',
            'RLS_FootprintBoundaryDistance',
            'RLS_HubFrequencyOffset',
            'RLS_LBandFrequency',
            'RLS_LoginAttenuation',
            'RLS_LoginFrequencyOffset',
            'RLS_LongPNSeed',
            'RLS_LongPNTap',
            'RLS_NominalAttenuation',
            'RLS_PacketSize',
            'RLS_PNPreamble',
            'RLS_RLWaveformID',
            'RLS_SatelliteHandoffStatus',
            'RLS_ShortPNSeed',
            'RLS_ShortPNTap',
            'RLS_TotalAttenuation',
            'RLS_TotalFrequencyOffset',
            'RLS_TXBFrequency',
            'RLS_TxDisable',
            'RLS_TxInhibitLogoutTimeout',
            'RLS_UplinkFrequency',
            'RLS_EbNoRequired',
            'RLS_EsNoRequired',
            'RLS_SRRCRollofffactor',
            'RLS_Modulation',
            'RLS_EndtoEndDelay',
            'RLS_Scrambling',
            'RLS_SpreadWordInitial',
            'RLS_BandwidthEfficiency',
            'RLS_SpreadingFactor',
            'RLS_SymbolRate',
            'RLS_DataRateFactor',
            'RLS_Encodedbitspersymbol',
            'RLS_SpreadWordTap',
            'RLS_UniquePilotTap',
            'RLS_FECCodeRate',
            'RLS_PilotPercentage',
            'RLS_UniquePilotInitial',
            'RLS_Modcode',
            'RLS_FECFrameSize',
            'RLS_ChannelBandwidth',
            'RLS_UniqueWordInitial',
            'RLS_UniqueWordTap',
            'TXR_300MHzLock',
            'TXR_BootCount',
            'TXR_ChassisTemperature',
            'TXR_Errors',
            'TXR_ETI',
            'TXR_HWType',
            'TXR_IPPacketsTx',
            'TXR_LOLock',
            'TXR_PowerFail',
            'TXR_PowerOverTemperature',
            'TXR_Rx18VAlarm',
            'TXR_Tx18VAlarm',
            'TXR_TxBytes',
            'TXR_TxPacketsDropped',
            'TXR_TxPacketsDroppedCongestionCtrl',
            'TXR_TxQueueDropsBufferOverflow',
            'RLS_ATIConfig',
            'TXR_AverageByteRate',
            'TXR_FanSpeed',
            'TXR_FanStatus',
            'TXR_InstantByteRate',
            'TXR_MaxByteRate',
            'TXR_MinByteRate',
            'TXR_TXRTemperature'
            ],termGui) 


    ############################################################################
    # Sets the Terminal ACU Status in the database
    ############################################################################
    def aldbStatusTerminalACUSet(self, pollTime, 
        ACU_ACUQueryRespMsgICDVersion='', ACU_ACUTXInhibit='', 
        ACU_AircraftType='', ACU_AircraftTypeFromACU='',
        ACU_AntStatusRespMsgICDVersion='',
        ACU_CalculatedHeading='', ACU_CalculatedPitch='', 
        ACU_CalculatedRoll='', 
        ACU_FirmwareVersion='',
        ACU_GatewayIPAddress='',
        ACU_HardwarePartNum='', ACU_HardwareSerialNum='', 
        ACU_IPAddress='', ACU_IPAddressMask='',
        ACU_NavDataCh1Bad='', 
        ACU_NavDataCh1Good='', ACU_NavDataCh2Bad='', ACU_NavDataCh2Good='',
        ACU_Port='', ACU_RSSIRate='',
        ACU_AntRcvParamRespMsgICDVersion='',
        ACU_SoftwarePartNum='', ACU_SoftwareVersion='', 
        ACU_State='', ACU_StatusMessageRate='',
        ACU_Temperature='', ACU_Type='', 
        ACU_Uptime='', ACU_VMTConfigCmdMsgICDVersion='', 
        Ant_AntennaMountOrientation='',
        Ant_AntennaState='',
        Ant_AzimuthErrorLimit='', Ant_ElevationErrorLimit='', 
        Ant_HorizStabilizerPos='', Ant_LNBSelect='', Ant_PartNum='',
        Ant_PlatformPitchOffset='', Ant_PlatformRollOffset='', 
        Ant_PlatformYawOffset='', Ant_PolarizationErrorLimit='',
        Ant_SerialNum='', Ant_Type='',
        Ant_MainFirmwareVersion='', Ant_ModelNum='',
        Ant_MotorControllerFWVer='', Ant_RFFirmwareVersion='',
        Ant_SkewMotorCtrlFWVer='',
        Nav_Altitude='', Nav_SatelliteLongitude='',
        Nav_SatellitePolarization='', 
        Nav_SatellitePolarizationCant='', 
        Nav_SatelliteRxPolarization='', 
        ACU_ACUDroppedMsgCount='',
        ACU_ACUIPLVersion='',
        ACU_ACUPartialMsgCount='',
        ACU_ACUPOSTStatus='',
        ACU_ACUPowerCycles='',
        ACU_ACUPowerInterruptions='',
        ACU_ACUTime='',
        ACU_AlarmStatus='',
        ACU_ETI='',
        ACU_HPAPower='',
        ACU_SoftwareStatus='',
        Ant_AntennaCommStatus='',
        Ant_BaseTemperature='',
        Ant_ETI='',
        Ant_SensorCalibrationStatus='',
        Ant_SensorCalTableStatus='',
        Ant_SlipDetection='',
        Ant_SlipsCounted='',
        Ant_TrackingState='',
        Nav_AbsAzimuth='',
        Nav_AbsElevation='',
        Nav_AbsPolarization='',
        Nav_AzimuthPositionError='',
        Nav_AzimuthSteps='',
        Nav_ElevationPositionError='',
        Nav_ElevationSteps='',
        Nav_Latitude='',
        Nav_Longitude='',
        Nav_PolarizationPositionError='',
        Nav_PolarizationSteps='',
        Nav_SatelliteAzimuth='',
        Nav_SatelliteElevation='',
        Nav_TrueHeading='',
        ACU_ACUBlockageEnableStatus='',
        ACU_ACUBlockageTblLoadedStatus='',
        ACU_ACUSquintEnableStatus='',
        ACU_ACUSquintTblLoadedStatus='',
        ACU_ACUTXLockoutAlarm='',
        ACU_AircraftFlightTime='',
        ACU_AircraftTakeoffs='',
        ACU_IFCSummaryAlarm='',
        ACU_ProcessRestartCount='',
        ACU_RSSIStatus='',
        ACU_SquintTableInUse='',
        Ant_AntennaInputCurrent='',
        Ant_AntennaInputVoltage='',
        Ant_AntennaTxInhibitStatus='',
        Ant_AvgAZELMotorTemperature='',
        Ant_AvgAZELMotorVoltage='',
        Ant_AZMotorPosition='',
        Ant_ELMotorPosition='',
        Ant_RateSensorAvgAccel='',
        Ant_RateSensorPeakAccel='',
        Ant_RxBandSettings='',
        Ant_RxFrequency='',
        Ant_SSPALeftFanSpeed='',
        Ant_SSPAPowerStatus='',
        Ant_SSPARightFanSpeed='',
        Ant_StepTrackPaused='',
        Ant_TxBandSettings='',
        Ant_TxFrequency='',
        Nav_PolarizationAngle='',
        Nav_SatelliteTxPolarization='',
        Nav_TxElevationHysteresis='',
        Nav_TxMinimumElevation='',
        Nav_TxSkewAngle='',
        Nav_TxSkewHysteresis='',
        Nav_TxSkewLimit='',
        Ant_Flap4Offset='',
        Ant_Flap3Offset='',
        Ant_Flap2Offset='',
        Ant_Flap1Offset='',
        Ant_GIVFlapCode='',
        **kwargs):

        data_terminal_ACU={ 'groupId' : self.groupId, 'pollTime': pollTime, 
            'ACU_ACUQueryRespMsgICDVersion': ACU_ACUQueryRespMsgICDVersion,
            'ACU_ACUTXInhibit': ACU_ACUTXInhibit,
            'ACU_AircraftType': ACU_AircraftType,
            'ACU_AircraftTypeFromACU': ACU_AircraftTypeFromACU,
            'ACU_AntRcvParamRespMsgICDVersion' : ACU_AntRcvParamRespMsgICDVersion,
            'ACU_AntStatusRespMsgICDVersion': ACU_AntStatusRespMsgICDVersion,
            'ACU_CalculatedHeading': ACU_CalculatedHeading,
            'ACU_CalculatedPitch': ACU_CalculatedPitch,
            'ACU_CalculatedRoll': ACU_CalculatedRoll,
            'ACU_FirmwareVersion' : ACU_FirmwareVersion,
            'ACU_GatewayIPAddress': ACU_GatewayIPAddress,
            'ACU_HardwarePartNum': ACU_HardwarePartNum,
            'ACU_HardwareSerialNum': ACU_HardwareSerialNum,
            'ACU_IPAddress': ACU_IPAddress,
            'ACU_IPAddressMask': ACU_IPAddressMask,
            'ACU_NavDataCh1Bad': ACU_NavDataCh1Bad,
            'ACU_NavDataCh1Good': ACU_NavDataCh1Good,
            'ACU_NavDataCh2Bad' : ACU_NavDataCh2Bad,
            'ACU_NavDataCh2Good' : ACU_NavDataCh2Good,
            'ACU_Port': ACU_Port,
            'ACU_RSSIRate': ACU_RSSIRate,
            'ACU_SoftwarePartNum': ACU_SoftwarePartNum,
            'ACU_SoftwareVersion': ACU_SoftwareVersion,
            'ACU_State': ACU_State,
            'ACU_StatusMessageRate': ACU_StatusMessageRate,
            'ACU_Temperature': ACU_Temperature,
            'ACU_Type': ACU_Type,
            'ACU_Uptime': ACU_Uptime,
            'ACU_VMTConfigCmdMsgICDVersion': ACU_VMTConfigCmdMsgICDVersion,
            'Ant_AntennaMountOrientation': Ant_AntennaMountOrientation,
            'Ant_AntennaState' : Ant_AntennaState,
            'Ant_AzimuthErrorLimit': Ant_AzimuthErrorLimit,
            'Ant_ElevationErrorLimit': Ant_ElevationErrorLimit,
            'Ant_HorizStabilizerPos': Ant_HorizStabilizerPos,
            'Ant_LNBSelect': Ant_LNBSelect,
            'Ant_MainFirmwareVersion' : Ant_MainFirmwareVersion,
            'Ant_ModelNum' : Ant_ModelNum,
            'Ant_MotorControllerFWVer' : Ant_MotorControllerFWVer,
            'Ant_PartNum': Ant_PartNum,
            'Ant_PlatformPitchOffset': Ant_PlatformPitchOffset,
            'Ant_PlatformRollOffset': Ant_PlatformRollOffset,
            'Ant_PlatformYawOffset': Ant_PlatformYawOffset,
            'Ant_PolarizationErrorLimit': Ant_PolarizationErrorLimit,
            'Ant_RFFirmwareVersion' : Ant_RFFirmwareVersion,
            'Ant_SerialNum': Ant_SerialNum,
            'Ant_SkewMotorCtrlFWVer' : Ant_SkewMotorCtrlFWVer,
            'Ant_Type': Ant_Type,
            'Nav_Altitude': Nav_Altitude,
            'Nav_SatelliteLongitude': Nav_SatelliteLongitude,
            'Nav_SatellitePolarization': Nav_SatellitePolarization,
            'Nav_SatellitePolarizationCant': Nav_SatellitePolarizationCant,
            'Nav_SatelliteRxPolarization': Nav_SatelliteRxPolarization,
            'ACU_ACUDroppedMsgCount': ACU_ACUDroppedMsgCount,
            'ACU_ACUIPLVersion': ACU_ACUIPLVersion,
            'ACU_ACUPartialMsgCount': ACU_ACUPartialMsgCount,
            'ACU_ACUPOSTStatus': ACU_ACUPOSTStatus,
            'ACU_ACUPowerCycles': ACU_ACUPowerCycles,
            'ACU_ACUPowerInterruptions': ACU_ACUPowerInterruptions,
            'ACU_ACUTime': ACU_ACUTime,
            'ACU_AlarmStatus': ACU_AlarmStatus,
            'ACU_ETI': ACU_ETI,
            'ACU_HPAPower': ACU_HPAPower,
            'ACU_SoftwareStatus': ACU_SoftwareStatus,
            'Ant_AntennaCommStatus': Ant_AntennaCommStatus,
            'Ant_BaseTemperature': Ant_BaseTemperature,
            'Ant_ETI': Ant_ETI,
            'Ant_SensorCalibrationStatus': Ant_SensorCalibrationStatus,
            'Ant_SensorCalTableStatus': Ant_SensorCalTableStatus,
            'Ant_SlipDetection': Ant_SlipDetection,
            'Ant_SlipsCounted': Ant_SlipsCounted,
            'Ant_TrackingState': Ant_TrackingState,
            'Nav_AbsAzimuth': Nav_AbsAzimuth,
            'Nav_AbsElevation': Nav_AbsElevation,
            'Nav_AbsPolarization': Nav_AbsPolarization,
            'Nav_AzimuthPositionError': Nav_AzimuthPositionError,
            'Nav_AzimuthSteps': Nav_AzimuthSteps,
            'Nav_ElevationPositionError': Nav_ElevationPositionError,
            'Nav_ElevationSteps': Nav_ElevationSteps,
            'Nav_Latitude': Nav_Latitude,
            'Nav_Longitude': Nav_Longitude,
            'Nav_PolarizationPositionError': Nav_PolarizationPositionError,
            'Nav_PolarizationSteps': Nav_PolarizationSteps,
            'Nav_SatelliteAzimuth': Nav_SatelliteAzimuth,
            'Nav_SatelliteElevation': Nav_SatelliteElevation,
            'Nav_TrueHeading': Nav_TrueHeading,
            'ACU_ACUBlockageEnableStatus': ACU_ACUBlockageEnableStatus,
            'ACU_ACUBlockageTblLoadedStatus': ACU_ACUBlockageTblLoadedStatus,
            'ACU_ACUSquintEnableStatus': ACU_ACUSquintEnableStatus,
            'ACU_ACUSquintTblLoadedStatus': ACU_ACUSquintTblLoadedStatus,
            'ACU_ACUTXLockoutAlarm': ACU_ACUTXLockoutAlarm,
            'ACU_AircraftFlightTime': ACU_AircraftFlightTime,
            'ACU_AircraftTakeoffs': ACU_AircraftTakeoffs,
            'ACU_IFCSummaryAlarm': ACU_IFCSummaryAlarm,
            'ACU_ProcessRestartCount': ACU_ProcessRestartCount,
            'ACU_RSSIStatus': ACU_RSSIStatus,
            'ACU_SquintTableInUse': ACU_SquintTableInUse,
            'Ant_AntennaInputCurrent': Ant_AntennaInputCurrent,
            'Ant_AntennaInputVoltage': Ant_AntennaInputVoltage,
            'Ant_AntennaTxInhibitStatus': Ant_AntennaTxInhibitStatus,
            'Ant_AvgAZELMotorTemperature': Ant_AvgAZELMotorTemperature,
            'Ant_AvgAZELMotorVoltage': Ant_AvgAZELMotorVoltage,
            'Ant_AZMotorPosition': Ant_AZMotorPosition,
            'Ant_ELMotorPosition': Ant_ELMotorPosition,
            'Ant_RateSensorAvgAccel': Ant_RateSensorAvgAccel,
            'Ant_RateSensorPeakAccel': Ant_RateSensorPeakAccel,
            'Ant_RxBandSettings': Ant_RxBandSettings,
            'Ant_RxFrequency': Ant_RxFrequency,
            'Ant_SSPALeftFanSpeed': Ant_SSPALeftFanSpeed,
            'Ant_SSPAPowerStatus': Ant_SSPAPowerStatus,
            'Ant_SSPARightFanSpeed': Ant_SSPARightFanSpeed,
            'Ant_StepTrackPaused': Ant_StepTrackPaused,
            'Ant_TxBandSettings': Ant_TxBandSettings,
            'Ant_TxFrequency': Ant_TxFrequency,
            'Nav_PolarizationAngle': Nav_PolarizationAngle,
            'Nav_SatelliteTxPolarization': Nav_SatelliteTxPolarization,
            'Nav_TxElevationHysteresis': Nav_TxElevationHysteresis,
            'Nav_TxMinimumElevation': Nav_TxMinimumElevation,
            'Nav_TxSkewAngle': Nav_TxSkewAngle,
            'Nav_TxSkewHysteresis': Nav_TxSkewHysteresis,
            'Nav_TxSkewLimit': Nav_TxSkewLimit,
            'Ant_Flap4Offset': Ant_Flap4Offset,
            'Ant_Flap3Offset': Ant_Flap3Offset,
            'Ant_Flap2Offset': Ant_Flap2Offset,
            'Ant_Flap1Offset': Ant_Flap1Offset,
            'Ant_GIVFlapCode': Ant_GIVFlapCode
            } 

        self.generalSet('TerminalStatus', data_terminal_ACU, False)

        if len(kwargs):
            print ("\nWarning: Detected new Terminal ACU status paramters [{}]\n".format(kwargs))



    ############################################################################
    # Gets and returns the Terminal ACU Status from the database
    ############################################################################
    def aldbStatusTerminalACUGet(self):
        return self.generalGet('TerminalStatus', ['pollTime', 
            'ACU_ACUQueryRespMsgICDVersion',
            'ACU_ACUTXInhibit',
            'ACU_AircraftType',
            'ACU_AircraftTypeFromACU',
            'ACU_AntRcvParamRespMsgICDVersion',
            'ACU_AntStatusRespMsgICDVersion',
            'ACU_CalculatedHeading',
            'ACU_CalculatedPitch',
            'ACU_CalculatedRoll',
            'ACU_FirmwareVersion',
            'ACU_GatewayIPAddress',
            'ACU_HardwarePartNum',
            'ACU_HardwareSerialNum',
            'ACU_IPAddress',
            'ACU_IPAddressMask',
            'ACU_NavDataCh1Bad',
            'ACU_NavDataCh1Good',
            'ACU_NavDataCh2Bad',
            'ACU_NavDataCh2Good',
            'ACU_Port',
            'ACU_RSSIRate',
            'ACU_SoftwarePartNum',
            'ACU_SoftwareVersion',
            'ACU_State',
            'ACU_StatusMessageRate',
            'ACU_Temperature',
            'ACU_Type',
            'ACU_Uptime',
            'ACU_VMTConfigCmdMsgICDVersion',
            'Ant_AntennaMountOrientation',
            'Ant_AntennaState',
            'Ant_AzimuthErrorLimit',
            'Ant_ElevationErrorLimit',
            'Ant_HorizStabilizerPos',
            'Ant_LNBSelect',
            'Ant_MainFirmwareVersion',
            'Ant_ModelNum',
            'Ant_MotorControllerFWVer',
            'Ant_PartNum',
            'Ant_PlatformPitchOffset',
            'Ant_PlatformRollOffset',
            'Ant_PlatformYawOffset',
            'Ant_PolarizationErrorLimit',
            'Ant_RFFirmwareVersion',
            'Ant_SerialNum',
            'Ant_SkewMotorCtrlFWVer',
            'Ant_Type',
            'Nav_Altitude',
            'Nav_SatelliteLongitude',
            'Nav_SatellitePolarization'
            'Nav_SatellitePolarizationCant',
            'Nav_SatelliteRxPolarization',
            'ACU_ACUDroppedMsgCount',
            'ACU_ACUIPLVersion',
            'ACU_ACUPartialMsgCount',
            'ACU_ACUPOSTStatus',
            'ACU_ACUPowerCycles',
            'ACU_ACUPowerInterruptions',
            'ACU_ACUTime',
            'ACU_AlarmStatus',
            'ACU_ETI',
            'ACU_HPAPower',
            'ACU_SoftwareStatus',
            'Ant_AntennaCommStatus',
            'Ant_BaseTemperature',
            'Ant_ETI',
            'Ant_SensorCalibrationStatus',
            'Ant_SensorCalTableStatus',
            'Ant_SlipDetection',
            'Ant_SlipsCounted',
            'Ant_TrackingState',
            'Nav_AbsAzimuth',
            'Nav_AbsElevation',
            'Nav_AbsPolarization',
            'Nav_AzimuthPositionError',
            'Nav_AzimuthSteps',
            'Nav_ElevationPositionError',
            'Nav_ElevationSteps',
            'Nav_Latitude',
            'Nav_Longitude',
            'Nav_PolarizationPositionError',
            'Nav_PolarizationSteps',
            'Nav_SatelliteAzimuth',
            'Nav_SatelliteElevation',
            'Nav_TrueHeading',
            'ACU_ACUBlockageEnableStatus',
            'ACU_ACUBlockageTblLoadedStatus',
            'ACU_ACUSquintEnableStatus',
            'ACU_ACUSquintTblLoadedStatus',
            'ACU_ACUTXLockoutAlarm',
            'ACU_AircraftFlightTime',
            'ACU_AircraftTakeoffs',
            'ACU_IFCSummaryAlarm',
            'ACU_ProcessRestartCount',
            'ACU_RSSIStatus',
            'ACU_SquintTableInUse',
            'Ant_AntennaInputCurrent',
            'Ant_AntennaInputVoltage',
            'Ant_AntennaTxInhibitStatus',
            'Ant_AvgAZELMotorTemperature',
            'Ant_AvgAZELMotorVoltage',
            'Ant_AZMotorPosition',
            'Ant_ELMotorPosition',
            'Ant_RateSensorAvgAccel',
            'Ant_RateSensorPeakAccel',
            'Ant_RxBandSettings',
            'Ant_RxFrequency',
            'Ant_SSPALeftFanSpeed',
            'Ant_SSPAPowerStatus',
            'Ant_SSPARightFanSpeed',
            'Ant_StepTrackPaused',
            'Ant_TxBandSettings',
            'Ant_TxFrequency',
            'Nav_PolarizationAngle',
            'Nav_SatelliteTxPolarization',
            'Nav_TxElevationHysteresis',
            'Nav_TxMinimumElevation',
            'Nav_TxSkewAngle',
            'Nav_TxSkewHysteresis',
            'Nav_TxSkewLimit',
            'Ant_Flap4Offset',
            'Ant_Flap3Offset',
            'Ant_Flap2Offset',
            'Ant_Flap1Offset',
            'Ant_GIVFlapCode'
            ],termGui)


    ############################################################################
    # Sets the configuration for the NLG task details in the database.
    ############################################################################
    def aldbConfNlgSet(self, pid, active):
        data_nlg = { 'groupId': self.groupId, 'pid': pid, 'active': active }
        self.generalSet('NlgConf', data_nlg, True)

    ############################################################################
    # Gets the configuration for the NLG task from the database
    ############################################################################
    def aldbConfNlgGet(self):
        default = { }
        getList = ['pid', 'active' ]
        return self.generalGet('NlgConf', getList, default)

    ##########################################################################
    # aldbExportToCsv
    #   Create a Csv File from DB table
    ##########################################################################
    def aldbExportToCsv(self,outFile,tableName,keyName,keyStart,keyEnd):

        # Tuneable "page size" parameter for indicating num records per access
        pageSize = 10

        # Get Table column names and put into a list
        result = self.getTable('information_schema.columns', ['column_name'], dict(table_name=tableName))
        columnNames = [li['column_name'] for li in result]

        # Create File and write the header row 
        # (setting fieldnames ensures correct column placement)
        csvwfilep = open(outFile,'w')
        csvw = csv.DictWriter(csvwfilep, fieldnames=columnNames)
        csvw.writeheader()

        # Determine the number of rows to be read
        constraint = " WHERE groupId=" + str(self.groupId) + " AND " + keyName + " >= '"+ str(keyStart) +"' AND " + str(keyName) + " <= '" + str(keyEnd) +"'"
        result = self.getTable(tableName,['COUNT(*)'],extraConstraint=constraint)
        # numRows = [li['COUNT(*)'] for li in result][0] 
        numRows = result[0]['COUNT(*)']

        # Get data within range of the key values (one page at a time) and dump to csv file
        numPages = (numRows/pageSize)
        if (numRows % pageSize):
            numPages += 1
        start = keyStart
        comp = " >= "
        loop = 1
        for page in range(0, numPages):
           loop += 1
           constraint = " WHERE groupId=" + str(self.groupId) + " AND " + keyName + comp  + "'" + str(start) +"' AND " + keyName + " <= '" + str(keyEnd) + "' ORDER BY " + keyName + " LIMIT " +  str(pageSize)
           result = self.getTable(tableName, columnNames, extraConstraint=constraint)
           csvw.writerows(result)
           comp =" > "
           start = result[len(result)-1][keyName]

    ############################################################################
    # Sets the configuration for the RTNMS in the database
    # TODO - Add RTNMS management screens; 
    #  currently static for Snowshoe, Sugarloaf, Wintergreen, and TA Hub EMS 
    ############################################################################
    def aldbConfRtnmsSet(self, ip=rtnms['ip'], hubname=rtnms['hubName'],
        usern=rtnms['usern'], passw=rtnms['passw']):
        data_Rtnms = {
                'zoneId': 0,
                'ip': ip,
                'hubName': hubname,
                'usern': usern,
                'passw': passw,
        }
        self.setTable('RtnmsConf', data_Rtnms)

    ############################################################################
    # Gets and returns the configuration for the NMS/EMS Gui form the database
    ############################################################################
    def aldbConfRtnmsGet(self, hubname):
        result = self.getTable('RtnmsConf', ['zoneId', 'ip', 'hubName', 'usern', 'passw'], whereDict=dict(hubName=hubname))
        return result[0]

    ############################################################################
    # Sets the Description configuration for the Group in the database
    ############################################################################
    def aldbConfGroupSet(self, testc=grp['TestCase'], descr=grp['Description'], station=grp['StationName']):
        data_grp = { 'TestCase': testc, 'Description': descr, 'StationName': station }
        self.updateGroupConfig(self.groupId, data_grp)

    ############################################################################
    # Gets and returns the configuration for the NMS/EMS Gui form the database
    ############################################################################
    def aldbConfGroupGet(self):
        result = self.getTable('GroupInfo', ['TestCase', 'Description', 'StationName'], extraConstraint="WHERE GrpID="+str(self.groupId))
        if len(result):
            return result[0]
        else:
            return grp

