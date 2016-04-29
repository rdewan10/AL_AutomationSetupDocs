#!/usr/bin/env python

from cgiSetup import *
from aldbConf import *
from aldbDefaults import *
from string import Template
from altgScreen import changeGroup
import subprocess, re, random, sys

data = changeGroup()
form = data['form']

if form.getvalue('groupId'):
	groupId = data['groupId']
else:
	groupId = aldbConf.getGroup(aldbConnParmsGet(), True)

conf = aldbConf(groupId)
header = """Content-type: text/html\n\n
<head>
<title>Test Automation Results</title>
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="-1">
</head>
<body>"""



groupIdFieldSet = """
<form action="altgTestResults.py" enctype="multipart/form-data"
method="post">
<fieldset>
<legend>Currently Loaded Group</legend>
<p>
Group ID
<input type="text" name="groupId" value={groupId}>
</p>
<div>
<input type="submit" value="Load">
</div>""".format(groupId=groupId)

print(header)
print(groupIdFieldSet)
print("<br>")
resultDir = "/results/{}/".format(groupId)
result = subprocess.check_output(["ls", "{}".format(conf.aldbConfDirsGet()['resultDir'])])
result = result.splitlines()
table = """
<table style="width:100%" border = "2" Cellspacing="1" Cellpadding="1">
	<tr>
	<th>Map Bundle Config</th>
	<th>Precedence Config</th>
	<th>Test Results</th>
	</tr>"""
confRegex = "("+")|(".join([sednomd5File, sscfnomd5File, rlcnomd5File, gdrmnomd5File, "\.zip"]) + ")"
precRegex = "("+")|(".join(["\.kml", "coords", "map.*\.pdf", "satlist"]) + ")"
resultsRegex = "("+")|(".join(["results", "\.png", "\.jpg", "\.jpeg", "\.log", "nlg", "dbx", "Syslog"]) + ")"
confFiles = []
precFiles = []
resultsFiles = []
rand = random.randint(1, sys.maxint)
for i in result:
	if re.search(confRegex, i):
		confFiles.append('<a href="{resultDir}{file}?{rand}"> {file} </a>'.format(file=i, resultDir=resultDir, rand = rand) + "<br>")
	elif re.search(precRegex, i):
		precFiles.append('<a href="{resultDir}{file}?{rand}"> {file} </a>'.format(file=i, resultDir=resultDir, rand = rand) + "<br>")
	elif re.search(resultsRegex, i):
		resultsFiles.append('<a href="{resultDir}{file}?{rand}"> {file} </a>'.format(file=i, resultDir=resultDir, rand = rand) + "<br>")
links = """<tr>
<td>{}</td>
<td>{}</td>
<td>{}</td>
</tr>
</table>""".format("".join(confFiles), "".join(precFiles), "".join(resultsFiles))
print(table)
print(links)
print("</fieldset>")
print("<div>")
print("<br>")
print('<a href="/cgi-bin/altgDbExport.py?groupId={groupId}"> Export Status Data </a>'.format(groupId=groupId))
print("<br><br>")
print('<a href="/cgi-bin/altgTestLauncher.py?groupId={groupId}"> Test Launcher </a>'.format(groupId=groupId))
print("</div>")
print("<br>")
print('<a href="/index.html"> Main Screen </a>')
print("</form>")
print("</body>")
print("</html>")
