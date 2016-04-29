#!/usr/bin/env python

from viasatMysql import vMysql
from aldbConf import aldbConnParmsGet
from altgScreen import changeGroup

data = changeGroup()
form = data['form']
if form.getvalue('groupList'):
	groupList = eval(form.getvalue('groupList'))



print("Content-type: text/html\n\n")
print("<form>")
table = """<table style="width:100%" border = "3" Cellspaceing="1" Cellpadding="1">
	<tr>
	<th>GroupID</th>
	<th>GroupName</th>
	<th>Description</th>
	<th>Station</th>
	</tr>"""

mysql = vMysql(**aldbConnParmsGet())
result = mysql.getTable('GroupInfo', ['GrpID', 'TestCase', 'Description', 'Station'], extraConstraint="ORDER BY GrpID")
if form.getvalue('groupList'):
	result = filter(lambda x: x['GrpID'] in groupList, result)

for row in result:
	table += """
	<tr>
	<td>
	<a href="/cgi-bin/altgTestResults.py?groupId={GrpID}">{GrpID}</a></td>
	<td>{TestCase}</td>
	<td>{Description}</td>
	<td>{Station}</td>
	</tr>""".format(GrpID=row['GrpID'],TestCase=row['TestCase'], Description=row['Description'], Station=row['Station'])
table += "\n</table>"
print(table)
print("""<br>
<a href="/cgi-bin/altgTestLauncher.py"> Test Launcher </a>""")
print("</form>")
print("""<a href="/index.html"> Main Screen </a>""")
