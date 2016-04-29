<?php
/*
 * ---------------------------------------------------------------
 *
 * File:  report.php
 *
 * Classification:  UNCLASSIFIED
 *
 * Copyright (C) 2013 ViaSat, Inc.
 *
 * All rights reserved.
 * The information in this software is subject to change without notice and
 * should not be construed as a commitment by ViaSat, Inc.
 *
 * ViaSat Proprietary
 * The information provided herein is proprietary to ViaSat and
 * must be protected from further distribution and use. Disclosure to others,
 * use or copying without express written authorization of ViaSat, is strictly
 * prohibited.
 *
 * ---------------------------------------------------------------
 */
?>
<?php
/******************************************************************************
 *
 & Filename: report.php
 * Purpose: A test report page. This page was made especially for surfbeam and
 *          leapfrog and will not work for other projects without major
 *          modifications. However, this page is the pinnacle of reda report
 *          due to it's abilit to condense information into a readable summary.
 *          In order to achieve this, however, a lot of project specific
 *          customization had to be made.
 *
 *****************************************************************************/

include 'func.php';
mysqlSetup($db);

//This function is responsible for displaying all of the IxOs section for
//a particular testID.
function ixos ($testID,$testIndex,$ixOsIndex, $grpID){

  global $db;
/*
  $result = mysql_query("SELECT GrpID FROM TestInfo WHERE TestID=$testID",$db);
  $grpIDRow = mysql_fetch_row($result);
  $grpID = $grpIDRow[0];
*/
    mysqlSetup($db); //I have to set it up again, unfortunately.
    ?>
    <p><b><?php echo "<a name=\"$testID" . "_ixos\"></a>$testIndex.$ixOsIndex"; ?> IxOS Data</b></p>
    <br><p>
    <?php

    //Get data from the IxOs table
    $query="SELECT * FROM IxOs WHERE TestID=$testID AND GrpID=$grpID ORDER BY TrafficDirection,IxOsID ASC";
    $result = mysql_query($query,$db);
    $index = 0;
    while ($col[$index] = mysql_fetch_row($result)){
      $index++;
    }
    echo "<table>";
    for ($i = 0; $i < mysql_num_fields($result);$i++){
      if(mysql_field_name($result, $i)!="TestID" && mysql_field_name($result, $i)!="GrpID" && mysql_field_name($result, $i) !="SeqErrors"){
        printf("<tr><td><p>%s</p></td>",mysql_field_name($result, $i));
        for ($j = 0; $j < count($col); $j++) {
          printf("<td><p>%s</p></td>",$col[$j][$i]);
        }
        printf("</tr>");
      }//if
    }//for
    ?>
    </table>
    </p><br>
    <?php
/*
    $result = mysql_query("SELECT GrpID FROM TestInfo WHERE TestID=$testID",$db);
    $temprow = mysql_fetch_row($result);
    $grpID = $temprow[0];
*/
    ?>
    <p><b><?php echo "<a name=\"$testID" . "_ixos\"></a>$testIndex.$ixOsIndex"; ?>.1 IxOS Plots</b></p>
    <br>
    <?php
    //Display the plots...
    $snmpQuery="SELECT PicName,TextAbove,TextBelow FROM TestReportPictureAnnotation WHERE SubDir=\"ixos\"";
    $result = mysql_query($snmpQuery,$db);
    while($picInfo= mysql_fetch_row($result)){
      $filename="/results/" . $grpID . "/ixos/IxOsTimeSeries_" . $grpID . "_" . $testID;
      $filename .="_" . $picInfo[0];
      if(file_exists("/data" . $filename)){
        echo "<table width=\"1024px\"><tr><td><p><center>" . $picInfo[1] . "</center></p><p><center>" . $picInfo[2] . "</center></p></td></tr><tr><td>";
        $img = $filename;
        echo "<a href=\"$img\"><img src=\"$img\" BORDER=0></a></td></tr></table><br><br><br><br>";
      } else {
        echo "no file exists at /data",$filename;
      }
    }
}//ixos

if($_GET != NULL){
  while(list($key, $value) = each($_GET)){
    $input[$key] = $value;
  }
}
?>
<HTML>
<head>
<link rel="stylesheet" type="text/css" href="reda.css">
<link rel="stylesheet" type="text/css" href="vipcat-style.min.css" title="vipcat-style">
<script type="text/javascript" src="vipcat-bundle.min.js"></script>
<?php
//If a testID is provided instead of a group id, this page will redirect.
if(isset($input["testID"])){
  $result = mysql_query("SELECT GrpID FROM TestInfo WHERE TestID=" . $input["testID"],$db);
  $grpID_row = mysql_fetch_row($result);
  echo "<META HTTP-EQUIV=\"Refresh\" CONTENT=\"0; URL=http://reda.viasat.com/report.php?grpID=" . $grpID_row[0] . "#" . $input["testID"] . "\">";
}

?>
<title>Reda Test Report - GrpID <?php echo "$projectName  ${input['grpID']}"; ?></title>
</head>
<?php
bodyStyle();
banner();
navbar1("report");

if($input["grpID"]!=NULL){
  ?>
  <a name="top"></a>
  <center><h2>&nbsp;</h2><h2>GrpID <?php echo "$projectName  ${input['grpID']}"; ?></h2></center>
  <div class="post"><div class="toplink">
  <?php
  //This section will happen a lot. Basically these two are links to on the right side of each
  //section's header.
  if(!isset($input["hide_toc"])){
    echo "<a href='" . $_SERVER['REQUEST_URI'] . "&hide_toc=1#exec'>Collapse Section</a>";
  } else {
    echo "<a href='" . str_replace("&hide_toc=1","",$_SERVER['REQUEST_URI']) . "#exec'>Expand Section</a>";
  }
  ?>
  | <a href="#top">Back to Top</a></div>
  <h1>Table of Contents</h1>
<?php
if(!isset($input["hide_toc"])){
?>
  <p><a href="#exec">1. Executive Summary</a></p>
  <p>&nbsp;&nbsp;&nbsp;&nbsp;<a href="#exec">1.1 Test Run Summary</a></p>
  <p>&nbsp;&nbsp;&nbsp;&nbsp;<a href="#execVersions">1.2 Versions</a></p>
  <p>&nbsp;&nbsp;&nbsp;&nbsp;<a href="#execSteps">1.3 Test Case Steps</a></p>
  <p>&nbsp;&nbsp;&nbsp;&nbsp;<a href="#execVP">1.4 Verification Points</a></p>
  <p><a href="#groupAnalysis">2. Group Analysis</a></p>
  <?php
  $tocIndex=1;

  //<p>&nbsp;&nbsp;&nbsp;&nbsp;<a href="#groupConsole">2.$tocIndex SMTS Console Log Summary</a></p>
  //$tocIndex++;
  
  //<p>&nbsp;&nbsp;&nbsp;&nbsp;<a href="#groupConsole">2.$tocIndex SM Console Log Summary</a></p>
  //$tocIndex++;

  //Look into the results folder and see if we can get some pictures.
  if(file_exists("results/" . $input["grpID"] . "/snmp/analysis")){
    echo "<p>&nbsp;&nbsp;&nbsp;&nbsp;<a href=\"#snmp\">2.$tocIndex Snmp Plots</a></p>\n";
    echo "<p>&nbsp;&nbsp;&nbsp;&nbsp;<a href=\"#snmpSignal\">2.$tocIndex.1 Signal Levels</a></p>\n";
    echo "<p>&nbsp;&nbsp;&nbsp;&nbsp;<a href=\"#snmpTraffic\">2.$tocIndex.2 Traffic</a></p>\n";
    $tocIndex++;
  } 
  if(file_exists("results/" . $input["grpID"] . "/top")){
    echo "<p>&nbsp;&nbsp;&nbsp;&nbsp;<a href=\"#top_plots\">2.$tocIndex Top Plots</a></p>\n";
    $tocIndex++;
  } 
  if(file_exists("results/" . $input["grpID"] . "/ixos")){
    echo "<p>&nbsp;&nbsp;&nbsp;&nbsp;<a href=\"#ixos\">2.$tocIndex IxOS Summary Plots</a></p>\n";
    $tocIndex++;
  } 
	  if(file_exists("results/" . $input["grpID"] . "/spd_chk")){
    echo "<p>&nbsp;&nbsp;&nbsp;&nbsp;<a href=\"#spd_chk\">2.$tocIndex Speed Check Plots</a></p>\n";
    $tocIndex++;
	  }
   
  $result = mysql_query("SELECT TestID,TestCase FROM TestInfo WHERE GrpID=" . $input["grpID"] . " ORDER BY TestID ASC",$db);
  $tocIndex=3;
  while($singleTestInfo=mysql_fetch_row($result)){
    $tocInnerIndex=1;
    echo "<p><a href=\"#" . $singleTestInfo[0] . "\">$tocIndex. TestID " . $singleTestInfo[0] . " - " .  $singleTestInfo[1] . "</a></p>\n";
    echo "<p>&nbsp;&nbsp;&nbsp;&nbsp;<a href=\"#" . $singleTestInfo[0] . "_info\">$tocIndex.$tocInnerIndex Test Information</a></p>\n";
    $tocInnerIndex++;
    //echo "<p>&nbsp;&nbsp;&nbsp;&nbsp;<a href=\"#" . $singleTestInfo[0] . "_smts\">$tocIndex.$tocInnerIndex SMTS Configuration</a></p>\n";
    //$tocInnerIndex++;
    $existsIxOsResult = mysql_query("SELECT * FROM IxOs WHERE GrpID=" . $input["grpID"] . " AND TestID=" . $singleTestInfo[0],$db);
    if(mysql_fetch_row($existsIxOsResult)){
      echo "<p>&nbsp;&nbsp;&nbsp;&nbsp;<a href=\"#" . $singleTestInfo[0] . "_ixos\">$tocIndex.$tocInnerIndex. IxOS</a></p>\n";
      $tocInnerIndex++;
    }
    $tocIndex++;
  }
  
  echo "<p><a href=\"#dataVisualizations\">$tocIndex. Data Visualizations</a></p>";
  
  ?>
  <br><br>
<?php
}
?>
  </div>
  <div class="post"><div class="toplink">
  <?php
  //This section will happen a lot. Basically these two are links to on the right side of each
  //section's header.
  if(!isset($input["hide_exec"])){
    echo "<a href='" . $_SERVER['REQUEST_URI'] . "&hide_exec=1#exec'>Collapse Section</a>";
  } else {
    echo "<a href='" . str_replace("&hide_exec=1","",$_SERVER['REQUEST_URI']) . "#exec'>Expand Section</a>";
  }
  ?>
  | <a href="#top">Back to Top</a></div>
  <a name="exec"></a><h1>1. Executive Summary</h1>
  <?php
  if(!isset($input["hide_exec"])){
  ?>
    <a name="exec"><p><b>1.1 Test Run Summary</b></p>
    <table><tr><td><p><a href="edit.php?grpID=<?php echo $input["grpID"]; ?>">Group Name</a></p></td>
    <?php
    //Display the group information
    $query = "SELECT GroupName,TestCase FROM GroupInfo WHERE GrpID=" . $input["grpID"];
    $result = mysql_query($query,$db);
    $myrow = mysql_fetch_row($result);
    echo "<td><p>" . $myrow[0] . "</p></td></tr>";
    $groupName=$myrow[0];
    ?>
    <tr><td><p><a href="edit.php?grpID=<?php echo $input["grpID"]; ?>">Test Case</a></p></td>
    <?php
    echo "<td><p>" . $myrow[1] . "</p></td></tr>";
    ?>

    <tr><td><p><a href="edit.php?grpID=<?php echo $input["grpID"]; ?>">Description</a></p></td>
    <?php
    $query = "SELECT Description FROM GroupInfo WHERE GrpID=" . $input["grpID"];
    $result = mysql_query($query,$db);
    $myrow = mysql_fetch_row($result);
    echo "<td><p>" . $myrow[0] . "</p></td></tr>";

    $testDesc_result=mysql_query("SELECT Purpose FROM TestReportPurposes WHERE GroupName='" . $groupName . "'",$db);
    $testDesc_row=mysql_fetch_row($testDesc_result);
    $testDesc=$testDesc_row[0];
    if($testDesc==NULL){
      echo "<tr><td><p>Purpose</p></td><td><p>None.</p></td></tr>\n";
    } else {
      echo "<tr><td valign=\"top\"><p>Purpose</p></td><td><p>$testDesc</p></td></tr>\n";
    }

    ?>
    <tr><td>&nbsp;</td></tr>
    <tr><td><p>Test Station</p></td>
    <?php
    $query = "SELECT StationName FROM GroupInfo WHERE GrpID=" . $input["grpID"];
    $result = mysql_query($query,$db);
    $myrow = mysql_fetch_row($result);
    echo "<td><p>" . $myrow[0] . "</p></td></tr>";

    echo "<tr><td><p>Station Type</p></td>";
    $query = "SELECT StationType FROM GroupInfo WHERE GrpID=" . $input["grpID"];
    $result = mysql_query($query,$db);
    $myrow = mysql_fetch_row($result);
    echo "<td><p>" . $myrow[0] . "</p></td></tr>";
  
    $query = "SELECT Status,Datetime,DurationHrs FROM GroupInfo WHERE GrpID=" . $input["grpID"];
    $result = mysql_query($query,$db);
    $myrow = mysql_fetch_row($result);
	
    printf("<tr><td><p><a href=\"edit.php?grpID=" . $input["grpID"] . "\">Status</a></p></td><td><p>%s</p></td></tr>",$myrow[0]);
    printf("<tr><td><p>Start Time</p></td><td><p>%s</p></td></tr>", $myrow[1]);
    printf("<tr><td><p><a href=\"edit.php?grpID=" . $input["grpID"] . "\">Group Duration</a></p></td><td><p>%s hours</p></td></tr>",$myrow[2]);
    $duration = $myrow[2];
    
    ?>
    <tr><td><p>&nbsp;</p></td><td></td></tr>
    <tr><td><p><a href="edit.php?grpID=<?php echo $input["grpID"]; ?>">User</a></p></td>
    <?php
    $query = "SELECT User FROM GroupInfo WHERE GrpID=" . $input["grpID"];
    $result = mysql_query($query,$db);
    $myrow = mysql_fetch_row($result);
    echo "<td><p>" . $myrow[0] . "</p></td></tr>";
    ?>
    <tr><td><p><a href="edit.php?grpID=<?php echo $input["grpID"]; ?>">Pass/Fail</a></p></td>
    <?php
    $query = "SELECT SpecPassFail FROM GroupInfo WHERE GrpID=" . $input["grpID"];
    $result = mysql_query($query,$db);
    $myrow = mysql_fetch_row($result);
    if($myrow[0]=="pass"){
      echo "<td><p class=\"green\">PASS</p></td></tr>";
    } elseif($myrow[0]=="FAIL"){
      echo "<td><p class=\"red\">FAIL</p></td></tr>";
    } else { 
      echo "<td><p>" . $myrow[0] . "</p></td></tr>";
    }
    ?>
    <tr><td><p><a href="edit.php?grpID=<?php echo $input["grpID"]; ?>">User Rating</a></p></td>
    <?php
    $query = "SELECT UserRating FROM GroupInfo WHERE GrpID=" . $input["grpID"];
    $result = mysql_query($query,$db);
    $myrow = mysql_fetch_row($result);
    echo "<td><p>" . $myrow[0] . "</p></td></tr>";
    ?>
    
    <tr><td><p><a href="edit.php?grpID=<?php echo $input["grpID"]; ?>">Notes</a></td>
    <?php

    $query = "SELECT Notes FROM GroupInfo WHERE GrpID=" . $input["grpID"];
    $result = mysql_query($query,$db);
    $myrow = mysql_fetch_row($result);
    echo "<td><p>" . $myrow[0] . "</p></td></tr>";

    ?>
    <?php
    $sxrs =  mysql_query("SELECT SXR FROM RelatedSXRs WHERE GrpID=" . $input["grpID"],$db);
    ?>
    <tr><td><p><a href="edit.php?grpID=<?php echo $input["grpID"]; ?>">JIRAs</a></p></td><td><p>
    <?php
    $singleSXR = mysql_fetch_row($sxrs);
    if($singleSXR[0]==0){
      echo "none";
    }else{
      do {
        //echo $singleSXR[0] . " ";
        echo "<a href=\"http://vcateam01/scripts/texcel/devtrack/BugInfo.dll?OnePage?190&1&" . $singleSXR[0] ."&0&0&0&1\">" . $singleSXR[0] . "</a> ";
      } while($singleSXR = mysql_fetch_row($sxrs));
    }
    ?>
    </p></td></tr>
    
    <!--START OF RELATED TEST FIELD-->
    <tr><td><p><a href="editLinks.php?grpID=<?php echo $input["grpID"]; ?>">Related Groups</a></p></td><td><p>
    <?php
    $links = mysql_query("SELECT LinkedSet FROM GroupInfo WHERE GrpID=" . $input["grpID"],$db);
    $linkId = mysql_fetch_row($links);
    if($linkId[0]!="") {
        $relatedGrpIds = mysql_query("SELECT GrpId FROM GroupInfo WHERE LinkedSet=" . $linkId[0],$db);
        while ($singleGrpId = mysql_fetch_row($relatedGrpIds)) {
            if ($singleGrpId[0] != $input["grpID"]) {
                echo "<a href=\"report.php?grpID=$singleGrpId[0]\">".$singleGrpId[0]."</a> ";
            }
        } 
    } else {
        echo "none";
    }
    ?>    
    
    </p></tr></td>
    <!--END OF RELATED TEST FIELD-->
    <tr><td><p>&nbsp;</p></td><td></td></tr>
    <tr><td><p>Results Directory</p></td>
    <?php

    $query = "SELECT Results FROM GroupInfo WHERE GrpID=" . $input["grpID"];
    $result = mysql_query($query,$db);
    $myrow = mysql_fetch_row($result);
    $resultsDirectory = $myrow[0];
    //echo "<td><p><a href=\"" . $resultsDirectory . "\">" . $resultsDirectory . "</a></p></td></tr>";
    echo "<td><p><a href=\"zipresult.php?grpID=" . $input["grpID"] . "\" style = \"color: #009300\">" . $projectName . "&nbsp;" . $input["grpID"] . "</a></p></td></tr>";
    ?>

	<tr><td><p>Summary Report</p></td>
    <?php
        echo "<td><p><a href=\"redareport.php?grpID=" . $input["grpID"] . "\" style = \"color: #0000FF\">" . $projectName . "&nbsp;" . $input["grpID"] . "</a></p></td></tr>";
    ?>

    </table><br>

    <a name="execVersions"><p><b>1.2 Versions</b></p>
    <?php
    //Get Version information
    $result = mysql_query("SELECT Name,Type,Version FROM VersionInfo WHERE VersionInfo.GrpID=" . $input["grpID"],$db);
    ?>
    <table border="1"><tr><td><p class="center"><b>Component</b></p></td><td><p class="center"><b>Type</b></p></td><td><p><b>Version</b></p></td></tr>
    <?php
    while($versInfo = mysql_fetch_row($result)){
        echo "<tr><td><p>" . $versInfo[0] . "</p></td><td><p class=\"center\">" . $versInfo[1] . "</p></td><td><p>" . $versInfo[2] . "</p></td></tr>";
    }
    ?>
    </table>
    <br>

    <a name="execSteps"><p><b>1.3 Test Case Steps</b></p>
    <?php
    //Get some test information
    $result = mysql_query("SELECT TestInfo.TestID,TestCase,SpecPassFail,Notes FROM TestInfo WHERE TestInfo.GrpID=" . $input["grpID"] . " ORDER BY TestID ASC",$db);
    ?><table border="1"><tr><td><p class="center"><b>Test ID</b></p></td><td><p class="center"><b>Test Case</b></p></td><td><p class="center"><b>Pass/Fail</b></p></td><td><p class="center"><b>Notes</b></p></td></tr>
  <?php
    $testCaseArray = array();
    while($singleTestInfo = mysql_fetch_row($result)){
      echo "<tr><td><p class=\"center\"><a href=\"#" . $singleTestInfo[0] . "\">" . $singleTestInfo[0] . "</a></p></td><td><p class=\"center\">" . $singleTestInfo[1] . "</p></td>";
      $testCaseArray[$singleTestInfo[0]] = $singleTestInfo[1];
      if(strtolower($singleTestInfo[2])=="pass"){
        echo "<td><p class=\"center green\">PASS</p></td>";
      } elseif(strtolower($singleTestInfo[2])=="fail") {
        echo "<td><p class=\"center red\">FAIL</p></td>";
      } else {
        echo "<td><p class=\"center\">" . $singleTestInfo[4] . "</p></td>";
      }
      echo "<td><p>" . $singleTestInfo[3] . "</p></td></tr>";
    }
    ?>
    </table>
    <br>

    <a name="execVP"><p><b>1.4 Verification Points</b></p>
    <?php
    //Display verification points
    $result = mysql_query("SELECT VerificationPoints.TestID,VerificationPoints.Name,VerificationPoints.Result,VerificationPoints.Type,VerificationPoints.ExpectedValue,VerificationPoints.Operator,VerificationPoints.ResultValue,VerificationPoints.Datetime FROM VerificationPoints WHERE VerificationPoints.GrpID=" . $input["grpID"] . " ORDER BY VerificationPoints.Datetime ASC",$db);
    ?><table border="1"><tr><td><p class="center"><b>Timestamp</b></p></td><td><p class="center"><b>Test ID</b></p></td><td><p class="center"><b>Test Case</b></p></td><td><p class="center"><b>Verification Point</b></p></td><td><p class="center"><b>Pass/Fail</b></p></td><td><p class="center"><b>Type</b></p></td><td><p class="center"><b>Expected Value</b></p></td><td><p class="center"><b>Operator</b></p></td><td><p class="center"><b>Result Value</b></p></td></tr>
    <?php
    while($singleVPInfo = mysql_fetch_row($result)){
      echo "<tr><td><p>" . $singleVPInfo[7] . "</p></td>";
      echo "<td><p class=\"center\"><a href=\"#" . $singleVPInfo[0] . "\">" . $singleVPInfo[0] . "</a></p></td><td><p class=\"center\">" . $testCaseArray[$singleVPInfo[0]] . "</p></td><td><p>" . $singleVPInfo[1] . "</p></td>";
      if(strtolower($singleVPInfo[2])=="pass"){
        echo "<td><p class=\"center green\">PASS</p></td>";
      } elseif(strtolower($singleVPInfo[2])=="fail") {
        echo "<td><p class=\"center red\">FAIL</p></td>";
      } else {
        echo "<td><p class=\"center\">" . $singleVPInfo[2] . "</p></td>";
      }
      echo "<td><p class=\"center\">" . $singleVPInfo[3] . "</p></td>";
      echo "<td><p>" . $singleVPInfo[4] . "</p></td>";
      echo "<td><p class=\"center\">" . $singleVPInfo[5] . "</p></td>";
      echo "<td><p>" . $singleVPInfo[6] . "</p></td></tr>";
    }
    ?>
    </table>
    <br>

  <?php
  }
  ?>
  </div>
  </div>
  
  <div class="post"><div class="toplink">
  <?php
  if(!isset($input["hide_groupAnalysis"])){
    echo "<a href='" . $_SERVER['REQUEST_URI'] . "&hide_groupAnalysis=1#groupAnalysis'>Collapse Section</a>";
  } else {
    echo "<a href='" . str_replace("&hide_groupAnalysis=1","",$_SERVER['REQUEST_URI']) . "#groupAnalysis'>Expand Section</a>";
  }
  ?>
  | <a href="#top">Back to Top</a></div>
  <a name="groupAnalysis"></a><h1>2. Group Analysis</h1>
  <?php
  if(!isset($input["hide_groupAnalysis"])){
    $tocIndex=1;
    
    echo "<a name=\"groupConsole\"><p><b>2.$tocIndex Blackboxes</b></p>\n";
    if ($handle = opendir("/opt/share/data/results/" . $input["grpID"] . "/blackboxes")) {
      while (($file = readdir($handle)) !== false) {
        if ($file !== "." && $file !== "..") {
          echo "<table><tr><td><p><a href=\"$resultsDirectory/blackboxes/$file\">$file</a></p></td></tr></table>";
        }
      }
      closedir($dh);
    }

    echo "<br>";

    $tocIndex++;

    echo "<a name=\"groupConsole\"><p><b>2.$tocIndex SMTS Syslog Summary</b></p>\n";
 
    $query = "SELECT File, Message, Count FROM Syslog WHERE GrpID=" . $input["grpID"] . " AND File LIKE \"%smts.syslog\" ORDER BY File,Message";
	$result = mysql_query($query,$db);
	
    echo "<table cellpadding=0 cellspacing=0><tr>";
    for ($i = 0; $i < mysql_num_fields($result);$i++){
      printf("<td><p class=\"tableheader\">&nbsp;&nbsp;%s&nbsp;&nbsp;</p></td>", mysql_field_name($result, $i));
    }
    echo "</tr>";
    while($myrow = mysql_fetch_row($result)){
      printf("<tr><td><p class=\"table\">%s</p></td><td><p class=\"table_left\">%s</p></td><td><p class=\"table\">%s</p></td></tr>", $myrow[0], $myrow[1], $myrow[2]);
    }
    echo "</table>";
    echo "<br>";

    $tocIndex++;

    echo "<a name=\"groupConsole\"><p><b>2.$tocIndex Accel Server Syslog Summary</b></p>\n";
 
    $query = "SELECT File, Message, Count FROM Syslog WHERE GrpID=" . $input["grpID"] . " AND File LIKE \"%ACCEL%%syslog\" ORDER BY File,Message";
	$result = mysql_query($query,$db);
	
    echo "<table cellpadding=0 cellspacing=0><tr>";
    for ($i = 0; $i < mysql_num_fields($result);$i++){
      printf("<td><p class=\"tableheader\">&nbsp;&nbsp;%s&nbsp;&nbsp;</p></td>", mysql_field_name($result, $i));
    }
    echo "</tr>";
    while($myrow = mysql_fetch_row($result)){
      printf("<tr><td><p class=\"table\">%s</p></td><td><p class=\"table_left\">%s</p></td><td><p class=\"table\">%s</p></td></tr>", $myrow[0], $myrow[1], $myrow[2]);
    }
    echo "</table>";
    echo "<br>";

    echo "<table><tr><td><p><a href=\"$resultsDirectory/syslog\">Complete syslogs</a></p></td></tr></table>";
    echo "<br>";

    $tocIndex++;

    echo "<a name=\"groupConsole\"><p><b>2.$tocIndex UT Online Summary</b></p>\n";
 
    $query = "SELECT UtStartTotal,UtEndTotal,UtOnlineTotal,UtOnlinePct FROM GroupInfo WHERE GrpID=" . $input["grpID"];
    $result = mysql_query($query,$db);
    $myrow = mysql_fetch_row($result);
    echo "<table>";
    for ($i = 0; $i < mysql_num_fields($result);$i++){
      if (mysql_field_name($result, $i) == "UtOnlinePct")
        if ($myrow[$i] == 100)
          $color="009900";
        else
          $color="FF0000";
      printf("<tr><td><b><p>%s</p></b></td><td><p><font color=$color>%s</font></p></td></tr>", mysql_field_name($result, $i), $myrow[$i]);
    }
    echo "</table>";
    echo "<br>";

    $tocIndex++;

    echo "<a name=\"groupConsole\"><p><b>2.$tocIndex UT Log Summary</b></p>\n";
    $query = "SELECT Message, SUM(Count) FROM Syslog WHERE GrpID=" . $input["grpID"] . " AND File LIKE \"%UT%.log\" GROUP BY Message";
	$result = mysql_query($query,$db);
	
    echo "<table cellpadding=0 cellspacing=0><tr>";
    for ($i = 0; $i < mysql_num_fields($result);$i++){
      printf("<td><p class=\"tableheader\">&nbsp;&nbsp;%s&nbsp;&nbsp;</p></td>", mysql_field_name($result, $i));
    }
    echo "</tr>";
    while($myrow = mysql_fetch_row($result)){
      printf("<tr><td><p class=\"table_left\">%s</p></td><td><p class=\"table\">%s</p></td></tr>", $myrow[0], $myrow[1]);
    }
    echo "</table>";
    $file = "UTLogSummary_".$input["grpID"].".csv";
    echo "<table><tr><td><p><a href=\"$resultsDirectory/$file\">Per UT log summary</a></p></td></tr></table>";
    echo "<p class\"table_left]\">*only counts instances where timestamp >= group start time</p>"; 
    echo "<br>";

    $tocIndex++;

    if(file_exists("/opt/share/data/results/" . $input["grpID"] . "/snmp/analysis")){
      echo "<a name=\"snmp\"></a><p><b>2.$tocIndex SNMP Plots</b></p>\n";
      $snmpQuery="SELECT PicName,TextAbove,TextBelow FROM TestReportPictureAnnotation WHERE SubDir=\"snmp/analysis\"";
      $result = mysql_query($snmpQuery,$db);
      while($picInfo= mysql_fetch_row($result)){
        $standardPics[] = "SnmpPlot_" . $input["grpID"] . "_" . $picInfo[0];
        if(file_exists("/opt/share/data/results/" . $input["grpID"] . "/snmp/analysis/SnmpPlot_" . $input["grpID"] . "_" . $picInfo[0])){
          echo "<table width=\"1024px\"><tr><td><p><center>" . $picInfo[1] . "</center></p><p><center>" . $picInfo[2] . "</center></p></td></tr><tr><td>";
          $img = "results/" . $input["grpID"] . "/snmp/analysis/SnmpPlot_" . $input["grpID"] . "_" . $picInfo[0];
          echo "<a href=\"$img\"><img src=\"$img\" BORDER=0></a></td></tr></table><br><br><br>"; //<p>" . $picInfo[2] . "<br><br><BR><br><Br>";
        }
      }
      //Misc SNMP Plots
      $dir = "/opt/share/data/results/" . $input["grpID"] . "/snmp/analysis/";
      // Open a known directory, and proceed to read its contents
      if (is_dir($dir)) {
        if ($dh = opendir($dir)) {
          while (($file = readdir($dh)) !== false) {
            if(substr($file,strrpos($file,".")+1)=="png" && array_search($file,$standardPics)===FALSE){
              $picTitle="<b>$file</b>";
              $picDesc="<font size = \"-1\"><i>A custom SNMP plot.</i></font>";
              $txtFilename = basename($file,".png") . ".txt";
              if(file_exists($dir . $txtFilename) && ($fileContents = file($dir . $txtFilename))){
                for($i=0;$i<count($fileContents);$i++){
                  if(strncmp(strtolower($fileContents[$i]),"title= ",7)==0){
                    $picTitle=substr($fileContents[$i],7);
                  }else if(strncmp(strtolower($fileContents[$i]),"title=",6)==0){
                    $picTitle=substr($fileContents[$i],6);
                  }else if(strncmp(strtolower($fileContents[$i]),"description= ",13)==0){
                    $picDesc=substr($fileContents[$i],13);
                  }else if(strncmp(strtolower($fileContents[$i]),"description=",12)==0){
                    $picDesc=substr($fileContents[$i],12);
                  }
                }
              }
              echo "<table width=\"1024px\"><tr><td><p><center>" . $picTitle . "</center></p>";
              echo "<p><center>" . $picDesc . "</center></p></td></tr><tr><td>";
              $img = "results/" . $input["grpID"] . "/snmp/analysis/" . $file;
              echo "<a href=\"$img\"><img src=\"$img\" BORDER=0></a></td></tr></table><br><br><br>";
            }
          }
          closedir($dh);
        }
      }
      $tocIndex++;
    }
    // end of snmp plots section
    
    if(file_exists("/opt/share/data/results/" . $input["grpID"] . "/top")){
      echo "<a name=\"top_plots\"></a><p><b>2.$tocIndex Top Plots</b></p>";

      $topQuery="SELECT PicName,TextAbove,TextBelow FROM TestReportPictureAnnotation WHERE SubDir=\"top\"";
      $result = mysql_query($topQuery,$db);
      while($picInfo= mysql_fetch_row($result)){
        $standardPics[] = "TopPlot_" . $input["grpID"] . "_" . $picInfo[0];
        if(file_exists("/opt/share/data/results/" . $input["grpID"] . "/top/TopPlot_" . $input["grpID"] . "_" . $picInfo[0])){
          echo "<table width=\"1024px\"><tr><td><p><center>" . $picInfo[1] . "</center></p><p><center>" . $picInfo[2] . "</center></p></td></tr><tr><td>";
          $img = "results/" . $input["grpID"] . "/top/TopPlot_" . $input["grpID"] . "_" . $picInfo[0];
          echo "<a href=\"$img\"><img src=\"$img\" BORDER=0></a></td></tr></table><br><br><br>";
        }
      }
      echo "<br>";
      $tocIndex++;
      
      //Misc Top Plots
      $dir = "/opt/share/data/results/" . $input["grpID"] . "/top/";
      // Open a known directory, and proceed to read its contents
      if (is_dir($dir)) {
        if ($dh = opendir($dir)) {
          while (($file = readdir($dh)) !== false) {
            if(substr($file,strrpos($file,".")+1)=="png" && array_search($file,$standardPics)===FALSE){
              $picTitle="<b>$file</b>";
              $picDesc="<font size = \"-1\"><i>A custom Top plot.</i></font>";
              $txtFilename = basename($file,".png") . ".txt";
              if(file_exists($dir . $txtFilename) && ($fileContents = file($dir . $txtFilename))){
                for($i=0;$i<count($fileContents);$i++){
                  if(strncmp(strtolower($fileContents[$i]),"title= ",7)==0){
                    $picTitle=substr($fileContents[$i],7);
                  }else if(strncmp(strtolower($fileContents[$i]),"title=",6)==0){
                    $picTitle=substr($fileContents[$i],6);
                  }else if(strncmp(strtolower($fileContents[$i]),"description= ",13)==0){
                    $picDesc=substr($fileContents[$i],13);
                  }else if(strncmp(strtolower($fileContents[$i]),"description=",12)==0){
                    $picDesc=substr($fileContents[$i],12);
                  }
                }
              }
              echo "<table width=\"1024px\"><tr><td><p><center>" . $picTitle . "</center></p>";
              echo "<p><center>" . $picDesc . "</center></p></td></tr><tr><td>";
              $img = "results/" . $input["grpID"] . "/top/" . $file;
              echo "<a href=\"$img\"><img src=\"$img\" BORDER=0></a></td></tr></table><br><br><br>";
            }
          }
          closedir($dh);
        }
      }
      $tocIndex++;
    }
    // end of top plots section
    
    if(file_exists("/opt/share/data/results/" . $input["grpID"] . "/ixos")){
      echo "<a name=\"ixos\"></a><p><b>2.$tocIndex IxOS Summary Plots</b></p>";

      $ixosQuery="SELECT PicName,TextAbove,TextBelow FROM TestReportPictureAnnotation WHERE SubDir=\"ixos_grp\"";
      $result = mysql_query($ixosQuery,$db);
      while($picInfo= mysql_fetch_row($result)){
        $standardPics[] = "IxOsTimeSeries_" . $input["grpID"] . "_" . $picInfo[0];
        if(file_exists("/opt/share/data/results/" . $input["grpID"] . "/ixos/IxOsTimeSeries_" . $input["grpID"] . "_" . $picInfo[0])){
          echo "<table width=\"1024px\"><tr><td><p><center>" . $picInfo[1] . "</center></p><p><center>" . $picInfo[2] . "</center></p></td></tr><tr><td>";
          $img = "results/" . $input["grpID"] . "/ixos/IxOsTimeSeries_" . $input["grpID"] . "_" . $picInfo[0];
          echo "<a href=\"$img\"><img src=\"$img\" BORDER=0></a></td></tr></table><br><br><br>";
        }
      }
      echo "<br>";
      $tocIndex++;
    }
    // end of ixos plots section

    if(file_exists("/opt/share/data/results/" . $input["grpID"] . "/spd_chk")){
      echo "<a name=\"spd_chk\"></a><p><b>2.$tocIndex Speed Check Plots</b></p>\n";
      $dir = "/opt/share/data/results/" . $input["grpID"] . "/spd_chk/";
      // Open a known directory, and proceed to read its contents
      if (is_dir($dir)) {
        if ($dh = opendir($dir)) {
          while (($file = readdir($dh)) !== false) {
            if(substr($file,strrpos($file,".")+1)=="png"){
              $picTitle="<b>$file</b>";
              $picDesc="<font size = \"-1\"><i>A custom SNMP plot.</i></font>";
              $txtFilename = basename($file,".png") . ".txt";
              if(file_exists($dir . $txtFilename) && ($fileContents = file($dir . $txtFilename))){
                for($i=0;$i<count($fileContents);$i++){
                  if(strncmp(strtolower($fileContents[$i]),"title= ",7)==0){
                    $picTitle=substr($fileContents[$i],7);
                  }else if(strncmp(strtolower($fileContents[$i]),"title=",6)==0){
                    $picTitle=substr($fileContents[$i],6);
                  }else if(strncmp(strtolower($fileContents[$i]),"description= ",13)==0){
                    $picDesc=substr($fileContents[$i],13);
                  }else if(strncmp(strtolower($fileContents[$i]),"description=",12)==0){
                    $picDesc=substr($fileContents[$i],12);
                  }
                }
              }
              echo "<table width=\"1024px\"><tr><td><p><center>" . $picTitle . "</center></p>";
              echo "<p><center>" . $picDesc . "</center></p></td></tr><tr><td>";
              $img = "results/" . $input["grpID"] . "/spd_chk/" . $file;
              echo "<a href=\"$img\"><img src=\"$img\" BORDER=0></a></td></tr></table><br><br><br>";
            }
          }
          closedir($dh);
        }
      }
    }
  }
  ?>
  </div>
  <?php
  //Start of Individual Tests...
  $tests = mysql_query("SELECT TestID,TestCase FROM TestInfo WHERE GrpID=" . $input["grpID"] . " ORDER BY TestID ASC",$db);
  $tocIndex=3;
  while($singleTestInfo=mysql_fetch_row($tests)){
  ?>
    <div class="post"><div class="toplink">
  <?php
  if(!isset($input["hide_" . $singleTestInfo[0]])){
    echo "<a href='" . $_SERVER['REQUEST_URI'] . "&hide_" . $singleTestInfo[0] . "=1#" . $singleTestInfo[0] . "'>Collapse Section</a>";
  } else {
    echo "<a href='" . str_replace("&hide_" . $singleTestInfo[0] . "=1","",$_SERVER['REQUEST_URI']) . "#" . $singleTestInfo[0] . "'>Expand Section</a>";
  }
  ?>
  | <a href="#top">Back to Top</a></div>
    <a name="<?php echo $singleTestInfo[0]; ?>"></a><h1><?php echo $tocIndex; ?>. TestID <?php echo $singleTestInfo[0]; ?> - <?php echo $singleTestInfo[1]; ?></h1>
    <?php
    if(!isset($input["hide_" . $singleTestInfo[0]])){
    ?>
    <p><b><a name="<?php echo $singleTestInfo[0]; ?>_info"></a><?php echo $tocIndex; ?>.1 Test Information</b></p>
    <br>
    <p><b><?php echo $tocIndex; ?>.1.1 Test Summary</b></p>
    <table>
    <?php
    $summary=mysql_query("SELECT SpecPassFail,Notes FROM TestInfo WHERE TestInfo.GrpID=" . $input["grpID"] . " AND TestInfo.TestID=" . $singleTestInfo[0],$db);
    $singleSummary = mysql_fetch_row($summary);
    
    echo "<tr><td><p><a href=\"edit.php?grpID=" . $input["grpID"] . "&ID=" . $singleTestInfo[0] . "\">Pass/Fail</a></p></td><td valign=\"top\">";
    if($singleSummary[0]=="pass"){
      echo "<p class=\"green\">PASS</p></td></tr>";
    } elseif($singleSummary[0]=="FAIL"){
      echo "<p class=\"red\">FAIL</p></td></tr>";
    } else {
      echo "<p>" . $singleSummary[0] . "</p></td></tr>";
    }
    echo "<tr><td><p><a href=\"edit.php?grpID=" . $input["grpID"]. "&ID=" . $singleTestInfo[0] . "\">Test Notes</a></p></td><td valign=\"top\"><p>" . $singleSummary[1] . "</p></td></tr>\n</table>";
    ?>
    <br>
    <div class="contain">
    <div class="leftcol">
    <p><b><?php echo $tocIndex; ?>.1.2 Test Configuration</b></p>
    <?php
    $query = "SELECT Datetime,DurationHrs,ScriptName,SAMParamFile FROM TestInfo WHERE GrpID=" . $input["grpID"] . " AND TestID=" . $singleTestInfo[0];
    $result = mysql_query($query,$db);
    $myrow = mysql_fetch_row($result);
    echo "<table>";
    for ($i = 0; $i < mysql_num_fields($result);$i++){
      if(mysql_field_name($result, $i)=="Status" || mysql_field_name($result, $i)=="DurationHrs"){
        printf("<tr><td><p><a href=\"edit.php?grpID=" . $input["grpID"]. "&ID=" . $singleTestInfo[0] . "\">%s</a></p></td><td><p>%s</p></td></tr>", mysql_field_name($result, $i), $myrow[$i]);
      } else {
        printf("<tr><td><p>%s</p></td><td><p>%s</p></td></tr>", mysql_field_name($result, $i), $myrow[$i]);
      }
    }
    echo "</table><br>";
    ?>
    </div><div class="rightcol">
    <p><b><?php echo $tocIndex; ?>.1.3 Test Results</b></p>
    <?php
    $query = "SELECT UtStartTotal,UtEndTotal,UtOnlineTotal,UtOnlinePct FROM TestInfo WHERE GrpID=" . $input["grpID"] . " AND TestID=" . $singleTestInfo[0];
    $result = mysql_query($query,$db);
    $myrow = mysql_fetch_row($result);
    echo "<table>";
    for ($i = 0; $i < mysql_num_fields($result);$i++){
      printf("<tr><td><b><p>%s</p></b></td><td><p>%s</p></td></tr>", mysql_field_name($result, $i), $myrow[$i]);
    }
    echo "</table>";
    ?>
    </div></div>
<?php
    echo "<br>";
    $tocInnerIndex=3;
    $existsIxOsResult = mysql_query("SELECT * FROM IxOs WHERE TestID=" . $singleTestInfo[0] . " AND GrpID=" . $input["grpID"],$db);
    if(mysql_fetch_row($existsIxOsResult)){
      ixos($singleTestInfo[0],$tocIndex,$tocInnerIndex, $input["grpID"]);
      $tocInnerIndex++;
    }
    }//if hide_testId
    ?>
    </div>

  <?php
  $tocIndex++;
  }
}
?>
  </div>

  <div class="post"><div class="toplink">
  <?php
  if(!isset($input["hide_dataVisualizations"])){
    echo "<a href='" . $_SERVER['REQUEST_URI'] . "&hide_dataVisualizations=1#dataVisualizations'>Collapse Section</a>";
  } else {
    echo "<a href='" . str_replace("&hide_dataVisualizations=1","",$_SERVER['REQUEST_URI']) . "#dataVisualizations'>Expand Section</a>";
  }
  ?>
  | <a href="#top">Back to Top</a></div>
<?php
  echo "<a name=\"dataVisualizations\"></a><h1>$tocIndex. Data Visualizations</h1>";

  if(!isset($input["hide_dataVisualizations"])){

    //Create vipcat graph div, retrieve contents of vipcat.js, begin templating operation
    echo "<div id=\"vipcat\" class=\"vipcat\" style=\"margin: 20px\"></div>"; 
    $vipcatJS = explode(';', file_get_contents("results/{$input["grpID"]}/vipcat/vipcat.js"));

    //pop off trailing empty array element since we split by semicolons  
    array_pop($vipcatJS); 
    //Default path for Reda test results
    $csvPath = "'results/{$input["grpID"]}/vipcat/data/";
  
    //Regex to replace filename with full directory path + filename.
    for($i = 0, $size = count($vipcatJS); $i < $size; $i++){
      $vipcatJS[$i] = preg_replace("/\'(.+\.csv)/", "$csvPath$1", $vipcatJS[$i]);
    }

    //echo all graphs out to Reda page
    echo "<script type=\"text/javascript\">window.onload = function () {"; 
    foreach($vipcatJS as $graph){   
      if(!empty($graph)){
        echo $graph . ";";
      }
    }
    echo "};</script>";
  }
?>
  </div>

<!--<iframe src="IxLoad Summary Report.html"></iframe>-->
</html>
