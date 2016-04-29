#!/bin/bash
### Test file that can be launched from AL Test GUI browser to see the environment 
### of the Apache Server CGI on the Automation Server

echo "Content-type: text/html"
echo ""
echo ""

echo ""
echo "PRINTENV"
echo ""
echo `printenv`


echo ""
echo "WHOAMI"
echo `whoami`
echo

echo ""
echo "WHICH CHROMEDRIVER"
echo `which chromedriver`

echo ""
echo "WHICH PYTHON"
echo `which python`

echo ""
echo "Finished Environment"

echo `ls /tmp`
echo `touch /tmp/altgWorkingDir/test`

#./mapbunUnitTest.py

# echo "BATCH ENV TEST"
# echo `batch <<< 'env > batchEnv.txt'`
# echo `env > env.txt`
