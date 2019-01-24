# !/usr/local/bin/python3.4.3
# ----Copyright (c) 2019 Carnegie Hall | The MIT License (MIT)----
# run script with 3 arguments:
# argument 0 is the script name
# argument 1 is the filepath to the exported source CSV
# argument 2 is directory you want to save output CSV to

import calendar
import csv
# from datetime import datetime, date, timedelta
import os
from os.path import join
import sys

filePath1 = str(sys.argv[1])
filePath2 = str(sys.argv[2])

fileDict = {}

with open(filePath1, 'rU') as f:
    cortexData = csv.reader(f, dialect='excel', delimiter=',', quotechar='"')
    for row in cortexData:
    	cortexID = row[0]
    	filename = row[1]
    	parts = filename.split('_')
    	year = row[8]
    	day = row[9]
    	month = row[10]
    	monthString = calendar.month_name[int(month)]
    	folderTitle = row[12]
    	pageNumber = parts[len(parts)-1].split('.')[0].lstrip('0')

    	newTitle = '{folderTitle}, {monthString} {day}, {year}, program page {pageNumber}'.format(**locals())
    	# Separate out/format the date into year-month-day. If we want to change to slashes, just change the - to /
    	date = '{year}-{month}-{day}'.format(**locals())

        fileDict[str(cortexID)] = {}
        fileDict[str(cortexID)]['newTitle'] = newTitle
        fileDict[str(cortexID)]['date'] = date


matchedFiles_name = ''.join([str(filePath2), 'newProgramPageTitles.csv'])

with open(matchedFiles_name, 'w', newline='')as f:
    a = csv.writer(f, dialect='excel', delimiter=',')
    a.writerow(["Cortex ID", "New Title", "Date"])
    for key, value in fileDict.items():
        a.writerow([key, value])

print("Done!")