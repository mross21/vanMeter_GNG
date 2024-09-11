"""
@author: Mindy Ross
python version 3.7.4
"""
## GET GNG INFO FROM SYNAPSE ZIP FILES
## INPUT: HEALTHCODE IDS in csv
## Output: one file with all users' GNG data (including accelerometer)
## MAKE SURE TO ADD YOUR USERNAME AND PASSWORD FOR SYNAPSE

## import libraries (Might need to install synapse client)
import synapseclient, json
import pandas as pd
import zipfile

# first add in your username & password
username_synapse = 'insert synapse username here' 
password_synapse = 'insert synapse password here'

# Then read in your data:
# csv file with data (read all IDs) and provide 1 output per Table syn code: 
pathIds = 'insert file path here' #file path to folder containing healthCodes (eg: /Users/mindy/Desktop/BiAffect/Users)
outPath = 'insert folder file path here' #file path to where go/no-go files should go (eg: /Users/mindy/Desktop/BiAffect/Output)

# Upload healthcodes csv file
userFile = pd.read_csv(pathIds + 'insert healthCodes csv filename here', index_col = False)
HealthIDList = userFile['healthCode'].to_list()
 
data = []

for idx in range(0,len(HealthIDList)): 
    syn = synapseclient.login(email=username_synapse, password=password_synapse, rememberMe=True)
    testSubj = HealthIDList[idx]; 
    print(testSubj)
    userDict = dict(zip(userFile.healthCode, userFile.userID))
    userID = userDict[testSubj]
    print(userID)
    
    ## Get GNG Info: 
    sessionTable = "syn12528097"; #GNG
    query_string = 'select * from {} where healthCode = {}'.format(sessionTable, str("'") + testSubj + str("'"))
    results = syn.tableQuery(query_string)
    GNGFilesZip = syn.downloadTableColumns(results,['rawData'])

    for file_id, path in GNGFilesZip.items():
        unzipped = zipfile.ZipFile(path)
        sessionInfo = json.loads(unzipped.open('info.json').read())
        try:
            session = json.loads(unzipped.open('gonogo.json').read())
        except (FileExistsError, zipfile.BadZipFile):
            print('FileExistsError or BadZipFile')
            session = json.loads(unzipped.open('gonogo.json').read())
            print('fixed file error')
        except json.decoder.JSONDecodeError:
            print('error accessing json file')
            broken_jsonFile = unzipped.open('gonogo.json').read()
            fixed_jsonFile = broken_jsonFile.replace(b'/', b'')
            session = json.loads(fixed_jsonFile)
            print('fixed json file')
        except UnicodeDecodeError:
            print('UnicodeDecodeError-session data not downloaded')
            continue
    
        dfSessionInfo = pd.DataFrame(sessionInfo)
        dfGNGinfo = pd.DataFrame(session['results'])

        recordID = path.split('/')[-1][:-8]
        appVer = dfSessionInfo['appVersion'][0].replace(',', ';')
        phoneInfo = dfSessionInfo['phoneInfo'][0].replace(',', '-')
        if dfSessionInfo['files'][0]['filename'] == 'gonogo.json':
            sessTimestamp = dfSessionInfo['files'][0]['timestamp']
        else:
            sessTimestamp = dfSessionInfo['files'][1]['timestamp']
        if sessTimestamp[-1] != 'Z':
            timezone = sessTimestamp[-6:].replace(':','')
        else: 
            timezone = float('NaN')

        for i in range(len(dfGNGinfo)):
            timestamp = dfGNGinfo.iloc[i]['timestamp']
            accuracy = dfGNGinfo.iloc[i]['incorrect']
            go = dfGNGinfo.iloc[i]['go']
            rxnTime = dfGNGinfo.iloc[i]['timeToThreshold']
            trial_info = dfGNGinfo.iloc[i]['identifier']
            for mag in dfGNGinfo['samples'][i]:
                vectorMag = mag['vectorMagnitude']
                magTime = mag['timestamp']
                relTimestamp = timestamp + magTime

                data.append((str(testSubj),
                        str(recordID),
                        str(phoneInfo),
                        str(appVer), 
                        str(sessTimestamp),
                        str(timezone),
                        str(timestamp),
                        str(accuracy),
                        str(go),
                        str(rxnTime),
                        str(vectorMag),
                        str(magTime),
                        str(relTimestamp),
                        str(trial_info)
                        ))

dfOut = pd.DataFrame(data, columns=['healthCode', 'recordId_GNG', 'phoneInfo','app_version','session_timestamp',
                      'timezone','trial_timestamp','incorrect',
                      'go','timeToThreshold', 'vector_magnitude', 'accel_timestamp', 'relative_timestamp',
                      'trial_identifier'])

dfOut.to_csv(outPath+'GNG_rawData_withAccel_fromZIP.csv', index=False)

print('Finish')