<?php
/*
 * ---------------------------------------------------------------
 *
 * File:  index.php
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
 & Filename: index.php
 * Purpose: The index page (which is the first page most people see when they
 *          access Reda) is comprised of several "widget." In fact, the index
 *          page is meant to serve as a portal so that the user can more easily
 *          access the data they are looking for.
 *
 *****************************************************************************/
include 'func.php';
mysqlSetup($db);

?>

<!--
All webpages must start with <html> and usually have <head> tags.
-->
<html>
<head>
  <title>ReDa: <?php echo $projectName; ?>'s Test Results Database</title> <!-- The <title> tag denotes what is displayed on bar
                                                         at the top of the browser -->
  <link rel="stylesheet" type="text/css" href="reda.css">
<script>

//Get the whole input box from getreleases.php. This is called everytime
//the user clicks the selection info.
function changeRelease(fieldName,ID){
  var spanID = "release" + ID;
  var xmlHttp;
  try {
    // Firefox, Opera 8.0+, Safari
    xmlHttp=new XMLHttpRequest();
  } catch (e) {
    // Internet Explorer
    try {
      xmlHttp=new ActiveXObject("Msxml2.XMLHTTP");
    } catch (e) {
      try {
        xmlHttp=new ActiveXObject("Microsoft.XMLHTTP");
      } catch (e) {
        alert("Your browser does not support AJAX!");
        return false;
      }
    }
  }
  xmlHttp.onreadystatechange=function()
    {
      if(xmlHttp.readyState==4) {
        //parse xmlHttp.responseText
        document.getElementById(spanID).innerHTML=xmlHttp.responseText;
      }
    }
  var url="getreleases.php";
  url=url+"?fieldName="+fieldName;
  url=url+"&id="+ID;
  xmlHttp.open("GET",url,true);
  xmlHttp.send(null);
}

//Called everytime the user clicks on the "+" button. This function adds another
//set of field-release boxes.
function addSelection(numToAdd,maxFields){
  var spanID= "selection" + numToAdd;
  var html ="<p>&nbsp;&nbsp;&nbsp;<select name='FieldName" + numToAdd + "' onChange=\"changeRelease(this.value, '" + numToAdd + "')\">";
<?php
$query="SELECT DISTINCT FieldName FROM Releases";
$result = mysql_query($query,$db);
$numFieldNames = mysql_num_rows($result);
$firstField=1;
while($fieldname = mysql_fetch_row($result)){
  echo "html=html+\"<option value='" . $fieldname[0] . "'>" . $fieldname[0] . "</option>\";\n";
  if($firstField==1)
    $firstFieldName = $fieldname[0];
  $firstField=0;
}
?>
  html=html+"</select> ";
  html=html+"<span id='release" + numToAdd + "'>";
  html=html+"<select name='OfficialRelease" + numToAdd + "'><option value='any'>Any</option>";
<?php
$query="SELECT DISTINCT OfficialRelease FROM Releases WHERE FieldName='" . $firstFieldName  . "'";
$result = mysql_query($query,$db);
while($release = mysql_fetch_row($result)){
  echo "  html=html+\"<option value='" . $release[0] . "'>" . $release[0] . "</option>\";\n";
}
?>
  html=html+"</select> ";
  html=html+"</span>";
  if(next<maxFields){
    numToAdd = numToAdd*1;
    var next = numToAdd+1;
    html=html+"<input type='button' value='+' onClick=\"addSelection('" + next + "','" + maxFields + "')\">";
  }
  html=html+"</p>";

  document.getElementById(spanID).innerHTML=html;
}

</script>
</head>
<?php 
bodyStyle();
banner();
navbar1("index");
?> <!-- be sure to close php code with ?> -->
<br> <!-- <br> tag (short for break) is used to start a new line. NOTE: HTML WILL IGNORE WHITESPACES, INCLUDING NEWLINES, UNLESS YOU SPECIFIY A NEW LINE WITH <br>. -->
<div id="leftcol">
<div class="post">
  <h1><b>Top 10 Searches</b></h1>
  <p>
    <?php
    $i=1;
    // We construct a query to get the list of globally saved queries from the database, sorted by times used:
    $query = "SELECT $savedQueryFieldName,$savedQueryDescriptionFieldName FROM $savedQueryTableName ORDER BY $savedQueryCountFieldName DESC"; 
    // Now to send it to the database: (NOTE: $result's variable type after this line is a "result set".
    $result = mysql_query($query,$db);
    while (($myrow = mysql_fetch_row($result)) && $i<=10){ //Going through the result set returned to us.
                                                           //Show the first 5.
      //All php code is read and execute before displaying the webpage. Therefore, if you want php to
      //leave some sort of info on the webpage, you much use echo or printf to print the appropriate
      //HTML code. NOTE: &nbsp; is used to denote a space " ".
      //Since we know that we're fetching query and description, in that order, we know that the first
      //element of $myrow is query and the second is description.
      printf("&nbsp;&nbsp;<a href=\"results.php?query=%s&searchtype=topten\">%s. %s</a><br>", str_replace('%','%25',$myrow[0]), $i, $myrow[1]);
      $i++;
    }
    ?>
	</p>
    </div>
<br>
<div class="post">
  <h1><b>Saved Searches</b></h1>
      <form action="../">
	  <p>
        <select name="saveddb" size="1" onChange="window.open(this.options[this.selectedIndex].value,'_top')">
        <option value="">---Select a Saved Search---</option>
        <?php
        //Get a list of saved searches.
        $query = "SELECT $savedQueryFieldName,$savedQueryDescriptionFieldName FROM $savedQueryTableName ORDER BY $savedQueryDescriptionFieldName ASC";
        $result = mysql_query($query,$db);
        while ($myrow = mysql_fetch_row($result)){
          printf("<option value=\"results.php?searchtype=saved&query=%s\">%s</option>", str_replace('%','%25',$myrow[0]), $myrow[1]);
        }
        ?>
        </select>
		</p>
      </form>
</div>
</div>
<div id="rightcol">
<div class="post">
  <h1><b>Recent Tests</b></h1>
  <form method="get" name="recentTests" action="results.php">
  <p>Find tests run within the past&nbsp;
  <select name="pastTime" size="1">
  <option value="day">Day</option>
  <option value="week" SELECTED>Week</option>
  <option value="2weeks">2 Weeks</option>
  <option value="3weeks">3 Weeks</option>
  <option value="month">Month</option>
  <option value="forever">Forever</option>
  </select>
  &nbsp;from&nbsp;
  <select name="testStation" size="1">
  <option value="all">All Test Stations</option>
  <?php
  //Get a list of test stations
  $query = "SELECT DISTINCT $testStationFieldName FROM $grpLevelTableName WHERE $testStationFieldName NOT LIKE '%,%' ORDER BY $testStationFieldName";
  echo $query;
  $result = mysql_query($query,$db);
  while ($myrow = mysql_fetch_row($result)){
    echo "<option value=\"" . $myrow[0] . "\">" . $myrow[0] . "</option>";
  }
  ?>
  </select>
  <input type="hidden" name="searchtype" value="recent">
  <br><input type="checkbox" name="overnight" value=1> Only Overnight
  <br><input type="Submit" name="submit" value="Search">
  </form></p>
</div>
<br>
<div class="post">
  <h1><b>ID Search</b></h1>
      <form method="get" name="search" action="results.php"> <!-- Refer to http://www.htmlgoodies.com/tutorials/forms/
                                                              For tutorials on how to create forms. -->
      <p>
      Comma and space separated lists accepted.<br>
	  <input type="hidden" name="searchtype" value="id">
      <select name="idtype" size="1">
      <option SELECTED value="GrpID">Group ID</option>
      </select>
      <select name="searchop" size="1">
        <option SELECTED value="=">is Equal to</option>
        <option value="!=">is Not Equal to</option>
        <option value=">">is Greater than</option>
        <option value=">=">is Greater than/Equal to</option>
        <option value="<">is Less than</option>
        <option value="<=">is Less than/Equal to</option>
        <option value="LIKE">is Like</option>
      </select>
      <input type="Text" name="searchmatch" size="10">
      <input type="Submit" name="submit" value="Search">
      </form>
      </p>
    </div>
<br>
<div class="post">
  <h1><b>Current Station Status / Last Test</b></h1>
  <p><table BORDER="1" RULES="ROWS" FRAME="HSIDES" CELLSPACING="0" ><col 3 WIDTH="100">
  <?php
  //Get a list of test stations
  $date = date("Y-m-d G:i:s",mktime(0, 0, 0, date("m")-1, date("d")-15, date("Y")));
  $query = "SELECT DISTINCT $testStationFieldName FROM $grpLevelTableName WHERE $testStationFieldName NOT LIKE '%,%' AND $grpLevelTableName.$grpDateFieldName>='$date' ORDER BY $testStationFieldName";
  
  //echo $query;
  $result = mysql_query($query,$db);

  while ($myrow = mysql_fetch_row($result)){
    $query = "SELECT $grpLevelTableName.Status, $grpLevelTableName.User, $grpLevelTableName.GrpId FROM $grpLevelTableName WHERE $grpLevelTableName.$testStationFieldName = '".$myrow[0]."' AND $grpLevelTableName.Status = 'running' ORDER BY $grpIDField DESC LIMIT 1";
    //echo $query;
    $result2 = mysql_query($query,$db);
    if (mysql_num_rows($result2) == 0) {
        $query = "SELECT $grpLevelTableName.Status, $grpLevelTableName.User, $grpLevelTableName.GrpId FROM $grpLevelTableName WHERE $grpLevelTableName.$testStationFieldName = '".$myrow[0]."' AND $grpLevelTableName.Status != 'invalid' ORDER BY $grpIDField DESC LIMIT 1";
        $result2 = mysql_query($query,$db);
    }
    $currentStatus = mysql_fetch_row($result2);
    if ( strcmp($currentStatus[0], "running") == 0 ) {
        echo "<tr><td>".$myrow[0] . "</td><td><font color='red'> in use by&nbsp;".$currentStatus[1]."</font></td><td>&nbsp;&nbsp;<a href=\"report.php?grpID=$currentStatus[2]\">$projectName $currentStatus[2]</a></td></tr>";
    } else {
        echo "<tr><td>".$myrow[0] . "</td><td><font color='green'>  free </font></td><td>&nbsp;&nbsp;<a href=\"report.php?grpID=$currentStatus[2]\">$projectName $currentStatus[2]</a></td></tr>";
    }
  }
  ?>
  </table></p>
<?php
//This section is not yet working in Leapfrog.
/*
<h1><b>Testing Status (beta)</b></h1>
<form method="get" action="status.php">
<p>
Show <select name='show' size='1'><option value='recent'>the most recent</option><option value='all'>all</option></select> tests for...</p>
<p>&nbsp;&nbsp;&nbsp;<select name='FieldName0' onChange="changeRelease(this.value, '0')">
<?php
//Find a list of software types (IE SMTS software vs. SM software)
$query="SELECT DISTINCT FieldName FROM Releases";
$result = mysql_query($query,$db);
$numFieldNames = mysql_num_rows($result);
$firstField=1;
while($fieldname = mysql_fetch_row($result)){
  echo "<option value='" . $fieldname[0] . "'>" . $fieldname[0] . "</option>";
  if($firstField==1)
    $firstFieldName = $fieldname[0];
  $firstField=0;
}
?>
</select>
<? echo "<input type='hidden' name='maxSelections' value='" . $numFieldNames . "'>";
?>
<span id='release0'>
<select name='OfficialRelease0'><option value='any'>Any</option>
<?php
//Get all the releases
$query="SELECT DISTINCT OfficialRelease FROM Releases WHERE FieldName='" . $firstFieldName  . "'";
$result = mysql_query($query,$db);
while($release = mysql_fetch_row($result)){
  echo "<option value='" . $release[0] . "'>" . $release[0] . "</option>";
}
?>
</select>
</span>
<?
if($numFieldNames>1){
  echo "<input type='button' value='+' onClick=\"addSelection('1', '" . $numFieldNames . "')\">";
}
?>
</p>
<?php
for($i=1;$i<$numFieldNames;$i++){
  echo "<span id='selection$i'></span>";
}
?>
<p>&nbsp;</p>
<p><input type="Submit" name="submit" value="Show Me the Money!" style="width: 150px;">
</form>
</div>
*/
/*
?>
<div class="post">
  <h1><b>SM Hardware Regression</b></h1>
  <form method="get" action="smhwregression.php">
    <p><table cellspacing=><tr>
      <td width="27%">Test Name<br>
          <select name="testName[]" multiple size="4">
          <option value="SmRegTime">SmRegTime</option>
          <option value="SmSwUpgrade">SmSwUpgrade</option>
          <option value="MrDsBer">MrDsBer</option>
          <option value="BidirectionalPER">BidirectionalPER</option>
          </select></p>
      </td>
      <td width="27%">Characteristic<br>
          <select name="characteristic[]" multiple size="4">
          <option value="modem">Modem</option>
          <option value="hwvers" DISABLED>Hardware Version</option>
          <option value="hwtype" DISABLED>Hardware Type</option>
          <option value="date" DISABLED>Production Date</option>
      </td>
      <td valign="top">
        <br>TestID (optional):<input type="Text" name="grpID" size="4"><br>
        <br><input type="Submit" name="submit" value="Show Results" style="width: 150px;">
      </td>
    </tr></table></p>
    <p class="small">Use Ctrl+Click to select multiple fields.</p>
  </form>
</div>
*/
?>
</div>
</body>
</html>
