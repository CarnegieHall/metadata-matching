# !/usr/local/bin/python3.4.2
# ----Copyright (c) 2016 Carnegie Hall | The MIT License (MIT)----
# ----For the full license terms, please visit https://github.com/CarnegieHall/quality-control/blob/master/LICENSE---- 
# run script with 3 or more arguments:
# argument 0 is the script name
# argument 1 is the path to the Robert Shaw Metadata Spreadsheet (CSV)
# arguments 2+ are the paths to the directories you want to create Central CSVs for 

import csv
import os
import glob
from os import listdir
from os.path import isfile, join, split
import json
import sys
import io

#Set filepath variables
filePath_1 = str(sys.argv[1])
filePath_2 = str(sys.argv[2])


videoDict = {}


#Open RS metadata CSV and put the data in the dictionary to be held in memory
with open(filePath_1, 'rU') as f:
    videoData = csv.reader(f, dialect='excel', delimiter=',')
    for row in videoData:
    	source_id = row[0]
    	original_format = row[1]
    	date = row[2]
    	date_freetext = row[3]
    	opas_id = row[4]
    	series = row[5]
    	venue = row[6]
    	description = row[7]
    	archives_collection = row[8]
    	notes_containerinfo = row[9]
    	generation = row[10]
    	recording_standard = row[11]
    	stereo_mono = row[12]
    	preservation_filename = row[13]
    	preservation_cksum = row[14]


    	videoDict[str(preservation_filename)] = {}
    	videoDict[str(preservation_filename)]['Source ID'] = source_id
    	videoDict[str(preservation_filename)]['Original Format'] = original_format
    	videoDict[str(preservation_filename)]['Date'] = date
    	videoDict[str(preservation_filename)]['Date (FreeText)'] = date_freetext
    	videoDict[str(preservation_filename)]['OPAS EVENT ID'] = opas_id
    	videoDict[str(preservation_filename)]['Series'] = series
    	videoDict[str(preservation_filename)]['Venue'] = venue
    	videoDict[str(preservation_filename)]['Description'] = description
    	videoDict[str(preservation_filename)]['Carnegie Hall Archives Collection'] = archives_collection
    	videoDict[str(preservation_filename)]['Notes/Container Annotation'] = notes_containerinfo
    	videoDict[str(preservation_filename)]['Generation'] = generation
    	videoDict[str(preservation_filename)]['Recording Standard'] = recording_standard
    	videoDict[str(preservation_filename)]['Stereo/Mono'] = stereo_mono
    	videoDict[str(preservation_filename)]['Preservation Master Filename'] = preservation_filename
    	videoDict[str(preservation_filename)]['pres master checksum value'] = preservation_cksum
   
# print(json.dumps(videoDict, indent=4))

# sys.argv is a list of all the filepaths we provided as arguments. "For everything this list starting at position 2, do xyz"
for hddFilePath in sys.argv[2:]:
	#Clear centralDict for each directory
	centralDict = {}
	#Set variable for volume # per directory
	volume = os.path.split(hddFilePath)[1]
	# directory = os.path.split(hddFilePath)[0]
	# Extract filenames from the full file path of each file
	onlyfiles = [f for f in listdir(str(hddFilePath)) if isfile(join(str(hddFilePath),f))]
	
	for i in range(len(onlyfiles)):
		filename = onlyfiles[i]
		# print(filename)
		# Test each file to make sure it's a preservation master; pass over the 'Thumbs.db' file stored with each volume
		if filename.endswith("_pm.mov"):
			# make videoDict into centralDict
			centralDict[str(filename)] = {}
			centralDict[str(filename)] = videoDict[str(filename)]
			
		# This writes the nested dictionary to a CSV file
			csv_path = "".join([hddFilePath, '/', 'Central_RobertShaw_', volume, '.csv'])

			fields = ['Source ID', 'Original Format', 'Date', 'Date (FreeText)', 'OPAS EVENT ID', 'Series', 'Venue', 'Description', 'Carnegie Hall Archives Collection', 'Notes/Container Annotation', 'Generation', 'Recording Standard', 'Stereo/Mono', 'Preservation Master Filename', 'pres master checksum value']
			with open(csv_path, 'w', newline='') as csvfile:
				w = csv.DictWriter(csvfile, fields)
				w.writeheader()
				for k in centralDict:
					w.writerow({field: centralDict[k].get(field) for field in fields})

	print("Central CSVs created for ", volume)