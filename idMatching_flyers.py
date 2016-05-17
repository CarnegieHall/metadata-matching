# !/usr/local/bin/python3.4.2
# ----Copyright (c) 2016 Carnegie Hall | The MIT License (MIT)----
# ----For the full license terms, please visit https://github.com/CarnegieHall/quality-control/blob/master/LICENSE---- 
# run script with 5 arguments:
# argument 0 is the script name
# argument 1 is the path to the Isilon HDD volume containing the assets
# argument 2 is the path to the metadata spreadsheet [~/Carnegie_Hall_Flyers.csv]
# argument 3 is the path ~/OPAS_ID_exports/OPAS_flyers_IDs_titles.csv
# argument 4 is the harddrive ID/volume that will be added to the output filename (E.g. ABH_20150901)

import csv
import glob
import itertools
import json
import os
from os.path import isfile, join, split
import sys

filePath_1 = str(sys.argv[1])
filePath_2 = str(sys.argv[2])
filePath_3 = str(sys.argv[3])

fileDict = {}
flyerDict = {}
titleDict = {}
##matchedList = []
unmatchedIDs = []

#Set a variable to equal the harddrive volume number, which is extracted from the file path
volume = sys.argv[len(sys.argv)-1]

#Extract filenames from the full file path and build dictionary

for full_filePath in glob.glob(os.path.join(filePath_1, '*.tif')):
    file_name = os.path.basename(full_filePath)
    file_flyerID = os.path.basename(full_filePath).split('_')[0]

    fileDict[str(file_name)] = {}
    fileDict[str(file_name)]['File Name'] = file_name
    fileDict[str(file_name)]['Source Unique ID'] = file_flyerID

with open(filePath_2, 'rU') as f:
    with open(filePath_3, encoding='utf-8') as g:
        flyerData = csv.reader(f, dialect='excel', delimiter=',')
        titleData = csv.reader(g, dialect='excel', delimiter=',')
        for row in titleData:
            event_id = row[0]
            titleMatch_id = ''.join(['CONC', event_id])
            text = row[1]
            if not text:
                text = '[No title available]'

            titleDict[titleMatch_id] = text
            
        for row in flyerData:
            opas_id = row[0]
            source_unique_id = row[1]
            collection = row[2]
            if collection == 'Main Hall Flyers':
                cortexFolder = 'CH_FLYERS_01'
            event = row[3]
            entities = row[4]
            event_date = row[5]
            event_year = row[5].split('/')[0]
            note = row[7]

            try:
                if opas_id != '':
                    opas_id = ''.join(['CONC', opas_id])
                    if event_year:
                        title = ''.join([titleDict[opas_id], ', ', event_year])
                else:
                    opas_id = ''.join([cortexFolder])
                    title = event

                flyerDict[str(source_unique_id)] = {}
                flyerDict[str(source_unique_id)]['OPAS ID'] = opas_id
                flyerDict[str(source_unique_id)]['Collection'] = collection
                flyerDict[str(source_unique_id)]['Date 1 (YYYY/mm/dd)'] = event_date
                flyerDict[str(source_unique_id)]['Note'] = note
                flyerDict[str(source_unique_id)]['Title'] = title

            #If OPAS ID from metadata spreadsheet is NOT in OPAS ID export, it will cause a KeyError
            #This exception catches those errors, and adds the IDs to a list of unmatched IDs
            #Since we added "CONC" to the OPAS ID above, we remove it here (opas_id[4:]) to allow for easier OPAS QC
            except KeyError:
                if opas_id not in unmatchedIDs:
                    unmatchedIDs.append(opas_id[4:])

##print (json.dumps(flyerDict, indent=4))

for key in fileDict:
    file_flyerID = fileDict[key]['Source Unique ID']

    if file_flyerID in flyerDict.keys():

        fileDict[key]['OPAS ID'] = flyerDict[file_flyerID]['OPAS ID']
        fileDict[key]['Collection'] = flyerDict[file_flyerID]['Collection']
        fileDict[key]['Date 1 (YYYY/mm/dd)'] = flyerDict[file_flyerID]['Date 1 (YYYY/mm/dd)']
        fileDict[key]['Note'] = flyerDict[file_flyerID]['Note']
        fileDict[key]['Title'] = flyerDict[file_flyerID]['Title']

matchedFiles_name = ''.join([str(filePath_1), '/Central_OPASmatchedFiles_flyers_', volume, '.csv'])
unmatchedIDs_name = ''.join(['../OPAS_Matching_ErrorOutput/unmatched_flyer_IDs_', volume, '.txt'])

# This writes the nested dictionary to a CSV file
fields = ['OPAS ID', 'Source Unique ID', 'Collection', 'Title', 'Date 1 (YYYY/mm/dd)', 'Note', 'File Name']
with open(matchedFiles_name, 'w', newline='') as csvfile:
    w = csv.DictWriter(csvfile, fields)
    w.writeheader()
    for k in fileDict:
        w.writerow({field: fileDict[k].get(field) for field in fields})

#This saves the unmatched OPAS IDs as a text file, so you can check the issues in OPAS
with open(unmatchedIDs_name, 'w') as h:
    h.write(','.join(str(opas_id) for opas_id in unmatchedIDs))
