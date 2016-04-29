<?php
/*
 * ---------------------------------------------------------------
 *
 * File:  zipresult.php
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
	ini_set('display_errors', 1);
	error_reporting(E_ALL);

	class Zipper extends ZipArchive {
		public function addDir($path) {
			print 'adding ' . $path . '<br>';
			$this->addEmptyDir($path);
			$nodes = glob($path . '/*');
			foreach ($nodes as $node) {
				print $node . '<br>';
				if (is_dir($node)) {
					$this->addDir($node);
				} else if (is_file($node))  {
					$this->addFile($node);
				}
			}
		}
	} // class Zipper

	$foldername = "result-grpID" . $_GET['grpID'] . '.zip';
	$folderpath = './' . $foldername;

	//Zip('/opt/share/data/results/', $folderpath);
	Zip('/var/www/html/results/', $folderpath);

	if(file_exists($foldername)) {
		//Set Headers:
		header('Pragma: public');
		header('Expires: 0');
		header('Cache-Control: must-revalidate, post-check=0, pre-check=0');
		header('Last-Modified: ' . gmdate('D, d M Y H:i:s', filemtime($foldername)) . ' GMT');
		header('Content-Type: application/force-download');
		header('Content-Disposition: inline; filename="'.$foldername.'"');
		header('Content-Transfer-Encoding: binary');
		header('Content-Length: ' . filesize($foldername));
		readfile($foldername);
		unlink($foldername);
		exit();
	} else {
		echo "File does not exist";
	}

	function Zip($source, $destination) {
		if (!extension_loaded('zip') || !file_exists($source)) {
			return false;
		}

		$zip = new Zipper();

		if (!$zip->open($destination, ZIPARCHIVE::CREATE)) {
			exit("cannot open <$destination><br>");
		}

		$source = $source . $_GET['grpID'];
		$source = str_replace('\\', '/', realpath($source));

		if (is_dir($source) === true) {
			$files = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($source), RecursiveIteratorIterator::SELF_FIRST);

			foreach ($files as $file) {
				$file = str_replace('\\', '/', realpath($file));

				//if($file != "/opt/share/data/results") {
				if($file != "/var/www/html/results") {
					if (is_dir($file) === true) {
						$zip->addEmptyDir(str_replace($source . '/', '', $file . '/'));
					} else if (is_file($file) === true) {
						$zip->addFromString(str_replace($source . '/', '', $file), file_get_contents($file));
					}
				}
			}
		} else if (is_file($source) === true) {
			$zip->addFromString(basename($source), file_get_contents($source));
		}

		//print "numfiles: " . $zip->numFiles . "<br>";
		//print "status:" . $zip->status . "<br>";
		$zip->close() or die ('<br>Could not close file. Check the folder permission.<br>');
		//print "status:" . $zip->status . "<br>";
	}
?>
