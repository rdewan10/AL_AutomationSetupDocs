<?php
/*
 * ---------------------------------------------------------------
 *
 * File:  redareport.php
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
ob_start();
?>

<html>
	<head>
		<script src="jquery-1.10.1.min.js"></script>
		<script src="jquery-migrate-1.2.1.min.js"></script>
		<title>Test Execution Report</title>
	</head>
	<style>
		div {
			margin: 0 0 0 10px;
			font: normal 16px 'Arial', Arial, Sans-serif;
		}
		p {
			margin: 0 0 0 10px;
			font: normal 16px 'Arial', Arial, Sans-serif;
		}

		ul {
			margin: 0 0 0 10px;
			font: normal 16px 'Arial', Arial, Sans-serif;
		}

		table.requirement {
			margin: 0 0 0 35px;
		}

        table {font: normal 11px 'Arial', Arial, Sans-serif; border-collapse: collapse;}

		td {
			padding-right: 10px;
		}

		img {
			max-width:100%;
			max-height:100%;
		}
	</style>
	<body>
    <center><h1 style="font-family:Arial">Test Execution Report</h1></center>

	<?php
		include 'func.php';
		//ini_set('display_errors', 1);
		//error_reporting(E_ALL);
		//ini_set("auto_detect_line_endings", true);

		mysqlSetup($db);
		$groupID = $_GET["grpID"];

		$select = "SELECT GroupName, TestCase, Description, StationName, Datetime, DurationHrs, User, SpecPassFail, Notes FROM GroupInfo WHERE GrpID = " . $groupID;
		//echo "select = " . $select . "<br>";
		$results = mysql_query($select, $db);
		$groupName = "";
		$testCase = "";
		$description = "";
		$stationName = "";
		$date = "";
		$duration = "";
		$tester = "";
		$result = "";
		$note = "";

		while ($row = mysql_fetch_assoc($results)) {
			if($row['GroupName']) {
				$groupName = $row['GroupName'];
				$groupName = str_replace('_', ' ', $groupName);
				//printf("Group Name = %s <br>", $row['GroupName']);
			}
			if($row['TestCase']) {
				$testCase = $row['TestCase'];
				//printf("Test Case = %s <br>", $row['TestCase']);
			}
			if($row['Description']) {
				$description = $row['Description'];
				//printf("Description = %s <br>", $row['Description']);
			}
			if($row['StationName']) {
				$stationName = $row['StationName'];
				//printf("Station Name = %s <br>", $row['StationName']);
			}
			if($row['Datetime']) {
				$date = $row['Datetime'];
				//printf("Date = %s <br>", $row['Datetime']);
			}
			if($row['DurationHrs']) {
				$duration = $row['DurationHrs'];
				//printf("Duration = %s <br>", $row['DurationHrs']);
			}
			if($row['User']) {
				$tester = $row['User'];
				//printf("Tester = %s <br>", $row['User']);
			}
			if($row['SpecPassFail']) {
				$result = $row['SpecPassFail'];
				//printf("Result = %s <br>", $row['SpecPassFail']);
			}
			if($row['Notes']) {
				$note = $row['Notes'];
				//printf("Notes = %s <br>", $row['Notes']);
			}
		}

		$selectTestId = "SELECT TestID FROM TestInfo WHERE GrpID = " . $groupID;
		//echo "selectTestId = " . $selectTestId . "<br>";
		$resultsTestId = mysql_query($selectTestId, $db);
		$testIdArray = array();

		while($row = mysql_fetch_assoc($resultsTestId)) {
			if($row['TestID']) {
				array_push($testIdArray, $row['TestID']);
			}
		}
		//print_r($testIdArray);

		// Config  
		$dbhost = '10.86.24.211';
		$dbname = 'gtaf';

		// Connect to the database  
		$m = new MongoClient("mongodb://$dbhost");
		$mongodb = $m->selectDB($dbname);

		//Retrieve description using reda id
		$resultsCollection = new MongoCollection($mongodb, 'results');
		$idCursor = $resultsCollection->find(array('id' => $groupID));

		if($idCursor->count() !== 1) {
			echo "<!-- Database unexpectedly returned " . $idCursor->count() . " result(s) when id was queried in results. -->";
		}
		echo "<!-- count = " . $idCursor->count(),' -->';
		$name = '';
		$origName = '';

		foreach ($idCursor as $obj) {
			echo "<!-- _test Object ID = " . $obj['_test'] . ' -->';
			//$objectID = $obj['_test'];
			echo "<!-- name Object ID = " . $obj['name'] . ' -->';
			$name = $obj['name'];
		}
		if($idCursor->count() === 0) {
			$name = $testCase;
		}
		$origName = $name;

		$testsCollection = new MongoCollection($mongodb, 'doors_tests');
		//$_idCursor = $testsCollection->find(array('_id' => $objectID));
		$nameCursor = $testsCollection->find(array('name' => $name, 'imported' => true));

		if($nameCursor->count() != 1) {
			echo "<!-- Database unexpectedly returned " . $nameCursor->count() . " result(s) when $name was queried in tests. -->";
			$suite = '';

			if(substr($name,0,3)==='GAT') {
				$suite = substr($name,0,6);
				if($suite[3] !== '-') {
					preg_match('/\d\d/',$suite,$matches);
					$suitenum = $matches[0];
					$suite = 'GAT-'.$suitenum;
				}
				$name = substr($name,6);
				if($name[0]==='_') {
					$name = substr($name,1);
				}
				//$name = str_replace('-',' *- *',$name);
				if(strpos($name,'-') !== false) {
					$name = substr($name,0,strpos($name,'-'));
				}
				$name = str_replace('_','[_ -]*',$name);
				$name = '/^[_ -]*'.$name.'/i';
			}
			if($name && $suite) {
				$regex = new MongoRegex($name);
				$query = array('name' => $regex, 'suites' => str_replace('_','-',$suite));
				$nameCursor = $testsCollection->find($query);
			}
		}
		echo "<!-- count = " . $nameCursor->count() . ', newname = ' . $name . ', suites = ' . $suite . '\n query: ' . print_r($query,true) . ' -->';
		$testReqs = array();
		$testSuite = false;

		foreach ($nameCursor as $obj) {
			echo "<!-- obj = " . print_r($obj,true) . ' -->';
			$description = $obj['description'];
			$testReqs = $obj['reqs'];
			$testCaseName = $obj['name'];
			$testSuite = $obj['suites'][0];
			echo '<!-- "' . $testSuite . ' ' . str_replace('_',' ',$testCaseName) . '" =? "' . str_replace('_',' ',$origName) . '" -->';

			if(($testSuite . ' ' . str_replace('_',' ',$testCaseName)) == str_replace('_',' ',$origName)) {
				//We have an "exact" match, use it!
				echo '<!-- yes -->';
				break;
			} else {
				echo '<!-- no -->';
			}
		}
		$description = str_replace('_', ' ', $description); //Replace _ with space
		$description = nl2br($description); //Replace \n with <br>
		$description = preg_replace("/[^[:alnum:][:punct:]]/"," ",$description); //Remove all special characters.

		$requirementsCollection = new MongoCollection($mongodb, 'doors_requirements');

		$testsCursor = $requirementsCollection->find(array(
			'name' => array('$in' => $testReqs)
		));
		//$testCaseName = str_replace('_', ' ', $testCase);
		//$testCaseName = $testCase;
		if($testSuite) {
			$testCaseName = $testSuite.'_'.$testCaseName;
		} else {
			$testCaseName = str_replace('_', ' ', $testCase);
		}
		echo '<!-- req count = '.$testsCursor->count().' -->';

		$fullNBN = array();
		$fullViaSat = array();
		$partialNBN = array();
		$partialViaSat = array();
		$fullCount = 0;
		$partialCount = 0;

		foreach ($testsCursor as $obj) {
			if(count($obj['tests']) == 1) {
				//echo "<!-- Full -->";
				//echo '<!-- Name: ' . $obj['name'] . ' -->';
				//echo '<!-- Customer Name: ' . $obj['customer_name'] . ' -->';
				$fullNBN[] = $obj['customer_name'];
				$fullViaSat[] = $obj['name'];
				$fullCount += 1;
			} else if(count($obj['tests']) > 1) {
				//echo "<!-- Partial -->";
				//echo '<!-- Name: ' . $obj['name'] . ' -->';
				//echo '<!-- Customer Name: ' . $obj['customer_name'] . ' -->';
				$partialNBN[] = $obj['customer_name'];
				$partialViaSat[] = $obj['name'];
				$partialCount += 1;
			}
		}
	?>
	<hr style='height:3px; background-color:#000000; margin:0 0 0 10px'>
	<br>
	<p><b>Test Case Title: <?php echo $testCaseName ?></b></p><br>
	<p><b><span style="font-size:22px"><?php echo $testCaseName ?></b></p>
	<br>
	<br>
	<p><b>Test Description:</b><br><?php echo $description ?></p><br>
	<p><b>Requirements Satisfied by Test:</b></p><br>
	<ul><li>Fully Verified Requirements:</li></ul>
	<table class='requirement'><tbody><tr><td><p><b>NBN Co. Requirement ID</b></p></td><td><p><b>ViaSat Requirement ID</b></p></tr></td>
	<?php if($fullCount > 0) {
			foreach(array_combine($fullNBN, $fullViaSat) as $full => $partial) { echo "<tr><td><p>" . $full . "</p></td><td><p>" . $partial . "</p></tr></td>";}
		} else {
			echo "<tr><td><p>None</p></td>";
		}?><br>
	</tbody></table><br>
	<ul><li>Partially Verified Requirements:</li></ul>
	<table class='requirement'><tbody><tr><td><p><b>NBN Co. Requirement ID</b></p></td><td><p><b>ViaSat Requirement ID</b></p></tr></td>
	<?php if($partialCount > 0) {
			foreach(array_combine($partialNBN, $partialViaSat) as $full => $partial) { echo "<tr><td><p>" . $full . "</p></td><td><p>" . $partial . "</p></tr></td>";}
		} else {
			echo "<tr><td><p>None</p></td>";
		}?><br>
	</tbody></table><br>
	<hr style='height:3px; background-color:#000000; margin:0 0 0 10px'>
	<div id="header"></div>
	<br clear='all'>
	<br>
	<div id="verification"></div>
	<br clear='all'>
	<br>
	<div id="version"></div>
	<br clear='all'>
	<hr style='height:3px; background-color:#000000; margin:0 0 0 10px'>
	<div id="output"></div>
	<br>
	<script>
		function SaveToDisk(fileURL, fileName) {
			// for non-IE
			if (!window.ActiveXObject) {
				var save = document.createElement('a');
				save.href = fileURL;
				save.target = '_blank';
				save.download = fileName || 'unknown';

				var event = document.createEvent('Event');
				event.initEvent('click', true, true);
				save.dispatchEvent(event);
				(window.URL || window.webkitURL).revokeObjectURL(save.href);
			}
			// for IE
			else if ( !! window.ActiveXObject && document.execCommand) {
				var _window = window.open(fileURL, '_blank');
				_window.document.close();
				_window.document.execCommand('SaveAs', true, fileName || fileURL)
				_window.close();
			}
		};
		var link = "<table border='1'><tbody><tr bgcolor=#BCC6CC><td><p><b>Verification Point</b></p></td><td><p><b>Criteria Name</b></p></td><td><p><b>Result</b></p></td><td><p><b>Expected Value</b></p></td><td><p><b>Actual Value</b></p></td></tr>";

		function start() {
			var content;
			//var resultsDirectory = "<a href=\"/zipresult.php?grpID=<?php echo $groupID; ?>\"><?php echo "SB2 "; echo $groupID; ?></a>";
			var resultsDirectory = "<a href=\"zipresult.php?grpID=<?php echo $groupID; ?>\"><?php echo "$projectName "; echo $groupID; ?></a>";
			var header = "<br><table align='left'><tbody><tr><td><p><b>Group Name</b></p></td><td><p><?php echo $groupName; ?></p></td></td>";
			header += "<tr><td><p><b>Test Station</b></p></td><td><p><?php echo $stationName; ?></p></tr></td>";
			header += "<tr><td><p><b>Start Time</b></p></td><td><p><?php echo $date; ?></p></tr></td>";
			var result = "<?php echo $result; ?>";
			result = result.toUpperCase();
			//var directory = "results/<?php echo $groupID; ?>/<?php echo $testCase; ?>_Steps.csv";
			<?php $directory = "results/" . $groupID . "/" . $testCase . "_Steps.csv"; ?>
			<?php
			if(isset($duration)) {
				echo 'header += "<tr><td><p><b>Test Duration</b></p></td><td><p>' . $duration . ' hours</p></tr></td>";' . "\n";
			} else {
				echo 'header += "<tr><td><p><b>Test Duration</b></p></td><td><p>' . $duration . '</p></tr></td>";' . "\n";
			}
			?>
			header += "<tr><td><p><b>Tester</b></p></td><td><p><?php echo $tester; ?></p></tr></td>";

			if(result == "PASS") {
				header += "<tr><td><p><b>Test Case Result</b></p></td><td><p><b style='color:green'>" + result + "</b></p></tr></td>";
			} else if(result == "FAIL") {
				header += "<tr><td><p><b>Test Case Result</b></p></td><td><p><b style='color:red'>" + result + "</b></p></tr></td>";
			} else {
				header += "<tr><td><p><b>Test Case Result</b></p></td><td><p><b><?php echo $result; ?></b></p></tr></td>";
			}
			header += "<tr><td><p><b>Notes</b></p></td><td><p><?php echo $note; ?></p></tr></td>";
			header += "<tr><td><p><b>Results Directory</b></p></td><td><p>" + resultsDirectory + "</p></tr></td>";
			header += "</tbody></table>";

			$('#header').append(header);
			var contents = "";
			<?php $contents = ""?>
			<?php $handle = fopen($directory, "r");

			if ($handle) {
				while (($line = fgets($handle)) !== false) {
					$line = rtrim($line, "\r\n");
					$line = str_replace('\'', '\\\'', $line)."\n";
					$contents .= $line;
				}
			} else {
				echo "//Error reading a file\n";
			}?>
			contents = <?php echo json_encode($contents); ?>;

			if(contents) {
				processFile(contents);
			} else {
				<?php echo "//Empty contents\n" ?>
				versionTable();
			}
			ixiaImages();
		};

		function versionTable() {
			var versionExist = false;

			<?php $versionsDirectory = "results/" . $groupID . "/versions.csv"; ?>
			var testing = "<?php echo $versionsDirectory; ?>";
			//console.log("version = " + testing);

			var versionContents = "";
			<?php $versionContents = ""?>
			<?php $versionExist = 1?>
			<?php $handle = fopen($versionsDirectory, "r");

			if ($handle) {
				while (($line = fgets($handle)) !== false) {
					$line = rtrim($line, "\r\n");
					$line = str_replace('\'', '\\\'', $line)."\\n";
					$versionContents .= $line;
				}
			} else {
				$versionExist = 0;
				console.log("Error reading a file.");
			}?>
			versionExist = <?php echo $versionExist; ?>;
			//console.log("versionExist = " + versionExist);

			if(versionExist) {
				versionContents = '<?php echo nl2br($versionContents); ?>';
				//console.log("versionContents = " + versionContents);

				var versionLineArr = parseCsv(versionContents); //If it was AJAX, copy the function of ../modules/parseCsv into this file because require doesn't work on browser.
				versionLineArr.shift(); //remove header
				versionResponse = '';
				var version = "<p><b>Software Versions used in Test: </b></p>";
				version += "<table border='1'><tbody><tr bgcolor=#BCC6CC><td><p><b>Component</b></p></td><td><p><b>Software Version</b></p></td></td>";

				versionLineArr.forEach(function(el) {
					versionResponse += versionReduceArr(el)+'\n';
				});

				version += versionResponse;
				version += "</tbody></table><br><br>";
			}

			if(versionExist) {
				$('#version').append(version);
			}
		};

		function ixiaImages() {
			var ixiaImageExist = false;
			<?php $ixiaImageExist = 0; ?>
			var ixiaContents = "<p><b>IxOS Plots</b></p><br>";
			<?php $ixiaImageFolder = "results/" . $groupID . "/ixos/";
			$idCounter = 0;
			$lineBreak = false;

			foreach($testIdArray as $value) {
				$ixiaContents = "";
				$select = "SELECT PicName, TextAbove, TextBelow FROM TestReportPictureAnnotation WHERE SubDir=\"ixos\"";
				//echo "select = " . $select . "<br>";
				$results = mysql_query($select, $db);

				while ($row = mysql_fetch_assoc($results)) {
					$filename = "/results/" . $groupID . "/ixos/IxOsTimeSeries_" . $groupID . "_" . $value;
					$filename .= "_" . $row['PicName'];
					echo "//" . $filename . "\n";

					if(file_exists("/data" . $filename)) {
						if($idCounter < $value) {
							$ixiaContents .= "<p><b>Test ID: $value</b></p><br>";
							$idCounter = $value;
							$lineBreak = true;
							$ixiaImageExist = true;
						}
						$ixiaContents .= "<table width=\"1024px\"><tr><td><p><center>" . $row["TextAbove"] . "</center></p><p><center>" . $row["TextBelow"] . "</center></p></td></tr><tr><td>";
						$img = $filename;
						$ixiaContents .= "<a href=\"$img\"><img src=\"$img\" BORDER=0></a></td></tr></table><br>";
						echo "//$ixiaContents\n";
					} else {
						echo "//No file found at /data", $filename . "\n";
					}
				}

				if($lineBreak) {
					$lineBreak = false;
					$ixiaContents .= "<hr>";
				}

				$ixiaContents = addslashes($ixiaContents);?>
				ixiaContents += "<?php echo $ixiaContents; ?>";
			<?php }?>

			ixiaImageExist = <?php echo $ixiaImageExist; ?>;

			if(ixiaImageExist) {
				$('#ixia').append(ixiaContents);
			} else {
				<?php echo "//File does not exist\n" ?>
			}
		};

		function processFile(csv) {
			//console.log("processFile");
			//console.log("csv = " + csv);
			var lineArr = parseCsv(csv); //If it was AJAX, copy the function of ../modules/parseCsv into this file because require doesn't work on browser.
			//var result = $('#parameter').data('result');
			var result = "<?php echo $result; ?>";
			result = result.toUpperCase();
			lineArr.shift(); //remove header
			response = '';
			wrapper = '<br clear="all"><p><b>Test Procedure:</b></p><br>';
			lineArr.forEach(function(el) {
				response += reduceArr(el)+'\n';
			});
			wrapper += response;
			wrapper += "<br><hr style='height:3px; background-color:#000000'><br>";
			//wrapper += "<p><b>Test Deliverables: </b>The Results Database (ReDa) contains a folder of test run logs and test output. Any screen captures required for the test will also be kept in ReDa. Please reference the ReDa ID #<a href=\"/zipresult.php?grpID=<?php echo $groupID; ?>\">" + "<?php echo $projectName; ?>" + <?php echo $groupID; ?> + "</a>.<p><br><hr>";
			wrapper += "<p><b>Test Deliverables: </b>The Results Database (ReDa) contains a folder of test run logs and test output. Any screen captures required for the test will also be kept in ReDa. Please reference the ReDa ID #<a href=\"zipresult.php?grpID=<?php echo $groupID; ?>\">" + "<?php echo $projectName; ?>" + <?php echo $groupID; ?> + "</a>.<p><br><hr>";

			if(result == "PASS") {
				wrapper += "<p><b>Overall Test Results: </b><b style='color:green'>" + result + "</b></p><br>";
			} else if(result == "FAIL") {
				wrapper += "<p><b>Overall Test Results: </b><b style='color:red'>" + result + "</b></p><br>";
			} else {
				wrapper += "<p><b>Overall Test Results: " + result + "</b></p><br>";
			}

			wrapper += "<hr style='height:3px; background-color:#000000'>";
			//console.log(wrapper);

			link += "</tbody></table>";
			$('#output').append(wrapper);

			versionTable();

			$('#verification').append(link);
		};

		function versionReduceArr(line) {
			//console.log("versionReduceArr");

			if(line.length > 1) {
				//take a csv and output a line of the test case
				//in the format: Component Name, Type, Version
				var componentName = line[0],
				version = line[2];
				var result = "<tr><td><p><b>" + componentName + "</b></p></td><td><p><b>" + version + "</b></p></td></td>";

				return result;
			} else {
				return '';
			}
		};

		function reduceArr(line) {
			//console.log("reduceArr");

			if(line.length > 1) {
				//take a csv and output a line of the test case
				//in the format: Time, Step Number, Type, Text, Expected Result, Pass/Fail, and Result/Note
				var time = line[0],
				stepNumber = line[1],
				type = line[2],
				text=(line[3]?(line[3]):'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\\n/g,'<br>'),
				expectedResult=(line[4]?(line[4]):'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\\n/g,'<br>'),
				passFail= line[5],
				resultNote=(line[6]?(line[6]):'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\\n/g,'<br>');

				if(passFail) {
					passFail = passFail.toUpperCase();
				}
				var result = "";

				switch(type)
				{
					case "note":
						result = "<p>" + time + "<br><br><b>Note: </b>" + text + "</p><br><hr>";
					break;

					case "manual step":
						result = "<p>" + time + "<br><br><b>Step " + stepNumber + ", Manual Step: </b>"  + text + "</p><br><hr>";
					break;

					case "manual VP":
						if(passFail == "PASS") {
							result = "<p><a name='" + stepNumber + "'></a>" + time + "<br><br><b>Step " + stepNumber + ", Manual Verification Point: </b>"  + text + "</p><br><p><b>Expected Result: </b>" + expectedResult + "</p><br><p><b>Result: </b><b style='color:green'>" + passFail + "</b></p><br><p><b>Notes: </b>" + resultNote + "</p><br><hr>";
							link += "<tr><td><p><b><a href='#" + stepNumber + "'>" + stepNumber + "</a></b></p></td><td><p>" + text + "</p></td><td><p><b style='color:green'>" + passFail + "</b></p></td></tr>";
						} else if(passFail == "FAIL") {
							result = "<p><a name='" + stepNumber + "'></a>" + time + "<br><br><b>Step " + stepNumber + ", Manual Verification Point: </b>"  + text + "</p><br><p><b>Expected Result: </b>" + expectedResult + "</p><br><p><b>Result: </b><b style='color:red'>" + passFail + "</b></p><br><p><b>Notes: </b>" + resultNote + "</p><br><hr>";
							link += "<tr><td><p><b><a href='#" + stepNumber + "'>" + stepNumber + "</a></b></p></td><td><p>" + text + "</p></td><td><p><b style='color:red'>" + passFail + "</b></p></td></tr>";
						} else {
							result = "<p><a name='" + stepNumber + "'></a>" + time + "<br><br><b>Step " + stepNumber + ", Manual Verification Point: </b>"  + text + "</p><br><p><b>Expected Result: </b>" + expectedResult + "</p><br><p><b>Result: " + passFail + "</b></p><br><p><b>Notes: </b>" + resultNote + "</p><br><hr>";
							link += "<tr><td><p><b><a href='#" + stepNumber + "'>" + stepNumber + "</a></b></p></td><td><p>" + text + "</p></td><td><p><b>" + passFail + "</b></p></td></tr>";
						}
					break;

					case "auto step":
						result = "<p>" + time + "<br><br><b>Step " + stepNumber + ", Auto Step: </b>"  + text + "</p><br><hr>";
					break;

					case "screen capture":
						result = "<p>" + time + "<br><br><b>Screen Capture:</b></p>" + "<img src=\"results/<?php echo $groupID; ?>/" + text + "\" alt='Picture'><br><br><hr>";
					break;

					case "auto VP":
						if(passFail == "PASS") {
							result = "<p><a name='" + stepNumber + "'></a>" + time + "<br><br><b>Step " + stepNumber + ", Auto Verification Point: </b>"  + text + "</p><br><p><b>Result: </b><b style='color:green'>" + passFail + "</b></p><br><p><b>Expected Value: </b>" + expectedResult + "</p><br><p><b>Actual Value: </b>" + resultNote + "</p><br><hr>";
							link += "<tr><td><p><b><a href='#" + stepNumber + "'>" + stepNumber + "</a></b></p></td><td><p>" + text + "</p></td><td><p><b style='color:green'>" + passFail + "</b></p></td><td><p>" + expectedResult + "</p></td><td><p>" + resultNote + "</p></td></tr>";
						} else if(passFail == "FAIL") {
							result = "<p><a name='" + stepNumber + "'></a>" + time + "<br><br><b>Step " + stepNumber + ", Auto Verification Point: </b>"  + text + "</p><br><p><b>Result: </b><b style='color:red'>" + passFail + "</b></p><br><p><b>Expected Value: </b>" + expectedResult + "</p><br><p><b>Actual Value: </b>" + resultNote + "</p><br><hr>";
							link += "<tr><td><p><b><a href='#" + stepNumber + "'>" + stepNumber + "</a></b></p></td><td><p>" + text + "</p></td><td><p><b style='color:red'>" + passFail + "</b></p></td><td><p>" + expectedResult + "</p></td><td><p>" + resultNote + "</p></td></tr>";
						} else {
							result = "<p><a name='" + stepNumber + "'></a>" + time + "<br><br><b>Step " + stepNumber + ", Auto Verification Point: </b>"  + text + "</p><br><p><b>Result: " + passFail + "</b></p><br><p><b>Expected Value: </b>" + expectedResult + "</p><br><p><b>Actual Value: </b>" + resultNote + "</p><br><hr>";
							link += "<tr><td><p><b><a href='#" + stepNumber + "'>" + stepNumber + "</a></b></p></td><td><p>" + text + "</p></td><td><p><b>" + passFail + "</b></p></td><td><p>" + expectedResult + "</p></td><td><p>" + resultNote + "</p></td></tr>";
						}
					break;

					case "config step":
						result = "<p>" + time + "<br><br><b>Step " + stepNumber + ", Configure Step: </b>"  + text + "</p><br><hr>";
					break;

					default:
						//console.log("default");
					break;
				}

				return result;
				//return '<tr><td>' + time + '</td><td>' + stepNumber + '</td><td>' + type + '</td><td>' + text + '</td><td>' + expectedResult + '</td><td>' + passFail + '</td><td>' + resultNote + '</td></tr>';
			} else {
				return '';
			}
		};

		function parseCsv(strData) {
			//console.log("parseCsv");
			// Check to see if the delimiter is defined. If not,
			// then default to comma.
			var strDelimiter = (strDelimiter || ",");
			// Create a regular expression to parse the CSV values.
			var objPattern = new RegExp((
				// Delimiters.
				"(\\" + strDelimiter + "|\\r?\\n|\\r|^)" +
				// Quoted fields.
				"(?:\"([^\"]*(?:\"\"[^\"]*)*)\"|" +
				// Standard fields.
				"([^\"\\" + strDelimiter + "\\r\\n]*))"
			),
			"gi"
			);
			// Create an array to hold our data. Give the array
			// a default empty first row.
			var arrData = [[]];
			// Create an array to hold our individual pattern
			// matching groups.
			var arrMatches = null,
			strMatchedValue = '';
			// Keep looping over the regular expression matches
			// until we can no longer find a match.
			while (null != (arrMatches = objPattern.exec( strData ))) {
				// Get the delimiter that was found.
				var strMatchedDelimiter = arrMatches[ 1 ];
				// Check to see if the given delimiter has a length
				// (is not the start of string) and if it matches
				// field delimiter. If id does not, then we know
				// that this delimiter is a row delimiter.
				if (strMatchedDelimiter.length && (strMatchedDelimiter !== strDelimiter)) {
					// Since we have reached a new row of data,
					// add an empty row to our data array.
					arrData.push( [] );
				}
				// Now that we have our delimiter out of the way,
				// let's check to see which kind of value we
				// captured (quoted or unquoted).
				if (arrMatches[ 2 ]) {
					// We found a quoted value. When we capture
					// this value, unescape any double quotes.
					strMatchedValue = arrMatches[ 2 ].replace(new RegExp( "\"\"", "g" ), "\"");
				} else {
					// We found a non-quoted value.
					strMatchedValue = arrMatches[ 3 ];
				}
				// Now that we have our value string, let's add
				// it to the data array.
				arrData[ arrData.length - 1 ].push( strMatchedValue );
			}
			// Return the parsed data.
			return( arrData );
		}
		$(document).ready(start);
	</script>
		<div id="ixia"></div>
		<br clear='all'>
	</body>
</html>
<?php
/*<script id="parameter" data-group-id="<?php echo $groupID; ?>" data-group-name="<?php echo $groupName; ?>" data-test-case="<?php echo $testCase; ?>" data-station-name="<?php echo $stationName; ?>" data-date="<?php echo $date; ?>" data-duration="<?php echo $duration; ?>" data-tester="<?php echo $tester; ?>" data-result="<?php echo $result; ?>" data-note="<?php echo $note; ?>" language="JavaScript" type="text/javascript" src="read-csv.js"></script>*/
$file = fopen("results/" . $groupID . "/$projectName_" . $groupID . "_Summary_Report.html", 'w');
$contents = ob_get_contents();
fwrite($file, $contents);
fclose($file);
ob_end_clean();
echo $contents;
?>
