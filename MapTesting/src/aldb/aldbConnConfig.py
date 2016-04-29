##########################################################################
### aldbConnConfig.py
###   This file contains the MYSQL database credentials used by ALDB pkg.
###
###   Since ALDB is dependent on the REDA layer, which also needs these 
###   credentials, the ALDB variables are set to the REDA values, so that
###   the values are only set in one place.  
###   To modify, change in readConfig.py.
###
###########################################################################

from redaConfig import *

dbname=dbName
dbhostname=dbIp
dbportnum=dbPort
dbuser=dbLogin
dbpassw=dbPass

