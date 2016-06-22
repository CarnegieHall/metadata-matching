# !/usr/local/bin/python3.4.2
# ----Copyright (c) 2016 Carnegie Hall | The MIT License (MIT)----
# ----For the full license terms, please visit https://github.com/CarnegieHall/quality-control/blob/master/LICENSE----
# run script with 3 or more arguments:
# argument 0 is the script name
# argument 1 is the path to the metadata CSV
# argument 2 is the path to the simplified mapping between original filename (as uploaded) and filename on disk (with UTF-8!).
# argument 3 is the path to you want to output the matched CSV to (folder to where files are.)
# argument 4 is the Batch ID of the subset of photographs (e.g. GB-001)

import csv
import os
import glob
from os import listdir
from os.path import isfile, join, split
import json
import sys
import io
import unicodedata

#Set filepath variables
filePath_1 = str(sys.argv[1])
filePath_2 = str(sys.argv[2])
filePath_3 = str(sys.argv[3])
batch = str(sys.argv[4])


fileDict = {}
photoDict = {}


#Open metadata CSV and put the data in the dictionary to be held in memory
with open(filePath_1, encoding='latin-1') as f, open(filePath_2, encoding='utf-8') as g:
    photoData = csv.reader(f, dialect='excel', delimiter=',')
    next(photoData, None)  # skip the headers
    fileData = csv.reader(g, dialect='excel', delimiter=',')
    for row in fileData:
        interface_id = row[0]
        filename_disk = row[2]

        fileDict[interface_id] = filename_disk
    # print(json.dumps(fileDict, indent=4))
    for row in photoData:
    	source_name = row[0]
    	title = row[1]
    	description = row[2]
    	copyright_notice = row[3]
    	entities = row[4]
    	keywords = row[5]
    	date = row[6]
    	date_year = row[7]
    	date_freetext = row[8]
    	venue = row[9]
    	confidentiality = row[10]
    	approval_status = row[11]
    	approval_conditions = row[12]
    	content_type = row[13]
    	genre = row[14]
    	asset_id = row[15]
    	original_filename = row[16]
    	new_filename = fileDict[asset_id]

    	photoDict[str(asset_id)] = {}
    	photoDict[str(asset_id)]['Source'] = source_name
    	photoDict[str(asset_id)]['Title'] = title
    	photoDict[str(asset_id)]['Description'] = description
    	photoDict[str(asset_id)]['Copyright Notice'] = copyright_notice
    	photoDict[str(asset_id)]['Participating Artists'] = entities
    	photoDict[str(asset_id)]['Keywords'] = keywords
    	photoDict[str(asset_id)]['Event Date'] = date
    	photoDict[str(asset_id)]['Date (YYYY)'] = date_year
    	photoDict[str(asset_id)]['Date (free text)'] = date_freetext
    	photoDict[str(asset_id)]['Event Location'] = venue
    	photoDict[str(asset_id)]['Confidentiality'] = confidentiality
    	photoDict[str(asset_id)]['Approval Status'] = approval_status
    	photoDict[str(asset_id)]['Approval Conditions'] = approval_conditions
    	photoDict[str(asset_id)]['Material Type'] = content_type
    	photoDict[str(asset_id)]['Genre'] = genre
    	photoDict[str(asset_id)]['Asset ID'] = ''.join(['GETTY', asset_id])
    	photoDict[str(asset_id)]['Legacy Filename'] = original_filename 
    	photoDict[str(asset_id)]['Upload Filename'] = new_filename

# Need workflow for batches of files
outputPath = ''.join([str(filePath_3), '/Central_Getty_', batch, '.csv'])

fields = ['Source', 'Title', 'Description', 'Copyright Notice', 'Participating Artists', 'Keywords', 'Event Date', 'Date (YYYY)', 'Date (free text)', 'Event Location', 'Confidentiality', 'Approval Status', 'Approval Conditions', 'Material Type', 'Genre', 'Asset ID', 'Legacy Filename', 'Upload Filename']
with open(outputPath, 'w', newline='') as csvfile:
	w = csv.DictWriter(csvfile, fields)
	w.writeheader()
	for k in photoDict:
		w.writerow({field: photoDict[k].get(field) for field in fields})
# print(json.dumps(photoDict, indent=4))
