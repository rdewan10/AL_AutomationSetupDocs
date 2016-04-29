--
-- Current Database: `performance`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `performance` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `performance`;

--
-- Table structure for table `Browser`
--

DROP TABLE IF EXISTS `Browser`;
CREATE TABLE `Browser` (
  `BrowserID` int(11) NOT NULL auto_increment,
  `Browser` varchar(40) NOT NULL,
  `Version` varchar(20) default NULL,
  `Connections` int(11) default NULL,
  PRIMARY KEY  (`BrowserID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `Browser`
--


/*!40000 ALTER TABLE `Browser` DISABLE KEYS */;
LOCK TABLES `Browser` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `Browser` ENABLE KEYS */;

--
-- Table structure for table `CPE`
--

DROP TABLE IF EXISTS `CPE`;
CREATE TABLE `CPE` (
  `CpeID` int(11) NOT NULL auto_increment,
  `OS` varchar(40) default NULL,
  `RAM` int(11) default NULL,
  `MAC` varchar(20) default NULL,
  `CPU` varchar(30) default NULL,
  `Brand` varchar(40) default NULL,
  `Description` text,
  PRIMARY KEY  (`CpeID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `CPE`
--


/*!40000 ALTER TABLE `CPE` DISABLE KEYS */;
LOCK TABLES `CPE` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `CPE` ENABLE KEYS */;

--
-- Table structure for table `CpeTimeSeries`
--

DROP TABLE IF EXISTS `CpeTimeSeries`;
CREATE TABLE `CpeTimeSeries` (
  `Datetime` datetime NOT NULL,
  `CpuUtilization` float(5,2) default NULL,
  `RamUtilization` float(5,2) default NULL,
  `GrpID` int(11) NOT NULL,
  PRIMARY KEY  (`Datetime`,`GrpID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `CpeTimeSeries`
--


/*!40000 ALTER TABLE `CpeTimeSeries` DISABLE KEYS */;
LOCK TABLES `CpeTimeSeries` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `CpeTimeSeries` ENABLE KEYS */;

--
-- Table structure for table `GroupInfo`
--

DROP TABLE IF EXISTS `GroupInfo`;
CREATE TABLE `GroupInfo` (
  `GrpID` int(11) NOT NULL auto_increment,
  `Results` varchar(60) default NULL,
  `Datetime` datetime default NULL,
  `DurationHrs` float(5,2) default NULL,
  `GroupName` varchar(40) default NULL,
  `StationName` varchar(40) default NULL,
  `StationType` varchar(40) default NULL,
  `User` varchar(40) default NULL,
  `TestCase` varchar(80) default NULL,
  `TestTool` varchar(40) default NULL,
  `Product` varchar(40) default NULL,
  `CpeID` int(11) default NULL,
  `BrowserID` int(11) default NULL,
  `Status` enum('complete', 'running', 'invalid') default NULL,
  `SpecPassFail` enum('pass', 'fail') default NULL,
  `Description` text,
  `Notes` text,
  PRIMARY KEY  (`GrpID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `GroupInfo`
--


/*!40000 ALTER TABLE `GroupInfo` DISABLE KEYS */;
LOCK TABLES `GroupInfo` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `GroupInfo` ENABLE KEYS */;

--
-- Table structure for table `ObjectTime`
--

DROP TABLE IF EXISTS `ObjectTime`;
CREATE TABLE `ObjectTime` (
  `ObjID` int(11) NOT NULL auto_increment,
  `PageID` int(11) NOT NULL,
  `Type` varchar(40) default NULL,
  `ObjURL` varchar(256) default NULL,
  `ObjSize` int(11) default NULL,
  `ObjHttpResponse` int(11) default NULL,
  PRIMARY KEY  (`ObjID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `ObjectTime`
--


/*!40000 ALTER TABLE `ObjectTime` DISABLE KEYS */;
LOCK TABLES `ObjectTime` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `ObjectTime` ENABLE KEYS */;

--
-- Table structure for table `PageTime`
--

DROP TABLE IF EXISTS `PageTime`;
CREATE TABLE `PageTime` (
  `PageID` int(11) NOT NULL auto_increment,
  `TestID` int(11) NOT NULL,
  `Datetime` datetime default NULL,
  `URL` varchar(256) default NULL,
  `Size` int(11) default NULL,
  `Objects` int(11) default NULL,
  `HttpResponse` int(11) default NULL,
  `LoadTime` int(11) default NULL,
  `DownloadBytes` int(11) default NULL,
  `UploadBytes` int(11) default NULL,
  `AcceleratedLoadTime` int(11) default NULL,
  `AcceleratedDownloadBytes` int(11) default NULL,
  `AccelearatedUploadBytes` int(11) default NULL,
  PRIMARY KEY  (`PageID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `PageTime`
--


/*!40000 ALTER TABLE `PageTime` DISABLE KEYS */;
LOCK TABLES `PageTime` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `PageTime` ENABLE KEYS */;

--
-- Table structure for table `PerfCheckConfig`
--

DROP TABLE IF EXISTS `PerfCheckConfig`;
CREATE TABLE `PerfCheckConfig` (
  `PerfCheckID` int(11) NOT NULL auto_increment,
  `TestID` int(11) NOT NULL,
  `NumReps` int(11) default NULL,
  `Timeout` int(11) default NULL,
  `ConnectionType` varchar(20) default NULL,
  `RestartClient` tinyint(1) default NULL,
  `ClearDeltaCache` tinyint(1) default NULL,
  `DelayBetweenSites` int(11) default NULL,
  `DownloadMaxThroughput` int(11) default NULL,
  `DownloadAvgThroughput` int(11) default NULL,
  `UploadMaxThroughput` int(11) default NULL,
  `UploadAvgThroughput` int(11) default NULL,
  `UnaccelDownloadMaxThroughput` int(11) default NULL,
  `UnaccelDownloadAvgThroughput` int(11) default NULL,
  `UnaccelUploadMaxThroughput` int(11) default NULL,
  `UnaccelUploadAvgThroughput` int(11) default NULL,
  `TxBw` int(11) default NULL,
  `RxBw` int(11) default NULL,
  `TxDelay` int(11) default NULL,
  `RxDelay` int(11) default NULL,
  `TxPacketLoss` int(11) default NULL,
  `RxPacketLoss` int(11) default NULL,
  PRIMARY KEY  (`PerfCheckID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `PerfCheckConfig`
--


/*!40000 ALTER TABLE `PerfCheckConfig` DISABLE KEYS */;
LOCK TABLES `PerfCheckConfig` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `PerfCheckConfig` ENABLE KEYS */;

--
-- Table structure for table `PerfCheckResults`
--

DROP TABLE IF EXISTS `PerfCheckResults`;
CREATE TABLE `PerfCheckResults` (
  `PageID` int(11) NOT NULL auto_increment,
  `PerfCheckID` int(11) NOT NULL,
  `URL` varchar(256) NOT NULL,
  `DownloadTime` int(11) NOT NULL,
  `UnaccelDownloadTime` int(11) NOT NULL,
  `DownloadBytes` int(11) NOT NULL,
  `UnaccelDownloadBytes` int(11) NOT NULL,
  `UploadBytes` int(11) NOT NULL,
  `UnaccelUploadBytes` int(11) NOT NULL,
  PRIMARY KEY  (`PageID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `PerfCheckResults`
--


/*!40000 ALTER TABLE `PerfCheckResults` DISABLE KEYS */;
LOCK TABLES `PerfCheckResults` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `PerfCheckResults` ENABLE KEYS */;

--
-- Table structure for table `PerfCheckSiteInfo`
--

DROP TABLE IF EXISTS `PerfCheckSiteInfo`;
CREATE TABLE `PerfCheckSiteInfo` (
  `PageID` int(11) NOT NULL auto_increment,
  `PerfCheckID` int(11) NOT NULL,
  `URL` varchar(256) NOT NULL,
  `AccelenetTime` int(11) NOT NULL,
  `UnacceleratedTime` int(11) NOT NULL,
  `AccelenetDownloadBytes` int(11) NOT NULL,
  `UnacceleratedDownloadBytes` int(11) NOT NULL,
  `AccelenetUploadBytes` int(11) NOT NULL,
  `UnacceleratedUploadByes` int(11) NOT NULL,
  `Acceleration` int(11) default NULL,
  `DownloadCompressionRatio` int(11) default NULL,
  `UploadCompressionRatio` int(11) default NULL,
  PRIMARY KEY  (`PageID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `PerfCheckSiteInfo`
--


/*!40000 ALTER TABLE `PerfCheckSiteInfo` DISABLE KEYS */;
LOCK TABLES `PerfCheckSiteInfo` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `PerfCheckSiteInfo` ENABLE KEYS */;

--
-- Table structure for table `PerfCheckTestSegnmentInfo`
--

DROP TABLE IF EXISTS `PerfCheckTestSegnmentInfo`;
CREATE TABLE `PerfCheckTestSegnmentInfo` (
  `PerfCheckID` int(11) NOT NULL auto_increment,
  `TestSegmentName` varchar(80) default NULL,
  `SiteList` varchar(256) default NULL,
  `NumReps` int(11) default NULL,
  `CompletedReps` int(11) default NULL,
  `Timeout` int(11) default NULL,
  `BrowserWaitTime` int(11) default NULL,
  `ConnectionType` varchar(256) default NULL,
  `RestartClient` tinyint(1) default NULL,
  `ClearDeltaCache` tinyint(1) default NULL,
  `ClearDnsCache` tinyint(1) default NULL,
  `NoAcceleNet` tinyint(1) default NULL,
  `DelayBetweenSites` int(11) default NULL,
  `DownloadMaxThroughput` int(11) default NULL,
  `DownloadAvgThroughput` int(11) default NULL,
  `UploadMaxThroughput` int(11) default NULL,
  `UploadAvgThroughput` int(11) default NULL,
  `UnaccelDownloadMaxThroughput` int(11) default NULL,
  `UnaccelDownloadAvgThroughput` int(11) default NULL,
  `UnaccelUploadMaxThroughput` int(11) default NULL,
  `UnaccelUploadAvgThroughput` int(11) default NULL,
  `UploadBandwidth` int(11) default NULL,
  `Downloadbandwidth` int(11) default NULL,
  `RTT` int(11) default NULL,
  `PacketLoss` int(11) default NULL,
  PRIMARY KEY  (`PerfCheckID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `PerfCheckTestSegnmentInfo`
--


/*!40000 ALTER TABLE `PerfCheckTestSegnmentInfo` DISABLE KEYS */;
LOCK TABLES `PerfCheckTestSegnmentInfo` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `PerfCheckTestSegnmentInfo` ENABLE KEYS */;

--
-- Table structure for table `TestInfo`
--

DROP TABLE IF EXISTS `TestInfo`;
CREATE TABLE `TestInfo` (
  `TestID` int(11) NOT NULL,
  `GrpID` int(11) NOT NULL,
  `Status` enum('complete', 'running', 'invalid') default NULL,
  `Datetime` datetime default NULL,
  `DurationHrs` float(5,2) default NULL,
  PRIMARY KEY  (`TestID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `TestInfo`
--


/*!40000 ALTER TABLE `TestInfo` DISABLE KEYS */;
LOCK TABLES `TestInfo` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `TestInfo` ENABLE KEYS */;

--
-- Table structure for table `Webtimer`
--

DROP TABLE IF EXISTS `Webtimer`;
CREATE TABLE `Webtimer` (
  `PageTimeID` int(11) NOT NULL auto_increment,
  `TestID` int(11) NOT NULL,
  `DwellTime` int(11) default NULL,
  `PageTimeout` int(11) default NULL,
  PRIMARY KEY  (`PageTimeID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `Webtimer`
--


/*!40000 ALTER TABLE `Webtimer` DISABLE KEYS */;
LOCK TABLES `Webtimer` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `Webtimer` ENABLE KEYS */;

--
-- Table structure for table `queries`
--

DROP TABLE IF EXISTS `queries`;
CREATE TABLE `queries` (
  `ID` int(11) NOT NULL auto_increment,
  `query` text NOT NULL,
  `description` text NOT NULL,
  `times_used` int(11) NOT NULL,
  PRIMARY KEY  (`ID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `queries`
--



/*!40000 ALTER TABLE `queries` DISABLE KEYS */;
LOCK TABLES `queries` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `queries` ENABLE KEYS */;
