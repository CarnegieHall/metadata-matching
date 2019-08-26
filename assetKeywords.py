# !/usr/local/bin/python3.4.3
# ----Copyright (c) 2019 Carnegie Hall | The MIT License (MIT)----
# run script with 4 arguments:
# argument 0 is the script name
# argument 1 is the filepath to the csv of asset IDs with folder IDs
# argument 2 is the filepath to the csv of event IDs and event keyword strings
# argument 3 is the filepath to the csv of work performance folder IDs and keyword strings
# argument 4 is destination directory for output CSV of asset IDs + all keywords

import csv
import os
from os.path import join
import sys

filePath1 = str(sys.argv[1])
filePath2 = str(sys.argv[2])
filePath3 = str(sys.argv[3])
filePath4 = str(sys.argv[4])

assetDict = {}
dupeDict = {}

with open(filePath1, newline = '', encoding='utf-8') as f:
	assetData = csv.reader(f, dialect='excel', delimiter=',', quotechar='"')
	next(assetData, None) #skip headers
	idChecklist = []
	for row in assetData:
                assetID = row[0]
                eventFolderID = row[1]

                assetDict[str(eventFolderID)] = {}
                assetDict[str(eventFolderID)]['Asset ID'] = assetID
                assetDict[str(eventFolderID)]['Keywords'] = ''

                if eventFolderID not in idChecklist:
                        idChecklist.append(eventFolderID)
                else:
                        print(eventFolderID, '\t', assetID)

with open(filePath2, newline = '', encoding='utf-8') as h:
	eventData = csv.reader(h, dialect='excel', delimiter=',', quotechar='"')
	next(eventData, None)
	for row in eventData:
		eventFolderID = row[0]
		eventPerformers = row[1]
		eventPresenters = row[2]

		if eventPerformers:
			keywordString = f'{eventPerformers}{eventPresenters}'
		else:
			keywordString = f'{eventPresenters}'

		try:
			assetDict[str(eventFolderID)]['Keywords'] = keywordString
		except KeyError:
			pass

with open(filePath3, newline = '', encoding='utf-8') as j:
        workPerfData = csv.reader(j, dialect='excel', delimiter=',', quotechar='"')
        next(workPerfData, None)
        idChecklist = []
        keywordList = []
        workPerfDict = {}

        for row in workPerfData:
                workPerfFolderID = row[0]
                eventFolderID = row[1]
                workPerfEntities = row[2]

                if workPerfEntities:
                        workPerfKeywords = workPerfEntities.split('|')

                        if eventFolderID not in idChecklist:
                                idChecklist.append(eventFolderID)
                                keywordList = []

                                for keyword in workPerfKeywords:
                                        if keyword:
                                                keywordList.append(keyword)

                                workPerfDict[str(eventFolderID)] = keywordList
                        else:
                                keywordList = workPerfDict[str(eventFolderID)]

                                for keyword in workPerfKeywords:
                                        if keyword:
                                                if keyword not in keywordList:
                                                        keywordList.append(keyword)
                                                        workPerfDict[str(eventFolderID)] = keywordList

        for key in workPerfDict:
                keywords = workPerfDict[key]
                s = '|'
                keywordString = s.join(keywords)
                workPerfDict[key] = keywordString

        for key in assetDict:
                assetKeywords = assetDict[key]['Keywords']

                try:
                        workPerfKeywords = workPerfDict[key]
                        keywordString = f'{assetKeywords}{workPerfKeywords}'
                        assetDict[key]['Keywords'] = keywordString
                except KeyError:
                        pass

outputPath = ''.join([str(filePath4), '/assetKeywords.csv'])

fields = ['Asset ID', 'Keywords']
with open(outputPath, 'w', newline='') as csvfile:
        w = csv.DictWriter(csvfile, fields)
        w.writeheader()
        for k in assetDict:
                w.writerow({field: assetDict[k].get(field) for field in fields})

print('Done assembling asset keywords')
