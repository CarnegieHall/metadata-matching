# !/usr/local/bin/python3.4.2
# ----Copyright (c) 2016 Carnegie Hall | The MIT License (MIT)----
# ----For the full license terms, please visit https://github.com/CarnegieHall/quality-control/blob/master/LICENSE----
# run script with 5 arguments:
# argument 0 is the script name
# argument 1 is the path to the Isilon HDD volume containing the assets
# argument 2 is the path to the metadata spreadsheet [~/Carnegie_Hall_wcs.csv]
# argument 3 is the path ~/OPAS_ID_exports/OPAS_wcs_IDs_titles.csv
# argument 4 is the path to the folder you want to save your unmatched performance IDs to
# argument 5 is the harddrive ID/volume that will be added to the output filename (E.g. ABH_20150901)

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
filePath_4 = str(sys.argv[4])

fileDict = {}
wcDict = {}
titleDict = {}
##matchedList = []
unmatchedIDs = []

#Set a variable to equal the harddrive volume number, which is extracted from the file path
volume = sys.argv[len(sys.argv)-1]

#Extract filenames from the full file path and build dictionary

for full_filePath in glob.glob(os.path.join(filePath_1, '*.tif')):
    file_name = os.path.basename(full_filePath)
    file_wcID = os.path.basename(full_filePath).split('_')[0]

    fileDict[str(file_name)] = {}
    fileDict[str(file_name)]['File Name'] = file_name
    fileDict[str(file_name)]['Source Unique ID'] = file_wcID

with open(filePath_2, 'rU') as f:
    with open(filePath_3, encoding='utf-8') as g:
        wcData = csv.reader(f, dialect='excel', delimiter=',')
        next(wcData, None)  # skip the headers
        titleData = csv.reader(g, dialect='excel', delimiter=',')
        for row in titleData:
            event_id = row[0]
            titleMatch_id = ''.join(['CONC', event_id])
            text = row[1]
            if not text:
                text = '[No title available]'

            titleDict[titleMatch_id] = text

        for row in wcData:
            opas_id = row[0]
            source_unique_id = row[1].strip()
            collection = row[2]
            if 'Window Cards' in collection:
# need to match any of these:
                # Main Hall Window Cards
                # Recital Hall Window Cards
                # Zankel Hall Window Cards
                cortexFolder = 'CH_WindowCards_01'
            event = row[3]
            entities = row[4]
            event_date = row[5]
            event_year = row[6]
            note = row[8]

            try:
                if opas_id != '':
                    opas_id = ''.join(['CONC', opas_id])
                    if event_year:
                        title = ''.join([titleDict[opas_id], ', ', event_year])
                else:
                    opas_id = ''.join([cortexFolder])
                    title = event

                wcDict[str(source_unique_id)] = {}
                wcDict[str(source_unique_id)]['OPAS ID'] = opas_id
                wcDict[str(source_unique_id)]['Collection'] = collection
                wcDict[str(source_unique_id)]['Date 1 (YYYY/mm/dd)'] = event_date
                wcDict[str(source_unique_id)]['Note'] = note
                wcDict[str(source_unique_id)]['Title'] = title

            #If OPAS ID from metadata spreadsheet is NOT in OPAS ID export, it will cause a KeyError
            #This exception catches those errors, and adds the IDs to a list of unmatched IDs
            #Since we added "CONC" to the OPAS ID above, we remove it here (opas_id[4:]) to allow for easier OPAS QC
            except KeyError:
                if opas_id not in unmatchedIDs:
                    unmatchedIDs.append(opas_id[4:])

##print (json.dumps(wcDict, indent=4))

for key in fileDict:
    file_wcID = fileDict[key]['Source Unique ID']

    if file_wcID in wcDict.keys():

        fileDict[key]['OPAS ID'] = wcDict[file_wcID]['OPAS ID']
        fileDict[key]['Collection'] = wcDict[file_wcID]['Collection']
        fileDict[key]['Date 1 (YYYY/mm/dd)'] = wcDict[file_wcID]['Date 1 (YYYY/mm/dd)']
        fileDict[key]['Note'] = wcDict[file_wcID]['Note']
        fileDict[key]['Title'] = wcDict[file_wcID]['Title']

matchedFiles_name = ''.join([str(filePath_1), '/Central_OPASmatchedFiles_WindowCards_', volume, '.csv'])
unmatchedIDs_name = ''.join([str(filePath_4), '/unmatched_WindowCards_IDs_', volume, '.txt'])

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