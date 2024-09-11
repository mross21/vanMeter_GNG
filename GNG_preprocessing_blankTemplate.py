"""
@author: Mindy Ross
python version 3.7.4
pandas version 1.3.5
"""
# preprocess GNG raw file downloaded from synapse ZIP files

# import libraries
import pandas as pd
from pyarrow import parquet

# file path for location of user data
pathIn = 'insert file path here' # file path to folder containing raw GNG file
# file path for healthCodes & userIDs
pathUser = 'insert file path here' # file path to folder containing healthCodes csv file
# file path for location of output files
pathOut = 'insert file path here' # file path to where output file should go
# filename of raw GNG data from synapse
filename = 'insert filename here'
# filename of healthCodes & userIDs
userFilename = 'insert filename here'

# FUNCTIONS 
# assign numbers to record IDs (GNG tasks)
def assignGNGNumber(dataframe):
    # need to group by user ID first
    userList = list(dataframe['recordId_GNG'].unique())
    numberList = list(range(1, len(userList)+1))
    d = dict(zip(userList, numberList))
    dataframe['taskNumber'] = dataframe['recordId_GNG'].map(d)
    return(dataframe)
    
# check order of sessions in dataframe
def checkSessionOrder(dataframe):
    unordered = []
    row = 0
    taskNo = dataframe.taskNumber
    print(str('checking task order for user ') + dataframe.userID.unique())
    for i, j in zip(taskNo, taskNo.shift(1)):
        row = row
        if i < j:
            unordered.append((str(dataframe.userID.unique()), row, i, j))
        row = row + 1
    df = pd.DataFrame(unordered, columns = ['userID', 'row', 
                                                 'currentTask', 'previousTask'])
    if unordered != []:
        print(df)
    else:
        print('ordered')
    return(unordered) 

def assignTrialNumber(dataframe):
    # need to group by user ID first
    # need to have column for task number (assignGGNNumber() function)
    dictOuter = {}
    # number trials by item ID
    dfByTask = dataframe.groupby(['taskNumber'])
    for task, group in dfByTask:
        trialList = list(group['trial_identifier'].unique())
        numberList = list(range(1, len(trialList)+1))
        dictInner = dict(zip(trialList, numberList))
        dictOuter[task] = dictInner    
    dataframe['trialNumber'] = dataframe.apply(lambda x: dictOuter[x['taskNumber']][x['trial_identifier']], axis=1)
    return(dataframe)

def timeSinceTrialStart(dataframe):
    out = []
    dfByTask = dataframe.groupby(['trial_identifier']) # group by task and trial
    for taskTrial, grp in dfByTask:
        firstTimestamp = float(grp['accel_timestamp'].iloc[0])
        if firstTimestamp > 1:
            grp['time_since_trial_start'] = grp['accel_timestamp'].astype(float) - firstTimestamp
        else:
            grp['time_since_trial_start'] = grp['accel_timestamp'].astype(float)
        out.append(grp)
    out = pd.concat(out)
    return(out)
    
# read csv into dataframe (should only be one of all users from Synapse)
df = pd.read_parquet(pathIn + filename, engine='pyarrow')

# add user ID
dfUser = pd.read_parquet(pathUser + userFilename, engine='pyarrow')
userDict = dict(zip(dfUser.healthCode, dfUser.userID))
df['userID'] = df['healthCode'].map(userDict)

# calculate date
df['date'] = df['session_timestamp'].str.split('T').str[0]
df['time'] = df['session_timestamp'].str.split('T').str[1].str.split('-').str[0]
df['sessionTimestampLocal'] = pd.to_datetime(df['date'] + ' ' + df['time'], utc=True).dt.tz_localize(None)

# sort by combined timestamp before labeling trials
df.sort_values(by=['userID','sessionTimestampLocal','relative_timestamp'], ascending=True, inplace=True, ignore_index=True)

# make empty dataframe
dfOut = pd.DataFrame()

# group by userID
dfByUser = df.groupby(['userID'])

# loop through each user and add variables
for u, group in dfByUser:
    recordID = group.recordId_GNG
    taskNo = assignGNGNumber(group).taskNumber
    user = group.userID
    hc = group.healthCode
    phoneInfo = group.phoneInfo
    app = group.app_version
    startT = group.session_timestamp
    startTL = group.sessionTimestampLocal
    d = group.date
    tzone = group.timezone
    rel_t = group.relative_timestamp
    time_since = timeSinceTrialStart(group).time_since_trial_start
    t = group.trial_timestamp
    incorr = group.incorrect  
    go = group.go
    timeToThresh = group.timeToThreshold
    trialNo = assignTrialNumber(group).trialNumber
    rel_time = group.accel_timestamp
    mag = group.vector_magnitude
    i = group.trial_identifier
    
# make df of results from each loop and append to dfOut
    toAdd = pd.DataFrame({'healthCode': hc,
                          'recordId_GNG': recordID,
                          'userID': user,
                          'phoneInfo': phoneInfo,
                          'app_version': app,
                          'sessionTimestampLocal': startTL,
                          'date': d,
                          'taskNumber': taskNo,
                          'trialNumber': trialNo,
                          'go': go,
                          'timeToThreshold': timeToThresh,
                          'relative_timestamp': rel_t,
                          'time_since_trial_start': time_since,
                          'trial_timestamp': t,
                          'incorrect': incorr,
                          'accel_timestamp': rel_time,
                          'vector_magnitude': mag,
                          'item': i,
                          'session_timestamp': startT,
                          'timezone': tzone})
    dfOut = dfOut.append(toAdd, ignore_index=True, sort=False)
    print('Finished user ' + str(group['userID'].unique()))
            
dfOut.to_csv(pathOut + 'AllUsers_GNGdata_withAccel_fromZIP.csv', index=False)

print('Finish')
# %%