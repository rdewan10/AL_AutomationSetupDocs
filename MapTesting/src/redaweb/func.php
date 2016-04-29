<?php
/*
 * ---------------------------------------------------------------
 *
 * File:  func.php
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
 & Filename: func.php
 * Purpose: This page is what the administrator should edit to adapt Reda to
 *          a particular project. This page also contains various functions
 *          used by other pages. It's for of a config page and a library rolled
 *          into one.
 *
 *****************************************************************************/


/******************************************************************************
/                               VALUES TO EDIT
******************************************************************************/
//What is your project called?
$projectName="AL";

//Info about the database
$dbHost = "localhost";
$dbUsername = "arclight";
$dbPassword = "viasat";
$dbName = "performance";

//Reda gives users the ability to save their searches
//so that they cna run the same search again at a later
//time with only one click.
$savedQueryTableName = "queries";
$savedQueryFieldName = "query";
$savedQueryCountFieldName = "times_used";
$savedQueryDescriptionFieldName = "description";

//If you have multiple test level tables, it is the one
//where you store test configuration information,
//such as the test date.
$testLevelTableName = "TestInfo";
$testIDField = "TestID";
$testDateFieldName = "Datetime";

//If you have multiple group level tables, it is the one
//where you store group configuration information,
//such as the group ID.
$grpLevelTableName = "GroupInfo";
$grpIDField = "GrpID";
$grpDateFieldName = "Datetime";
//Since we have multiple test stations, we have a field for it. TestStation must be under the grpLevelTableName's table.
$testStationFieldName = "StationName";
//These are the default fields that will be displayed when a user makes
//a standard search. Format of the items in this array should be 
// <TABLE NAME>.<FIELD NAME>
$defaultFields = array("GroupInfo.GrpID as Report",
                       "GroupInfo.Results",
                       "GroupInfo.GrpID",
                       "GroupInfo.Status",
                       "GroupInfo.Datetime",
		       "GroupInfo.DurationHrs",
                       "GroupInfo.StationName",
                       "GroupInfo.StationType",
		       "GroupInfo.User",
                       "GroupInfo.GroupName",
                       "GroupInfo.SpecPassFail",
                      );

//Simplified version of the above.
$simplifiedFields = array("GroupInfo.Results",
                          "GroupInfo.GrpID as Report",
                          "GroupInfo.GrpID",
                          "GroupInfo.Status",
                          "GroupInfo.Datetime",
                          "GroupInfo.DurationHrs",
                          "GroupInfo.StationName",
                          "GroupInfo.User",
                          "GroupInfo.GroupName",
                          "GroupInfo.TestCase",
                          "GroupInfo.SpecPassFail",
                          "GroupInfo.Description",
                          "GroupInfo.Notes"
                        );

$defaultOptionalTables = array();

//This list of table _MUST_ also include the neccessary tables so that
//the tables in defaultOptionalTables can form a link of dependencies
//to the other tables.
$defaultTables = array('GroupInfo'
                    );

$simplifiedTables = array('GroupInfo'
                    );

//Fields that can be edited using Reda's edit page (edit.php).
//We encourage the administrator of Reda to allow as few editable
//fields as possible. We have discovered that the more fields someone
//can edit, the more likely they are to make a mistake.
//Entries should be formatted:
//
//  "<TABLE NAME>.<FIELDNAME>" => <TYPE>
//
//There are three types of fields:
// -DROPDOWN: The webpage queries for a list of distinct values and the user can only select one of those values.
// -TEXTAREA: A large text field
// -TEXT: A standard, one line, text field
// -MULTINUM: A list of numbers, stored in it's own table. Format for this is different:
//     "<TABLENAME>" => MULTINUM

$editableGroupFields = array("GroupInfo.GroupName" => "DROPDOWN",
            "GroupInfo.TestCase" => "DROPDOWN",
            "GroupInfo.Status" => "DROPDOWN",
			"GroupInfo.Description" => "TEXTAREA",
			"GroupInfo.Datetime" => "TEXT",
			"GroupInfo.DurationHrs" => "TEXT",
			"GroupInfo.SpecPassFail" => "DROPDOWN",
            //"GroupInfo.ReleaseCycle" => "DROPDOWN",
			"GroupInfo.User" => "TEXT",
			"GroupInfo.Notes" => "TEXTAREA",
            "RelatedSXRs" => "MULTINUM"
        );

$editableGroupTables = array("GroupInfo"
                            );

$editableTestFields = array("TestInfo.TestCase" => "DROPDOWN",
                            "TestInfo.Datetime" => "TEXT",
                            "TestInfo.DurationHrs" => "TEXT",
                            "TestInfo.SpecPassFail" => "DROPDOWN",
                            "TestInfo.Notes" => "TEXTAREA",
                           );

$editableTestTables = array("TestInfo"
                           );

//Fields such as notes or descriptions (ie, fields that a user would put
//their thoughts and comments in
$commentFieldNames = array("RelatedSXRs.SXR",
                           "TestInfo.Notes",
                           "GroupInfo.Description",
                           "GroupInfo.Notes",
                          );

/******************************************************************************
 *
 *                      DATABASE STRUCTURE AND INFORMATION
 *
 *****************************************************************************/
//These following tables tell the application how your database is structured.


//We list linked tables using this field. Each entry will be of the format:
//
//      <DEPENDENT TABLE> => <PARENT TABLE>
//A parent table is defined as a table who's primary key is a foreign key in 
//the dependent table. 
$tableParents = array("RelatedSXRs" => "GroupInfo",
                      "TestInfo" => "GroupInfo",
                      "VersionInfo" => "GroupInfo"
                    );

//A ranking of the tables. A rank of 1 means that the table is not dependent on
//any other tables. A rank of 2 means that the table is dependent on a table of
//rank 1, etc.
$tableHierarchy = array("GroupInfo" => 1,
                        "TestInfo" => 2,
                        "VersionInfo" => 2,
                        "RelatedSXRs" => 2
                    );

//We are listing the foreign key in each table. If there is more than one
//foreign key,list it in a comma-separated manner.
$tableKeyField = array("TestInfo" => "GrpID",
                       "VersionInfo" => "GrpID",
                       "RelatedSXRs" => "GrpID"
                    );

//This is for tables where there may or may not be an entry corresponding to it's parent table.
$optionalTables = array("RelatedSXRs","VersionInfo");

//The following two tables are pretty self explanatory: they list fields and tables that the user
//can search from.
//Fields in $allFieldsSearchable should be of the format 
//
//       <FIELD> (<TABLE>)
$allFieldsSearchable = array("Results (GroupInfo)", "GrpID (GroupInfo)",
                        "TestID (TestInfo)", "Status (GroupInfo)",
                        "Datetime (GroupInfo)", "Datetime (TestInfo)",
                        "DurationHrs (GroupInfo)", "DurationHrs (TestInfo)",
                        "StationName (GroupInfo)", "StationType (GroupInfo)",
                        "User (GroupInfo)", "GroupName (GroupInfo)",
                        "TestCase (TestInfo)", "TestCase (GroupInfo)",
                        "ScriptName (TestInfo)", "SAMParamFile (TestConfig)",
                        "SpecPassFail (TestInfo)", "SpecPassFail (GroupInfo)",

                        "UtStartTotal (TestInfo)", "UtStartTotal (GroupInfo)",
                        "UtEndTotal (TestInfo)", "UtEndTotal (GroupInfo)",
                        "UtOnlineTotal (TestInfo)", "UtOnlineTotal (GroupInfo)",
                        "UtOnlinePct (TestInfo)", "UtOnlinePct (GroupInfo)",

                        "Name (VersionInfo)", "Type (VersionInfo)", "Version (VersionInfo)",
                        
                        "SXR (RelatedSXRs)",
                        "Description (GroupInfo)", "Notes (TestInfo)", 
                        "Notes (GroupInfo)"
                    );
                             
$allTablesSearchable = array("GroupInfo", "TestInfo", "RelatedSXRs", "VersionInfo");

/******************************************************************************
/                        DO NOT EDIT BELOW HERE!
******************************************************************************/

function mysqlSetup(&$db) {
  global $dbHost, $dbUsername, $dbPassword, $dbName;
  if($dbPassword==""){
    $db = mysql_connect($dbHost, $dbUsername);
  } else {
    $db = mysql_connect($dbHost, $dbUsername, $dbPassword);
  }
  mysql_select_db($dbName,$db); //Specify our database (reda2)
}

function getCustomViewsAsArray() {
  global $customViews;

}

function getAllFields() {
  global $allFieldsSearchable;
  foreach ($allFieldsSearchable as $field){
    $fieldsCommaSeparated = $fieldsCommaSeparated . $field . ",";
  }
  $fieldsCommaSeparated = substr($fieldsCommaSeparated,0,strlen($fieldsCommaSeparated)-1);
  return $fieldsCommaSeparated;
}

function getAllFieldsSqlFormatted() {
  global $allFieldsSearchable;
  foreach($allFieldsSearchable as $field){
    $tableNameStart = strpos($field,"(")+1;
    $tableNameLength = strlen($field) - 1 - $tableNameStart;
    $tableName = substr($field,$tableNameStart,$tableNameLength);
    $fieldName = substr($field,0,$tableNameStart-2);
    $mysqlFormattedField = $tableName . "." . $fieldName;
    $allFieldsFormatted .= $mysqlFormattedField . ",";
  }
  $allFieldsFormatted = substr($allFieldsFormatted,0,strlen($allFieldsFormatted)-1);
  return $allFieldsFormatted;
}

function getAllFieldsSqlFormattedAsArray() {
  global $allFieldsSearchable;
  $i=0;
  foreach($allFieldsSearchable as $field){
    $tableNameStart = strpos($field,"(")+1;
    $tableNameLength = strlen($field) - 1 - $tableNameStart;
    $tableName = substr($field,$tableNameStart,$tableNameLength);
    $fieldName = substr($field,0,$tableNameStart-2);
    $mysqlFormattedField = $tableName . "." . $fieldName;
    $allFieldsFormatted[$i]=$mysqlFormattedField;
    $i++;
  }
  return $allFieldsFormatted;
}

function getAllFieldsSortedAsArray() {
  global $allFieldsSearchable;
  $allFieldsSorted =$allFieldsSearchable;
  asort($allFieldsSorted);
  $i=0;
  foreach ($allFieldsSorted as $field){
    $fieldsArray[$i] = $field;
    $i++;

  }
  return $fieldsArray;
}

function getAllTables(){
  global $allTablesSearchable;
  foreach ($allTablesSearchable as $table){
    $tablesCommaSeparated = $tablesCommaSeparated . $table . ",";
  }
  $tablesCommaSeparated = substr($tablesCommaSeparated,0,strlen($tablesCommaSeparated)-1);
  return $tablesCommaSeparated;
}

function getAllTablesAsArray(){
  global $allTablesSearchable;
  return $allTablesSearchable;
}

function getDefaultFields() {
  global $defaultFields;
  $fieldsCommaSeparated = "";
  foreach ($defaultFields as $field){
    $fieldsCommaSeparated = $fieldsCommaSeparated . $field . ",";
  }
  $fieldsCommaSeparated = substr($fieldsCommaSeparated,0,strlen($fieldsCommaSeparated)-1);
  return $fieldsCommaSeparated;
}

function getDefaultFieldsAsArray() {
  global $defaultFields;
  return $defaultFields;
}

function getDefaultTables(){
    global $defaultTables;
    global $defaultOptionalTables;
    global $tableKeyField;
    global $tableParents;

    $tablesCommaSeparated="";
    foreach ($defaultTables as $table){
      if(!in_array($table,$defaultOptionalTables)){
        $tablesCommaSeparated = $tablesCommaSeparated . $table . ",";
      }
    }
    $tablesCommaSeparated = substr($tablesCommaSeparated,0,strlen($tablesCommaSeparated)-1);

    foreach($defaultOptionalTables as $table){
      $tablesCommaSeparated = " LEFT JOIN " . $table . " ON " . $table . "." . 
                              $tableKeyField[$table] . "=" . 
                              $tableParents  . "." . $tableKeyField[$table];
    }
    return $tablesCommaSeparated;
}

function getDefaultTablesAsArray(){
    global $defaultTables;
    $i=0;
    foreach ($defaultTables as $table){
      $tablesArray[$i] = $table;
      $i++;
    }
    return $tablesArray;
}

function getSimplifiedFields() {
  global $simplifiedFields;
  $fieldsCommaSeparated = "";
  foreach ($simplifiedFields as $field){
    $fieldsCommaSeparated = $fieldsCommaSeparated . $field . ",";
  }
  $fieldsCommaSeparated = substr($fieldsCommaSeparated,0,strlen($fieldsCommaSeparated)-1);
  return $fieldsCommaSeparated;
}

function getSimplifiedFieldsAsArray() {
  global $simplifiedFields;
  return $simplifiedFields;
}


function getSimplifiedTables(){
    global $simplifiedTables;
    global $tableKeyField;
    global $tableParents;

    $tablesCommaSeparated="";
    foreach ($simplifiedTables as $table){
      $tablesCommaSeparated = $tablesCommaSeparated . $table . ",";
    }
    $tablesCommaSeparated = substr($tablesCommaSeparated,0,strlen($tablesCommaSeparated)-1);

    return $tablesCommaSeparated;
}

function getSimplifiedTablesAsArray(){
    global $simplifiedTables;
    $i=0;
    foreach ($simplifiedTables as $table){
      $tablesArray[$i] = $table;
      $i++;
    }
    return $tablesArray;
}

function getFieldList($Table) {
  mysqlSetup($db);
  $res = mysql_query("SHOW COLUMNS FROM $Table");
  while ($row = mysql_fetch_array($res)) $col_names[]=$row[0];
  return ($col_names);
}

function sortFieldsAsArray($fieldsList){
  $allFieldsSearchable = getAllFieldsSqlFormattedAsArray();
  $i=0;
  foreach ($fieldsList as $field){
    if($field == "GroupInfo.GrpID as Report"){
      $sortedFields[$i] = $field;
      $i++;
      break;
    }
  }

  foreach($allFieldsSearchable as $searchableField){
    foreach ($fieldsList as $field){
      if($field == $searchableField){
        $sortedFields[$i] = $field;
        $i++;
        break;
      }
    }
  }
  return $sortedFields;
}

function sortFields($fieldsList){
  $allFieldsSearchable = getAllFieldsSqlFormattedAsArray();
  $sortedFields="";
  
  foreach ($fieldsList as $field){
    if($field == "GroupInfo.GrpID as Report"){
      $sortedFields .= $field . ",";
      break;
    }
  }

  foreach($allFieldsSearchable as $searchableField){
    foreach ($fieldsList as $field){
      if($field == $searchableField){
        $sortedFields .= $field . ",";
        break;
      }
    }
  }
  $sortedFields = substr($sortedFields,0,strlen($sortedFields)-1);
  return $sortedFields;
}

//Given a list of tables, link the tables together so we can form a query.
function tableLink($tablesList){
  global $tableParents;
  global $tableHierarchy;
  global $tableKeyField;
  global $optionalTables;

  $lowestHierarchyLevel = 0;
  $numTables = 0;
  $outerIndex = 0;
  $tableJoinCondition="";

  foreach($optionalTables as $table){
    if(($index = array_search($table,$tablesList))!==FALSE){
      unset($tablesList[$index]);
    }
  }
  $tablesListTemp = $tablesList;

  if(count($tablesList)==1){
    return "1=1";
  }
  foreach($tablesListTemp as $tableOuter){
    array_shift($tablesListTemp);
    foreach($tablesListTemp as $tableInner){
      if($tableOuter == $tableInner){
        array_splice($tablesList,$outerIndex,1);
        return tableLink($tablesList);
      }
    }
    $outerIndex++;
  }

  foreach($tablesList as $table){
    if($tableHierarchy[$table] > $lowestHierarchyLevel){
      $lowestHierarchyLevel = $tableHierarchy[$table];
      $lowestHierarchyTable = $table;
      $lowestHierarchyIndex = $numTables;
    }
    $numTables++;
  }
  //connect two tables using the related keys.
  $start=0;
  $end=strpos($tableKeyField[$lowestHierarchyTable],",");
  if($end===FALSE){
    $key = substr($tableKeyField[$lowestHierarchyTable],$start);
  } else {
    $key = substr($tableKeyField[$lowestHierarchyTable],$start,$end);
  }
  while($key !== FALSE){
    $tableJoinCondition = $lowestHierarchyTable . "." . $key . "=" . $tableParents[$lowestHierarchyTable] . "." . $key;
    if($end===FALSE)
      break;
    $start = $end+1;
    $end = strpos($tableKeyField[$lowestHierarchyTable],",",$end+1);
    if($end===FALSE){
      $key = substr($tableKeyField[$lowestHierarchyTable],$start);
    }else {
      $key = substr($tableKeyField[$lowestHierarchyTable],$start,$end-$start);
    }
  }

  array_splice($tablesList,$lowestHierarchyIndex,1,$tableParents[$lowestHierarchyTable]);
  $recursiveJoinConditions = tableLink($tablesList);
  if($recursiveJoinConditions != NULL){
    $tableJoinCondition = $tableJoinCondition . " AND " . $recursiveJoinConditions;
  }
  if($tableJoinCondition==""){
    $tableJoinCondition="1=1";
  }
  return $tableJoinCondition;
}

function leftJoinParents($tablesList, $leftJoinTable){
  global $tableParents;
  global $tableHierarchy;
  global $tableKeyField;
  global $optionalTables;

  $parents = array();

  if(!in_array($tableParents[$leftJoinTable],$tablesList)){
    $parents[] = $tableParents[$leftJoinTable];
  }

  return $parents;
} 

function bodyStyle(){
  echo "<BODY  BGCOLOR='FAFAFA' LINK=\"005830\" VLINK=\"005830\" ALINK=\"005830\">\n";
  echo "<font face=\"arial\">\n";
}

function banner(){
  global $projectName;
  echo "<div id=\"banner\"><h4><center>reda 2.0</center></h4><h5><center><b>" . $projectName . " Test Results Database</b></center></h5></div>";
}

function banner_testplan($release){
  global $projectName;
  echo "<div id=\"banner\"><h4><center>Release ".$release."</center></h4><h5><center><b>Test Plan Status</b></center></h5></div>";
}

function navbar1($page){
  echo "<div id=\"full\">";
  echo "<div class=\"post\">\n";
  echo "      <center>\n";
  if($page == "index"){
    echo "    <font color='#ECF4EC'>Main Page</font>\n";
  } else {
    echo "    <a href=\"index.php\"><font color='#ECF4EC'><b>Main Page</b></font></a>\n";
  }
  divider();
  if($page == "modify"){
    echo "    <font color='#ECF4EC'>Advanced Search</font>\n";
  } else {
    echo "    <a href=\"modify_search.php\"><font color='#ECF4EC'><b>Advanced Search</b></font></a>\n";
  }
  divider();
  if($page == "search"){
    echo "    <font color='#ECF4EC'>Resource Status</font>\n";
  } else {
    echo "    <a href=\"resource_status.php\"><font color='#ECF4EC'><b>Resource Status</b></font></a>\n";
  }
  divider();
  if($page == "release"){
    echo "    <font color='#ECF4EC'>Release Status</font>\n";
  } else {
    echo "    <a href=\"testplan.php\"><font color='#ECF4EC'><b>Release Status</b></font></a>\n";
  }
  divider();
  if($page == "help"){
    echo "    <font color=\"ECF4EC\">Help Page</font>\n";
  } else {
    echo "    <a href=\"faq.php\"><font color='#ECF4EC'><b>Help Page</b></font></a>\n";
  }
  divider();
  if($page == "admin"){
    echo "    <font color=\"ECF4EC\">Admin Page</font>\n";
  } else {
    echo "    <a href=\"admin.php\"><font color='#ECF4EC'><b>Admin Page</b></font></a>\n";
  }
  echo "      </center>\n";
  echo "</div>";
  echo "</div>";
}


function navbar2($category, $page, $query) {
  echo "<div id=\"full\">";
  echo "<div class=\"post\"><center>";
  if($category == "help"){
    navbar2_help($page);
  } elseif ($category == "results"){
    navbar2_results($page, $query);
  }
  echo "</center></div>\n";
  echo "</div>";
}

function navbar3($page){
  echo "<div id=\"full\"><div class=\"post\"><center>";
  if($page == "edit"){
    echo "  <font color=\"ECF4EC\">Edit Entry</font>\n";
  } else {
    echo "  <a href=\"edit.php\"><font color='#ECF4EC'><b>Edit Entry</b></font></a>\n";
  }
  divider();
  if($page == "manual_entry"){
    echo "  <font color=\"ECF4EC\">Add Manual Entry</font>\n";
  } else {
    echo "  <a href=\"http://" . $_SERVER['SERVER_NAME'] . "/createReport.php\"><b><font color='#ECF4EC'>Add Manual Entry</font></b></a>\n";
  }
  divider();
  if($page == "editLink"){
    echo "  <font color=\"ECF4EC\">Edit Linked Groups</font>\n";
  } else {
    echo "  <a href=\"editLinks.php\"><font color='#ECF4EC'><b>Edit Linked Groups</b></font></a>\n";
  }
  divider();  
  if($page == "edit_query"){
    echo "  <font color=\"ECF4EC\">Edit Saved Query</font>\n";
  } else {
    echo "  <a href=\"edit_query.php\"><font color='#ECF4EC'><b>Edit Saved Query</b></font></a>\n";
  }
  divider();
  echo "  <a href=\"http://" . $_SERVER['SERVER_NAME'] . "/phpmyadmin\"><b><font color='#ECF4EC'>phpMyAdmin</font></b></a>\n";
  divider();
  if($page == "webpagehelp"){
    echo "  <font color=\"ECF4EC\">Help</font>\n";
  } else {
    echo "  <a href=\"webpagehelp.php\"><font color='#ECF4EC'><b>Help</b></font></a>\n";
  }
  divider();
  echo "</center>\n";
  echo "</div></div>";
}

function navbar2_help($page) {
  if($page == "faq"){
    echo "  <font color=\"ECF4EC\">FAQ</font>\n";
  } else {
    echo "  <a href=\"faq.php\"><font color='#ECF4EC'><b>FAQ</b></font></a>\n";
  }
  divider();
  if($page == "admin"){
    echo "  <font color=\"ECF4EC\">Admin Page</font>\n";
  } else {
    echo "  <a href=\"admin.php\"><font color='#ECF4EC'><b>Admin Page</b></font></a>\n";
  }
}

function navbar2_results($page, $query) {
  $query = str_replace("\"","'",$query);
  $query = str_replace("%","%25",$query);
  echo "  <a href=\"csv.php?query=" . $query . "\"><font color='#ECF4EC'><b>Save as CSV</b></font></a>\n";

  divider();
  if($page == "modify_query"){
    echo "  <font color=\"ECF4EC\">Modify Query</font>\n";
  } else {
    echo "  <a href=\"modify_search.php?query=" . $query . "\"><font color='#ECF4EC'><b>Modify Query</b></font></a>\n";
  }
  divider();
  if($page == "save"){
    echo "  <font color=\"ECF4EC\">Save Query</font>\n";
  } else {
    echo "  <a href=\"save.php?query=" . $query . "\"><font color='#ECF4EC'><b>Save Query</b></font></a>\n";
  }
}

  
function divider() {
  echo "      &nbsp;<font color='#ECF4EC'>|</font>&nbsp;\n";
}

?>
