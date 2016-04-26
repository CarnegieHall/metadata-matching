# !/usr/local/bin/python3.4.2
# ----Copyright (c) 2016 Carnegie Hall | The MIT License (MIT)----
# ----For the full license terms, please visit https://github.com/CarnegieHall/quality-control/blob/master/LICENSE---- 
# This code parses a list of files for program scans as created by NEDCC
    # Output is a dictionary with filename as Key, and values for Date, Venue Code, and Qualifier
    # The Qualifier is "b" or "c" (or "d'), used by NEDCC to distinguish 2nd and 3rd (4th) events on the same day
# Next it parses an OPAS export in .csv form, with the following fields: 1) OPAS ID, 2) Date, 3) Time ("start" in OPAS)
    # Output is a dictionary with date-time strings for each event as keys, OPAS IDs as values
# Finally it reconciles multiple OPAS ID-to-filename matches by sorting the corresponding list of events in date/time order
    # Outputs are 1) an updated fileDict with correctly matched filenames; 2) .csv file with matched filenames;
    # 3) "troubleShoot" .csv 4).csv file with unmatched filenames, to catch mistakes in either filename or OPAS data;
	# 5) .txt file with unmatched OPAS IDs (should only be events with no program)

# run script with 4 arguments:
# argument 0 is the script name
# argument 1 is the path to the Isilon HDD volume containing the assets
# argument 2 is the path ~/Filename_OPAS_Matching/OPAS_ID_Exports/OPAS_eventIDs_1891_1960.csv
# argument 3 is the harddrive ID/volume that will be added to the output filename (E.g. 12-306)

import csv
import json
from datetime import datetime, date, timedelta
import os
import re
from os import listdir
from os.path import isfile, join, split
import sys

filePath_1 = str(sys.argv[1])
filePath_2 = str(sys.argv[2])

fileDict = {}
opasIdDict = {}
matchedDict = {}
unmatchedList = []
OPAS_checkList = []

# Set a variable to equal the hard drive volume number, which is extracted from the file path
volume = sys.argv[len(sys.argv)-1]

# Extract filenames from the full file path
onlyfiles = [f for f in listdir(str(filePath_1)) if isfile(join(str(filePath_1),f))]

for i in range(len(onlyfiles)):
    filename = onlyfiles[i]

    # This dict allows us to assign a numerical position to each file qualifier
    # We'll use this later to access an OPAS ID from a chronologically sorted list of OPAS events
    positionDict = {'none': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}

    # Test each file to make sure it's a TIF; pass over the 'Thumbs.db' file stored with each volume
    if filename.endswith(".tif"):
        try:
            parts = filename.split('_')
            fileType = parts[len(parts)-1].split('.')[1]
            venueCode = parts[1]
            year = parts[2][0:4]
            month = parts[2][4:6]
            day = parts[2][6:8]
            qualifier = parts[3]
            
            # Separate out/format the date into year-month-day
            date = '{year}-{month}-{day}'.format(**locals())

            # Check to see if filename ends in numeric character, i.e. there is no qualifier
            #(No qualifier = only one event in that venue on that date)
            pattern = re.compile(r'\d')
            if pattern.findall(qualifier):
                qualifier = 'none'
            position = positionDict[qualifier]

            fileDict[str(filename)] = {}
            fileDict[str(filename)]['qualifier'] = qualifier
            fileDict[str(filename)]['position'] = position
            fileDict[str(filename)]['date'] = date
            fileDict[str(filename)]['venue code'] = venueCode
        except (ValueError,IndexError):
            pass

with open(filePath_2, 'rU') as f:
    opasData = csv.reader(f, dialect='excel', delimiter=',', quotechar='"')
    for row in opasData:
        event_id = row[0]
        date = row[1]
        #calculate the day before, in case event was a midnight concert
        yest = (datetime.strptime(date, '%m/%d/%Y').date()) - timedelta(days=1)
        isoDate = datetime.strptime(date, '%m/%d/%Y').date().isoformat()
        timeString = row[2]
        
        #Group date and time into single string
        date_string = isoDate + ' ' + timeString
        
        # Re-format the date into year-month-day to match filenames
        # Puts time string into 24-hour format for proper sorting
        isoDateTime = datetime.strptime(date_string, '%Y-%m-%d %I:%M %p')
        if timeString == "12:00 AM":
            isoDateTime = isoDateTime - timedelta(seconds=1)
            #put date into correct ISO 8601 format
            isoDate = yest.isoformat()

        # Put datetime into correct ISO 8601 format
        isoDateTime = isoDateTime.isoformat()

        venue = row[3]

        opasIdDict[str(event_id)] = {}
        opasIdDict[str(event_id)]['date'] = isoDate
        opasIdDict[str(event_id)]['isoDateTime'] = isoDateTime
        opasIdDict[str(event_id)]['venue'] = venue

for filename in fileDict:
    venueCode = fileDict[filename]['venue code']
    position = int(fileDict[filename]['position'])
    
    # Create a blank dict to hold all possible matching events for each filename
    # Dict has datetime as key, opas ID as value
    matchesDict = {}
    fileDate = fileDict[filename]['date']
            
    for key in opasIdDict:
        matchDict = {}
        date = opasIdDict[key]['date']
        isoDateTime = opasIdDict[key]['isoDateTime']

        venue = opasIdDict[key]['venue'].lower()
        if venue == 'crh':
            venue = 'cr'
        elif venue == 'rh':
            venue = 'cl'
        
        if venueCode == venue:
            if fileDate == date:
                matchDict[str(isoDateTime)] = key

        matchesDict.update(matchDict)

    # Sort the date-time strings in chrono order
    # This returns a list of date-time strings, which are the keys of matchesDict
    matchedEvents = sorted(matchesDict)
    
    # This loop matches filename to correct OPAS ID from list of possibilities created above
	# If clause finds files that didn't match to any OPAS event
    # Else clause finds the correct match, using the position indicator from above
    # Since matchedEvents is just a list of keys (but in correct chrono order), we need to use position
    # to pick the correct key, from which we'll grab the matching OPAS ID
	# The try:/except: statement catches disconnects between OPAS and filenames, e.g. incorrect filenames or
	# mistakes in OPAS data (e.g. a duplicate event record [2 records, with different IDs, for same event/date/time/venue])
	# OPAS_checkList outputs to a "troubleShoot" file that can be used to trouble shoot these issues
    if len(matchedEvents) == 0:
        unmatchedList.append(filename)
    else:
        try:
            match = matchesDict[(matchedEvents[position])]
        except (ValueError,IndexError):
            OPAS_checkList.append(filename)
            
    
    fileDict[filename]['opas matches'] = matchesDict
    fileDict[filename]['match'] = match

    matchedDict[filename] = str("CONC" + match)

## Final step checks for unmatched OPAS IDs
## Helps identify problems caused by OPAS records with no physical program
matchList = []
matchesList = []
unmatchedIDs = []

for filename in fileDict:
    try:
        match = fileDict[filename]['match']
        if match not in matchList:
            matchList.append(match)
    except KeyError:
        pass

    matches = fileDict[filename]['opas matches']

    for item in matches.values():
        if item not in matchesList:
            matchesList.append(item)

for item in matchesList:
    if item not in matchList:
        unmatchedIDs.append(item)

matchedFiles_name = ''.join([str(filePath_1), '/Central_OPASmatchedFiles_', volume, '.csv'])
unmatchedFiles_name = ''.join(['../OPAS_Matching_ErrorOutput/unmatchedFiles_', volume, '.csv'])
unmatchedIDs_name = ''.join(['../OPAS_Matching_ErrorOutput/unmatchedIDs_', volume, '.txt'])
fileDict_name = ''.join(['JSON_dicts/fileDict_', volume, '.json'])
OPAS_checkList_name = ''.join(['../OPAS_Matching_ErrorOutput/troubleShoot_', volume, '.csv'])

with open(matchedFiles_name, 'w', newline='')as f:
    a = csv.writer(f, dialect='excel', delimiter=',')
    a.writerow(["Program File Name", "OPAS ID for Cortex"])
    for key, value in matchedDict.items():
        a.writerow([key, value])

with open(unmatchedFiles_name,'w', newline='') as g:
    b = csv.writer(g, dialect='excel', delimiter=',')
    for item in unmatchedList:
        b.writerow([item])

with open(OPAS_checkList_name,'w', newline='') as cl:
    c = csv.writer(cl, dialect='excel', delimiter=',')
    for item in OPAS_checkList:
        c.writerow([item])                                                                                        

with open(unmatchedIDs_name, 'w') as h:
    h.write(', '.join(str(opasID) for opasID in unmatchedIDs))

##print (json.dumps(fileDict, indent=4))
with open(fileDict_name, 'w') as newfile:
    json.dump(fileDict, newfile)

print("Done with volume ", volume)
