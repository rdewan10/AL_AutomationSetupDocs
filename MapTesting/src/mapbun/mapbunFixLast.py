#!/usr/bin/env python

# -*- coding: utf-8 _*_
import sys

##################################################################
# function to remove checksum string at the end on the last line
# in the .csv file
#
# Calling args:  string   - last line of the .cvs file
#                numparam - number of comma seperated values
#                min      - minimum value
#                max      - maximum value
# Example: 
# myresult=`./getBuf.py "9,17,ABS-7(6/RJ/A/N)_OLD,N,N,60,99997MB94  7 1 10000 `
##################################################################
# get the command line arguments: string, num of params, min, max
buf=str(sys.argv[1])
numparam=int(sys.argv[2])
min=sys.argv[3]
max=sys.argv[4]
items = buf.split(",")
i=0
offset=0

#get to the last item and extract the numeric value
lastItem = items[numparam-1]
while i < len(lastItem):
      ch = lastItem[offset]
      if (ch < '0' or ch > '9'):
         break 
      offset += 1 
      i += 1
lastItem = lastItem[:i]

# determine the min/max values
while i > int(min):
      x = int(lastItem[:i])
      if x <= int(max):
         break;
      i = i -1
   
lastItem = lastItem[:i]
j=0

# Construct the last line with corrected values
returnItem=""
while j < numparam-1:
      returnItem = returnItem + items[j] + ","
      j += 1 
returnItem = returnItem + lastItem
print '\"'+returnItem+'\"'

