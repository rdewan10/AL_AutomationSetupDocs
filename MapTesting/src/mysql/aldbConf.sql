--
-- Current Database: `performance`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `performance` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `performance`;


--
-- Table structure for table `MapBun`
--
DROP TABLE IF EXISTS `MapBun`;
CREATE TABLE `MapBun` (
  `groupId` int(11) NOT NULL ,
  `filename` varchar(36),
  `profile` varchar(36),
  `script` varchar(36),
  `satName` varchar(36),
  `bundleVersion` varchar(36),
  PRIMARY KEY  (`groupId`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `MapBun`
--

/*!40000 ALTER TABLE `MapBun` DISABLE KEYS */;
LOCK TABLES `MapBun` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `MapBun` ENABLE KEYS */;

--
-- Table structure for table `NmsGui`
--
DROP TABLE IF EXISTS `NmsGui`;
CREATE TABLE `NmsGui` (
  `groupId` int(11) NOT NULL ,
  `ip` varchar(36),
  `port` int(11),
  `usern` varchar(36),
  `passw` varchar(36),
  PRIMARY KEY  (`groupId`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `NmsGui`
--

/*!40000 ALTER TABLE `NmsGui` DISABLE KEYS */;
LOCK TABLES `NmsGui` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `NmsGui` ENABLE KEYS */;

/*!40000 ALTER TABLE `MapBun` DISABLE KEYS */;
LOCK TABLES `MapBun` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `MapBun` ENABLE KEYS */;

--
-- Table structure for table `TermGui`
--
DROP TABLE IF EXISTS `TermGui`;
CREATE TABLE `TermGui` (
  `groupId` int(11) NOT NULL ,
  `ip` varchar(36),
  `port` int(11),
  `usern` varchar(36),
  `passw` varchar(36),
  `name` varchar(36),
  `CLI` enum('Console', 'SSH'),
  `consolePort` varchar(36),
  PRIMARY KEY  (`groupId`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `TermGui`
--

/*!40000 ALTER TABLE `TermGui` DISABLE KEYS */;
LOCK TABLES `TermGui` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `TermGui` ENABLE KEYS */;

/*!40000 ALTER TABLE `MapBun` DISABLE KEYS */;
LOCK TABLES `MapBun` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `MapBun` ENABLE KEYS */;

--
-- Table structure for table `MapBunDetailed`
--
DROP TABLE IF EXISTS `MapBunDetailed`;
CREATE TABLE `MapBunDetailed` (
  `groupId` int(11) NOT NULL ,
  `signed` tinyint(1) NOT NULL ,
  `sedVersion` varchar(36),
  `sscfVersion` varchar(36),
  `rlcVersion` varchar(36),
  `gdrmVersion` varchar(36),
  `sedmd5` varchar(32),
  `sscfmd5` varchar(32),
  `rlcmd5` varchar(32),
  `gdrmmd5` varchar(32),
  `satName` varchar(36),
  `satId` varchar(36),
  `satLong` varchar(16),
  `polarity` varchar(4),
  `flTxFreq` int(11),
  `flRxFreq` int(11),
  `flChipRate` int(11),
  `pilot` varchar(4),
  `rolloff` varchar(4),
  `antennaType` varchar(36),
  PRIMARY KEY  (`groupId`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `MapBunDetailed`
--

/*!40000 ALTER TABLE `MapBunDetailed` DISABLE KEYS */;
LOCK TABLES `MapBunDetailed` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `MapBunDetailed` ENABLE KEYS */;

--
-- Table structure for tabe TuningConf
--

DROP TABLE IF EXISTS `TuningConf`;
CREATE TABLE `TuningConf` (
    `groupId` int(11) NOT NULL,
    `precedenceDwell` int(11),
    `defaultBitRate` int(11),
    `dnldBitRatePercent` int(11),
    `flRxFreq` int(11),
    PRIMARY KEY (`groupId`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

/*!40000 ALTER TABLE `TuningConf` DISABLE KEYS */;
LOCK TABLES `TuningConf` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `TuningConf` ENABLE KEYS */;

--
-- Table structure for table `Hubs`
--
DROP TABLE IF EXISTS `Hubs`;
CREATE TABLE `Hubs` (
   `groupId` int(11) NOT NULL ,
   `hub1Name` varchar(40) default NULL,
   `hub2Name` varchar(40) default NULL,
  PRIMARY KEY  (`groupId`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `Hubs`
--

/*!40000 ALTER TABLE `Hubs` DISABLE KEYS */;
LOCK TABLES `Hubs` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `Hubs` ENABLE KEYS */;


--
-- Table structure for table `RtnmsConf`
--
DROP TABLE IF EXISTS `RtnmsConf`;
CREATE TABLE `RtnmsConf` (
   `zoneId` int(11) default 0,
   `ip` varchar(36),
   `hubName` varchar(40),
   `usern` varchar(36),
   `passw` varchar(36),
  PRIMARY KEY  (`hubName`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `RtnmsConf`
--

/*!40000 ALTER TABLE `RtnmsConf` DISABLE KEYS */;
LOCK TABLES `RtnmsConf` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `RtnmsConf` ENABLE KEYS */;


