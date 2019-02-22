# !/usr/local/bin/python3.4.3
# ----Copyright (c) 2019 Carnegie Hall | The MIT License (MIT)----
# run script with 4 arguments:
# argument 0 is the script name
# argument 1 is the filepath to the csv of all event IDs with seasons
# argument 2 is the filepath to the csv of asset IDs with their parent event IDs
# argument 3 is directory you want to save output CSV to that contains the asset ID and associated event seasons

import csv
import os
from os.path import join
import sys

filePath1 = str(sys.argv[1])
filePath2 = str(sys.argv[2])
filePath3 = str(sys.argv[3])

seasonDict = {}
assetDict = {}
c = 0

with open(filePath1, 'rU') as f:
	eventData = csv.reader(f, dialect='excel', delimiter=',', quotechar='"')
	next(eventData, None) #skip headers
	for row in eventData:
		folderID = row[0]
		season = row[1].rstrip('|')

		seasonDict[folderID] = season


with open(filePath2, 'rU') as h:
	programpageData = csv.reader(h, dialect='excel', delimiter=',', quotechar='"')
	next(programpageData, None)
	for row in programpageData:
		assetID = row[0]
		folderID = row[1]

		try:
			season = seasonDict[folderID]
		except KeyError:
			season = ''

		if season == '':
			c += 1

		assetDict[str(assetID)] = season


outputPath = ''.join([str(filePath3), '/assignSeasonToAsset.csv'])


with open(outputPath, 'w', newline='') as csvfile:
	for key in assetDict.keys():
		csvfile.write("%s,%s\n"%(key,assetDict[key]))


print("There are {} null values in Season".format(c))
