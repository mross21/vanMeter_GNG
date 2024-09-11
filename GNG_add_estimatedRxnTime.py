"""
@author: Mindy Ross
python version 3.7.4
"""
# add estimated reaction time for incorrect no-go trials

import pandas as pd

fileIn = 'insert file path and file name for preprocessed GNG file' # (e.g. /home/mindy/Desktop/GNG/AllUsers_GNGdata.csv)
pathOut = 'insert folder path to save output file'

df_full = pd.read_csv(fileIn, index_col=False)
# filter out any negative response times
df = df_full.loc[pd.to_numeric(df_full['timeToThreshold']) >= 0]
dfOut = pd.DataFrame()

# make true/false columns booleans
df['go'] = df['go'].map({'True': True, 'False': False})
df['incorrect'] = df['incorrect'].map({'True': True, 'False': False})
df['vector_magnitude'] = df['vector_magnitude'].astype(float)

listOut = []
dfByUser = df.groupby(['userID', 'taskNumber'])
for user_task, group in dfByUser:
    user = user_task[0]
    task = user_task[1]
    dictThreshTime = {}

# use commented code below if want to set magnitude threshold based on values obtained from correct go trials
# sets variable threshold per GNG task per user
    # # figure out threshold based on correct go rxn times 
    # correct_go = group.loc[(group['go'] == True) & (group['incorrect'] == False)]
    # # correct_go['trial_time'] = correct_go['relative_timestamp'].astype(float) - correct_go['trial_timestamp'].astype(float)
    # correct_go_threshTime = correct_go[['userID', 'taskNumber', 'trialNumber','timeToThreshold',
    #                                     'vector_magnitude','time_since_trial_start']].reset_index()
    # correct_go_threshTime['time_diff'] = abs(correct_go_threshTime['timeToThreshold'].astype(float)-correct_go_threshTime['time_since_trial_start'].astype(float))
    # threshTimeIdx = correct_go_threshTime.groupby('trialNumber')['time_diff'].idxmin()
    # task_thresh = correct_go_threshTime.iloc[threshTimeIdx]['vector_magnitude'].min()

    # # check if any threshold magnitudes are under 0.5
    # if task_thresh < 0.5:
    #     print('user: ' + str(user))
    #     print('task number: ' + str(task))
    #     print(task_thresh)
    #     print(correct_go_threshTime.iloc[threshTimeIdx])
    #     break

    task_thresh = 0.5
    
    # find incorrect response times
    dfByTrial = group.groupby(['trialNumber'])
    for trial, grp in dfByTrial:
        grp.sort_values(by=['time_since_trial_start'], ascending=True, inplace=True, ignore_index=True)
        # extract time to threshold
        if ((grp['go'].iloc[0] == False) & (grp['incorrect'].iloc[0] == True)):
            threshIdx = (grp['vector_magnitude'] >=task_thresh).idxmax()
            incorr_thresh_time = grp.loc[grp.index == threshIdx]['time_since_trial_start'].iloc[0]
            dictThreshTime.update({trial: incorr_thresh_time})
        else:
            dictThreshTime.update({trial: grp['timeToThreshold'].iloc[0]})


    group['timeToThreshold_all'] = group['trialNumber'].map(dictThreshTime)
    group['est_threshold_magnitude'] = task_thresh

    # removes accelerometer values
    # comment out if want to save accelerometer rows
    listOut.append(group.groupby(['trialNumber']).first().reset_index()) # append first row per trial (remove accel)
    # # use below if want to save accelerometer rows
    # listOut.append(group)

dfOut = pd.concat(listOut)
dfOut2 = dfOut[['healthCode','recordId_GNG','userID','phoneInfo','app_version','sessionTimestampLocal','date',
                'taskNumber','trialNumber','go','incorrect','timeToThreshold_all','est_threshold_magnitude','timeToThreshold',
                'time_since_trial_start','relative_timestamp','trial_timestamp','item','session_timestamp','timezone']]
dfOut2.to_csv(pathOut+'AllUsers_GNGdata_allResponseTimes.csv', index=False)

print('finish')