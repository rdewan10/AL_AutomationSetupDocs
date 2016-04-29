<?php
/*
 * ---------------------------------------------------------------
 *
 * File:  results.php
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
 & Filename: result.php
 * Purpose: The meat of Reda's searching system, the result page takes a query
 *          and converts it into a mysql query. Afterwards, it displays the
 *          results.
 *
 *****************************************************************************/

include 'func.php';
mysqlSetup($db);
//while(list($key, $value) = each($_POST)){
//  $input[$key] = $value;
//}
//Typical error message
$constructionError="ERROR: Your search was improperly constructed. Enter in a <a href=modify_search.php>new search</a> or hit the Back button to revise your search.";
if($_GET != NULL){
  while(list($key, $value) = each($_GET)){
    $input[$key] = $value;
  }
  if(isset($input["query"])) { //Top10, saved search, custom query or...
    $query = str_replace("\\","",$input["query"]);

    if(isset($input["colsort"])) {  // ...the user clicked on a column header to sort results by that column.
      if(strpos(strtolower($query),"order by")) {
        $orderpos=strpos(strtolower($query),"order by");
        $sortasc=$input["colsort"] . " ASC";
        $sortdesc=$input["colsort"] . " DESC";
        if(strpos(strtolower($query),strtolower($sortasc))){
          $query = str_replace($sortasc,$sortdesc,$query);
        } elseif(strpos(strtolower($query),strtolower($sortdesc))){
          $query = str_replace($sortdesc,$sortasc,$query);
        } else {
          $query = substr($query, 0, $orderpos);
          $query .= "ORDER BY " . $sortasc;
        }
      } else {
        $query .= " ORDER BY " . $input["colsort"] . " ASC";
      }
    } elseif(isset($input["notes"]) && $input["notes"]==0){ //The user turned off notes

      //First, we have to get our bearings and split the query into
      //manageable pieces.
      $from_index = strpos(strtolower($query)," from");
      $where_index = strpos(strtolower($query)," where");
      $order_index = strpos(strtolower($query)," order by");
      $group_index = strpos(strtolower($query)," group by");
      $selectFields = substr($query,7,$from_index-7);

      //get rid of the comment fields
      foreach($commentFieldNames as $commentField){
        $selectFields = str_replace($commentField,"",$selectFields);
      }
      do{
        //Get rid of the "," that got left behind
        $select_temp = $selectFields;
        $selectFields = str_replace(",,",",",$selectFields);
      } while ($select_temp != $selectFields);

      if($selectFields[0]==","){
        $selectFields = substr($selectFields,1);
      }
      //Forming the query minus the comment fields
      $newquery = "SELECT " . $selectFields;
      if($newquery[strlen($newquery)-1]==","){
        $newquery = substr($newquery,0,strlen($newquery)-1);
      }
      $newquery .= " FROM ";

      if($where_index!=0){
        $tables = substr($query,$from_index+6,$where_index-$from_index-6);
      } elseif($order_index != 0 && ($order_index<$group_index || $group_index=0)){
        $tables = substr($query,$from_index+6,$order_index-$from_index-6);
      } elseif($group_index != 0 && ($group_index<$order_index || $order_index=0)){
        $tables = substr($query,$from_index+6,$group_index-$from_index-6);
      }
      foreach($commentFieldNames as $commentField){
        $commentField = substr($commentField,0,strpos($commentField,"."));
        if(($pos = strpos($tables," LEFT JOIN " . $commentField))!==FALSE){
          $leftJoin = substr($tables,$pos);
          $pos = strpos($leftJoin,",");
          $leftJoin = substr($leftJoin,0,$pos);
          $tables = str_replace($leftJoin,"",$tables);
        }
      }
      $newquery .= $tables;

      $i=0;
      while($pos = strpos($tables,",")) {
        $table = substr($tables, 0, $pos);
        if(($pos2 = strpos($table," LEFT JOIN"))!==FALSE){
          $tablesList[$i] = substr($table, 0, $pos2);
        } else {
          $tablesList[$i] = substr($tables, 0, $pos);
        }
        $tables = substr($tables, $pos+1);
        $i++;
      }
      $tablesList[$i]=$tables;
      $newquery .= " WHERE ((" . tableLink($tablesList) . "))";
      $paren_index = strpos($query,"))");
      if($paren_index>0){
        $newquery .= substr($query,$paren_index+2);
      }
      $query = $newquery;

    } elseif(isset($input["notes"]) && $input["notes"]==1){ //User wants to display comments
      $from_index = strpos(strtolower($query)," from");
      $where_index = strpos(strtolower($query)," where");
      $order_index = strpos(strtolower($query)," order by");
      $group_index = strpos(strtolower($query)," group by");
      $selectFields = substr($query,7,$from_index-7);

      foreach($commentFieldNames as $commentField){
        $selectFields = str_replace($commentField,"",$selectFields);
      }
      do{
        $select_temp = $selectFields;
        $selectFields = str_replace(",,",",",$selectFields);
      } while ($select_temp != $selectFields);

      if($selectFields[0]==","){
        $selectFields = substr($selectFields,1);
      }
      $newquery = "SELECT " . $selectFields;
      if($newquery[strlen($newquery)-1]==","){
        $newquery = substr($newquery,0,strlen($newquery)-1);
      }

      foreach($commentFieldNames as $commentField){
        $newquery .= "," . $commentField;
      }

      if($where_index!=0){
        $tables = substr($query,$from_index+6,$where_index-$from_index-6);
      } elseif($order_index != 0 && ($order_index<$group_index || $group_index=0)){
        $tables = substr($query,$from_index+6,$order_index-$from_index-6);
      } elseif($group_index != 0 && ($group_index<$order_index || $order_index=0)){
        $tables = substr($query,$from_index+6,$group_index-$from_index-6);
      }
      foreach($commentFieldNames as $commentField){
        $tableName = substr($commentField,0,strpos($commentField,"."));
        $tables= str_replace($tableName,"",$tables);
      }
      while($pos = strpos($tables," LEFT JOIN  ON .")){
        $leftJoin = substr($tables,$pos);
        $pos = strpos($leftJoin,",");
        $leftJoin = substr($leftJoin,0,$pos);
        $tables = str_replace($leftJoin,"",$tables);
      }

      do{
        $tables_temp = $tables;
        $tables = str_replace(",,",",",$tables);
      } while ($tables_temp != $tables);

      if($tables[0]==","){
        $tables = substr($tables,1);
      }
      if($tables[strlen($tables)-1]==","){
        $tables = substr($tables,0,strlen($tables)-1);
      }
      $i=0;
      $tempTables = $tables;
      //Make an array out of our string so we can parse the tables better
      while($pos = strpos($tempTables,",")) {
        $tablesList[$i] = substr($tempTables, 0, $pos);
        $i++;
        $tempTables = substr($tempTables, $pos+1);
      }
      if($tempTables!=""){
        $tablesList[$i]=$tempTables;
        $num_table_fields=$i+1;
      }

      foreach($commentFieldNames as $commentField){
        $commentTable = substr($commentField,0,strpos($commentField,"."));
        if(in_array($commentTable,$optionalTables)){ //comment field neeeds
                                                     //a left join with its
                                                     //parent.
          if(strpos($tables,$tableParents[$commentTable])===FALSE){ 
            $tablesList[$num_table_fields]=$tableParents[$commentTable];
            $num_table_fields++;
            $tableLink=tableLink($tablesList);
            $tableLinkTemp = $tableLink;
            //See if there are any tables in the linking clause that is not
            //in our list of tables.
            do {
              $tableNameEnd = strpos($tableLinkTemp,".");
              //In case the table link is empty
              if($tableNameEnd===FALSE){
                break;
              }
              $table = substr($tableLinkTemp,0,$tableNameEnd);

              $tableAlreadyAccountedFor =0;
              if(in_array($table,$tablesList)){
                  $tableAlreadyAccountedFor =1;
                }
              if($tableAlreadyAccountedFor==0){
                $tablesList[$num_table_fields]=$table;
                $num_table_fields++;
              }
              $tableLinkTemp = substr($tableLinkTemp,strpos($tableLinkTemp,"=")+1);
              $tableNameEnd = strpos($tableLinkTemp,".");
              $table = substr($tableLinkTemp,0,$tableNameEnd);

              if(in_array($table,$tablesList)){
                $tableAlreadyAccountedFor =1;
              } else {
                $tableAlreadyAccountedFor=0;
              }
              if($tableAlreadyAccountedFor==0){
                $tablesList[$num_table_fields]=$table;
                $num_table_fields++;
              }
              $stillMoreToProcess = strpos($tableLinkTemp," AND ");
              $tableLinkTemp = substr($tableLinkTemp,$stillMoreToProcess+5);
            } while($stillMoreToProcess);

            $tables="";
            foreach ($tablesList as $table){
              $tables = $tables . $table . ",";
            }
            $tables = substr($tables,0,strlen($tables)-1);
          }
          $join = " LEFT JOIN " . $commentTable . " ON " .
                    $commentTable . "." . $tableKeyField[$commentTable] . "=" .
                    $tableParents[$commentTable] . "." . $tableKeyField[$commentTable];
          $tables = str_replace($tableParents[$commentTable],$tableParents[$commentTable] . $join,$tables);
        } else {
          $tableName = substr($commentField,0,strpos($commentField,"."));
          if(strpos($tables,$tableName)===FALSE){
            $tables .= "," . $tableName;
            $tablesList[$num_table_fields]=$tableName;
            $num_table_fields++;
          }
        }
      }

      $newquery .= " FROM " . $tables;

      $newquery .= " WHERE ((" . tableLink($tablesList) . "))";
      $paren_index = strpos($query,"))");
      if($paren_index>0){
        $newquery .= substr($query,$paren_index+2);
      } elseif($where_index!=0){
        $newquery .= " AND " . substr($query,$where_index+6);
      }
      $query = $newquery; 
    }
    
    $update="UPDATE $savedQueryTableName SET $savedQueryCountFieldName = $savedQueryCountFieldName + 1 WHERE $savedQueryFieldName=\"" . $query . "\"";
    mysql_query($update,$db);

  } elseif($input["searchtype"]=="recent"){//User wanted to see results spanning back a certain period of time
    if($input["pastTime"]=="day"){
      $date = date("Y-m-d G:i:s",mktime(0, 0, 0, date("m"), date("d")-1, date("Y")));
    } elseif($input["pastTime"]=="week"){
      $date = date("Y-m-d G:i:s",mktime(0, 0, 0, date("m"), date("d")-7, date("Y")));
    } elseif($input["pastTime"]=="2weeks"){
      $date = date("Y-m-d G:i:s",mktime(0, 0, 0, date("m"), date("d")-14, date("Y")));
    } elseif($input["pastTime"]=="3weeks"){
      $date = date("Y-m-d G:i:s",mktime(0, 0, 0, date("m"), date("d")-21, date("Y")));
    } elseif($input["pastTime"]=="month"){
      $date = date("Y-m-d G:i:s",mktime(0, 0, 0, date("m")-1, date("d"), date("Y")));
    }
    if($input["pastTime"]!="forever"){
      $query = "SELECT " . sortFields(getSimplifiedFieldsAsArray()) . " FROM " . getSimplifiedTables() . " WHERE ((" . 
                tableLink(getsimplifiedTablesAsArray()) . ")) AND $grpLevelTableName.$grpDateFieldName>='$date'";
    } else {
      $query = "SELECT " . sortFields(getSimplifiedFieldsAsArray()) . " FROM " . getSimplifiedTables() . " WHERE ((" .
                tableLink(getsimplifiedTablesAsArray()) . "))";
    }

    if($input["testStation"]!="" && $input["testStation"]!="all"){
      $query .= " AND $grpLevelTableName.$testStationFieldName='" . $input["testStation"] . "'";
    }
    if(isset($input["overnight"]) && $input["overnight"]==1){
      $query .= " AND $grpLevelTableName.DurationHrs>8";
    }
    //$query .= " AND $testLevelTableName.Status!='invalid' ORDER BY $grpLevelTableName.$grpIDField DESC";
    $query .= " ORDER BY $grpLevelTableName.$grpIDField DESC";

  } elseif($input["searchtype"]=="id"){
    $id = strtolower($input["searchmatch"]);
    do{
      $temp_id = $id;
      $id = str_replace(";",",",$id);
      $id = str_replace(".",",",$id);
      $id = str_replace("and",",",$id);
      $id = str_replace(" ",",",$id);
      $id = str_replace(",,",",",$id);
    } while($temp_id != $id);
    
    if($id[strlen($id)-1] == ","){
      $id = substr($id,0,strlen($id)-1);
    }
    $idCount = 0;
    while(strpos($id, ",") !== FALSE){
      $singleId = substr($id,0,strpos($id, ","));
      $idList[$idCount] = $singleId;
      $idCount++;
      $id = substr($id,strpos($id, ",")+1);
    }
    $idList[$idCount] = $id;
    $idCount++;

    $query = "SELECT " . sortFields(getDefaultFieldsAsArray()) . " FROM " . getDefaultTables() . " WHERE (";
      for($i=0;$i<$idCount;$i++){
        $query .="$grpLevelTableName." . $input["idtype"] . $input["searchop"] . $idList[$i] .  " OR ";
      }

    $query = substr($query,0,strlen($query)-4);
    $query .= ")";

  } elseif($input["searchtype"]=="advanced"){
    $query = "SELECT ";
    if($input["display"] == "fields"){
      if($input["fields"][0]==""){
        $input["fields"][0]="default";
      }
      if($input["fields"][0]=="default"){
        $query .= sortFields(getDefaultFieldsAsArray());
        $tables = getDefaultTablesAsArray(); 
        $count=count(getDefaultFieldsAsArray());
      } else if($input["fields"][0]=="simplified"){
        $query .= sortFields(getSimplifiedFieldsAsArray());
        $tables = getSimplifiedTablesAsArray();
        $count=count(getSimplifiedFieldsAsArray());
      } else {
        $count=count($input["fields"]);
        for ($i=0; $i<$count; $i++) {
          $tableAlreadyAccountedFor =0;
          for($j=0;$j<$i;$j++){
            if($fields[$i]== "GroupInfo.GrpID as Report"){
              if($tables[$j]== "GroupInfo"){
                $tableAlreadyAccountedFor =1;
                break;
              }
            } else if($tables[$j]== substr($input["fields"][$i],0,strpos($input["fields"][$i],"."))){
              $tableAlreadyAccountedFor =1;
              break;
            }
          }
          if($tableAlreadyAccountedFor==0){
            if($fields[$i]== "GroupInfo.GrpID as Report"){
              $tables[$i] ="GroupInfo";
            } else {
              $tables[$i] = substr($input["fields"][$i],0,strpos($input["fields"][$i],"."));
            }
          }
        }
        $query .= sortFields($input["fields"]);
      }
    } elseif ($input["display"] == "aggregate"){
        if($input["groupbyfield"] != "") {
          $query .= $input["groupbyfield"] . ",";
          $tables[1] = substr($input["groupbyfield"],0,strpos($input["groupbyfield"],"."));
        }
        $query .= $input["aggregateop"] . "(" . $input["aggregatefield"] . ") " . 
                  $input["aggregateop"] . "_of_" . 
                  substr($input["aggregatefield"],strpos($input["aggregatefield"],".")+1);
        if($tables[1] != substr($input["aggregatefield"],0,strpos($input["aggregatefield"],"."))){
          $tables[0] = substr($input["aggregatefield"],0,strpos($input["aggregatefield"],"."));
        }
        $count = 2;
    }

    $condition=""; 
    if($input["searchfield0"] != ""){//User, in advanced search, listed some criteria
      for($i = 0; $i < 6; $i++) {
          $tempfield = "searchfield" . $i;
          $tempop = "searchop" . $i;
          $tempmatch = "searchmatch" . $i;
          $tempjoin = "searchjoin" . $i;
        if($i==0 || $input[$tempjoin] != ""){
          if($i > 0 && $input[$tempjoin] != ""){
            $condition .= " " . $input[$tempjoin] . " ";
          }
          if($input[$tempfield]!= ""){
            $condition .= $input[$tempfield] . " " .$input[$tempop] . " '" . $input[$tempmatch] . "'";
            $tableAlreadyAccountedFor =0;
            for($j=0;$j<$count;$j++){
              if($tables[$j]== substr($input[$tempfield],0,strpos($input[$tempfield],"."))){
                $tableAlreadyAccountedFor =1;
                break;
              }
            }
            if($tableAlreadyAccountedFor==0){
              $tables[$count]=substr($input[$tempfield],0,strpos($input[$tempfield],"."));
              $count++;
            }
          } else {
            $constructionError="ERROR: You specified a join condition without specifying the next search criterion.";
          }
        }
      }
    }
    if(isset($input["invalid"]) && $input["invalid"]==1){
      $tableAlreadyAccountedFor =0;
      for($j=0;$j<$count;$j++){
        if($tables[$j]== "$grpLevelTableName"){
          $tableAlreadyAccountedFor =1;
          break;
        }
      }
      if($tableAlreadyAccountedFor==0){
        $tables[$count]="$grpLevelTableName";
        $count++;
      }
    }

    if(isset($input["relativetime"]) && $input["relativetime"]==1){ //invalid and relativetime are checkboxes
      $tableAlreadyAccountedFor =0;
      for($j=0;$j<$count;$j++){
        if($tables[$j]== "$grpLevelTableName"){
          $tableAlreadyAccountedFor =1;
          break;
        }
      }
      if($tableAlreadyAccountedFor==0){
        $tables[$count]="$grpLevelTableName";
        $count++;
      }
    }

    $query .= " FROM ";
    //We sould add any optional table's parents so that table link
    //will work properly.
    $parents = array();
    foreach($tables as $table){
      if(in_array($table,$optionalTables)){
        $parents[] = $tableParents[$table];
      }
    }
    $parents = array_unique($parents);
    $tables = array_merge($tables,$parents);
    $tables = array_unique($tables);

    //By using tableLink, we can determine if there are any linking
    //tables that are no in the original table list
    $tableLink = tableLink($tables);
    $tableLinkTemp = $tableLink;
    do {
      $tableNameEnd = strpos($tableLinkTemp,".");
      //In case the table link is empty
      if($tableNameEnd===FALSE){
        break;
      }
      $table = substr($tableLinkTemp,0,$tableNameEnd);
      $tableAlreadyAccountedFor =0;
      for($j=0;$j<$count;$j++){
        if($tables[$j]== $table){
          $tableAlreadyAccountedFor =1;
          break;
        }
      }
      if($tableAlreadyAccountedFor==0){
        $tables[$count]=$table;
        $count++;
      }
      $tableLinkTemp = substr($tableLinkTemp,strpos($tableLinkTemp,"=")+1);
      $tableNameEnd = strpos($tableLinkTemp,".");
      $table = substr($tableLinkTemp,0,$tableNameEnd);
      for($j=0;$j<$count;$j++){
        if($tables[$j]== $table){
          $tableAlreadyAccountedFor =1;
          break;
        }
      }
      if($tableAlreadyAccountedFor==0){
        $tables[$count]=$table;
        $count++;
      }
      $stillMoreToProcess = strpos($tableLinkTemp," AND ");
      $tableLinkTemp = substr($tableLinkTemp,$stillMoreToProcess+5);
    } while($stillMoreToProcess);

    foreach($tables as $table){
      if(!in_array($table,$optionalTables)){
        $query .= "$table";
        if(in_array($table,$parents)){
          foreach($tables as $table2){
            if(in_array($table2,$optionalTables) && $tableParents[$table2]==$table){
              $leftJoinTable = $table2;
              $query .= " LEFT JOIN " .  $leftJoinTable . " ON " . 
                        $leftJoinTable . "." . $tableKeyField[$leftJoinTable] . "=" .
                        $table . "." . $tableKeyField[$leftJoinTable];
            }
          }
        }
        $query .= ",";
      }
    }
    $query = substr($query,0,-1);

    if($tableLink != NULL || $input["searchfield0"] != "" || $input["invalid"]==1 || $input["relativetime"]==1){
      $query .= " WHERE ";
    }
    if($tableLink != NULL){
      $query .= "((" . $tableLink . "))";
    }
    if($input["searchfield0"] != "" && $tableLink != NULL){
      $query .= " AND (" . $condition . ")";
    } elseif($input["searchfield0"] != ""){
      $query .= "(" . $condition . ")";
    }

    if (isset($input["invalid"]) && $input["invalid"]==1){
      if($input["searchfield0"] != "" || $tableLink != NULL){
        $query .= " AND";
      }
      $query .=" $grpLevelTableName.Status!='invalid'";
    }
    if (isset($input["relativetime"]) && $input["relativetime"]==1){
      if($input["searchfield0"] != "" || $tableLink != NULL || $input["invalid"]==1){
        $query .= " AND";
      } 
      $query .= " $grpLevelTableName.Datetime>=DATE_SUB(NOW(),INTERVAL " . $input["timevalue"] . " " . $input["timeunit"] . ")";
    }
    
    if ($input["display"] == "aggregate" && $input["groupbyfield"] != ""){
      $query .= " GROUP BY " . $input["groupbyfield"];
    }
    if($input["sortfield0"] != "") {
      $query .= " ORDER BY ";
      for($i = 0; $i < 3; $i++) {
        $tempfield = "sortfield" . $i;
        $tempop = "sortop" . $i;
        if($i > 0 && $input[$tempfield] != ""){
          $query .= ",";
        }
        if($input[$tempfield]!= ""){
          $query .= $input[$tempfield] . " " . $input[$tempop];
        }
      }
    }
  }
}
//Make sure the query is not malicious.
$query=str_replace("delete","",$query);
$query=str_replace("update","",$query);
$query=str_replace("truncate","",$query);
?>
<!-- For Help with basic HTML and PHP, consult the commets in index.php -->
<html>
<HEAD>
<TITLE>Query Results</TITLE>
<link rel="stylesheet" type="text/css" href="reda.css">
</head>
<?php
bodyStyle();
banner();
navbar1("results");
navbar2("results", "results", $query);
echo "<br><br>";
$result = mysql_query($query,$db);

if($result){
  if(isset($input["notes"]) && $input["notes"]==1){
    echo "<a href=\"results.php?query=$query&notes=0\">Disable Notes and Descriptions</a><br>";
  } else {
    echo  "<a href=\"results.php?query=$query&notes=1\">See Notes and Descriptions</a><br>";
  }

  echo "<table border=0>";
  echo "<tr>";

  $results_links_index = -1;
  $testid_index = -1;
  $grpid_index=-1;

  for ($i = 0; $i < mysql_num_fields($result);$i++){
    echo "<td BACKGROUND=\"images/bg_hdr1.gif\"><font face=\"arial\" size=2><b><center>
          <a href=\"results.php?query=" . str_replace("\"","'",$query) . "&colsort=";
    if(mysql_field_table($result, $i)){
          echo mysql_field_table($result, $i) . ".";
    }
    echo mysql_field_name($result, $i) . "\"><font color=\"ECF4EC\">" . mysql_field_name($result, $i) . "</font></b>";
    echo "</a></center></font></td>";

	if(mysql_field_name($result, $i)=="Results"){
      $results_links_index = $i;
    } elseif(mysql_field_name($result, $i)==$testIDField){
      $testid_index = $i;
    } elseif(mysql_field_name($result, $i)==$grpIDField){
      $grpid_index = $i;
    }

    if(($input["searchtype"]=="recent" || $input["fields"][0]=="simplified" || isset($input["notes"]) && $input["notes"]==1) &&
         ($i == $results_links_index || ($results_links_index==-1 && $i==1 && mysql_field_name($result,0)=="Report") || ($results_links_index==-1 && $i=00))){
      echo "<td BACKGROUND=\"images/bg_hdr1.gif\"><font face=\"arial\" size=2><font color=\"ECF4EC\"><b><center>Edit</b></center></font></font></td>";
    }

	//This is for adding an extra column Summary next to Report column
    if($i==0 && mysql_field_name($result,0)=="Report")
    {
	echo "<td BACKGROUND=\"images/bg_hdr1.gif\"><font face=\"arial\" size=2><font color=\"ECF4EC\"><b><center>Summary</b></center></font></font></td>";
    }
  }
  echo "</tr>";

  while ($myrow = mysql_fetch_row($result)){
    for ($i = 0; $i < mysql_num_fields($result);$i++){
      if(mysql_field_name($result,$i)=="Report"){
        printf("<td bgcolor=\"F0F0F0\" rowspan=1><font size=2><a href=\"report.php?grpID=%s\"><center><img src='images/addressbookWindow.png' width='20px' height='20px' style='border-style: none'></center></a></font></td>",$myrow[$i]);
      } else if($i == $results_links_index){
        #printf("<td bgcolor=\"F0F0F0\" rowspan=1><font size=2><a href=\"%s\"><center><img src='images/folder_aphrodite_green_with_gray_background.jpg' width='25px' height='25px' style='border-style: none'></center></a></font></td>",$myrow[$i]);
        //printf("<td bgcolor=\"F0F0F0\" rowspan=1><font size=2><a href=\"/zipresult.php?grpID=%s\"><center><img src='images/folder_aphrodite_green_with_gray_background.jpg' width='25px' height='25px' style='border-style: none'></center></a></font></td>",$myrow[$grpid_index]);
        printf("<td bgcolor=\"F0F0F0\" rowspan=1><font size=2><a href=\"zipresult.php?grpID=%s\"><center><img src='images/folder_aphrodite_green_with_gray_background.jpg' width='25px' height='25px' style='border-style: none'></center></a></font></td>",$myrow[$grpid_index]);
/*
      } elseif ($i == $testid_index){
        $grpResult = mysql_query("SELECT $grpIDField FROM $testLevelTableName WHERE $testIDField=" . $myrow[$i],$db);
        $temp_row = mysql_fetch_row($grpResult);
        $grpID=$temp_row[0];
        printf("<td bgcolor=\"F0F0F0\" rowspan=1><font size=2><a href=\"report.php?grpID=%s\"><b><center>%s</center></b></a></font></td>",$grpID,$myrow[$i]);
*/
      } elseif ($i == $grpid_index){
        echo "<td bgcolor=\"F0F0F0\" rowspan=1><font size=2><a href=\"results.php?query=SELECT " . getDefaultFields() .
             " FROM " . getDefaultTables() . " WHERE ((" . tableLink(getDefaultTablesAsArray()) . 
             ")) AND $grpLevelTableName.$grpIDField=" . $myrow[$i] . "\"><b><center>" . $projectName . "&nbsp;" . $myrow[$i] . "</center></b></a></font></td>";
      } elseif(mysql_field_type($result,$i)=="blob" || mysql_field_type($result,$i)=="string"){
        printf("<td bgcolor=\"F0F0F0\"><font size=2>%s</font></td>",$myrow[$i]);
      } else {
        printf("<td bgcolor=\"F0F0F0\"><font size=2><center>%s</center></font></td>",$myrow[$i]);
      }

      if(($input["searchtype"]=="recent" || $input["fields"][0]=="simplified" ||
         isset($input["notes"]) && $input["notes"]==1) &&
         ($i == $results_links_index || ($results_links_index==-1 && $i==1 && mysql_field_name($result,0)=="Report") || ($results_links_index==-1 && $i==0))){
         echo "<td bgcolor=\"F0F0F0\"><font size=2>";
        if($grpid_index ==-1){
          echo "<center>cannot edit</center>";
        } else {
          echo "<a href=\"edit.php?grpID=" . $myrow[$grpid_index];

          if($testid_index != -1){
            echo "&ID=" . $myrow[$testid_index];
          }
          echo "\"><center><img src='images/edit.png' width='25px' height='25px' style='border-style: none'></center></a>";
        }
        echo "</font></td>";
      }
		//This is for adding an extra column Summary next to Report column
		if($i==0 && mysql_field_name($result,$i)=="Report"){
			printf("<td bgcolor=\"F0F0F0\" rowspan=1><font size=2><a href=\"redareport.php?grpID=%s\"><center><img src='images/report.ico' width='20px' height='20px' style='border-style: none'></center></a></font></td>",$myrow[$i]);
		}
	}
    echo "</tr>";
  }
  echo "</table>";
  } else {
    echo "<br><center>$constructionError</center><br>";
    echo "<br><center>" . mysql_error() . "</center><br>";
  }
  echo "<br><br><br><br><font size=1>Using the Query: \"" . $query . "\"</font><br>";
?>
</font>
</body>

