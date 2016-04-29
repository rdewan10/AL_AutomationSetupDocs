#!/usr/bin/env python

from altgScreen import utilScreen

util = utilScreen()
util.printScreen()

testname = util.form.getvalue('Option')

if testname == 'Report':
    test = util.mapResult()
elif testname == 'Maint':
    test = util.testMaint()
elif testname == 'Wdog':
    test = util.testMaintWdog()
else:
    test = 'Select utility.'

print("<br><br>")
print(test)

