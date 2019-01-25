# !/usr/local/bin/python3.4.3
# ----Copyright (c) 2019 Carnegie Hall | The MIT License (MIT)----
# run script with 3 arguments:
# argument 0 is the script name
# argument 1 is the filepath to the exported source CSV
# argument 2 is directory you want to save output CSV to

import calendar
import csv
import os
from os.path import join
import sys

filePath1 = str(sys.argv[1])
filePath2 = str(sys.argv[2])

fileDict = {}

with open(filePath1, 'rU') as f:
    cortexData = csv.reader(f, dialect='excel', delimiter=',', quotechar='"')
    next(cortexData, None)  # skip the headers
    for row in cortexData:
    	cortexID = row[0]
    	filename = row[1]
    	parts = filename.split('_')
    	year = row[2]
    	day = row[3]
    	month = row[4]
    	monthString = calendar.month_name[int(month)]
    	folderTitle = row[5]
    	pageNumber = parts[len(parts)-1].split('.')[0].lstrip('0')

    	newTitle = '{folderTitle}, {monthString} {day}, {year}, program page {pageNumber}'.format(**locals())
    	# Separate out/format the date into year-month-day. If we want to change to slashes, just change the - to /
    	date = '{year}-{month}-{day}'.format(**locals())

    	fileDict[str(cortexID)] = {}
    	fileDict[str(cortexID)]['Cortex ID'] = cortexID
    	fileDict[str(cortexID)]['New Title'] = newTitle
    	fileDict[str(cortexID)]['Date'] = date

outputPath = ''.join([str(filePath2), 'newProgramPageTitles.csv'])

fields = ['Cortex ID', 'New Title', 'Date']
with open(outputPath, 'w', newline='')as csvfile:
    w = csv.DictWriter(csvfile, fields)
    w.writeheader()
    for k in fileDict:
        w.writerow({field: fileDict[k].get(field) for field in fields})

print('Done!')
