#%%
import pandas as pd
import numpy as np
import datetime
from collections import defaultdict

gngFile = '/home/mindy/Desktop/BiAffect-iOS/vanMeter/processed_output/AllUsers_GNGdata_fromZIP_allResponseTimes.csv'
IDlinkFile = '/home/mindy/Desktop/BiAffect-iOS/vanMeter/raw_input/ID_link.csv'
# participantFile = '/home/mindy/Desktop/BiAffect-iOS/vanMeter/raw_input/participants.csv'
smsFile = '/home/mindy/Desktop/BiAffect-iOS/vanMeter/raw_input/BiAffect_SMS.csv'

dfGNG = pd.read_csv(gngFile, index_col=False)
dfIDs = pd.read_csv(IDlinkFile, index_col=False)
# dfParticipants = pd.read_csv(participantFile, index_col=False)
dfSMS = pd.read_csv(smsFile, index_col=False)


# match userIDs to IDs
dictIDs = dict(zip(dfIDs['Health Code'], dfIDs['ID']))
dfGNG['studyID'] = dfGNG['healthCode'].map(dictIDs)
dfGNG = dfGNG.dropna(subset = ['studyID'])

IDlist = dfGNG['studyID'].unique()
# IDlist = IDlist[~(np.isnan(IDlist))]

# remove weird dates
dfSMS['date'] = np.where(dfSMS['date'] == '1/0/00 0:00', float('NaN'), dfSMS['date'])
dfSMS.dropna(subset=['date'], inplace=True)
dfSMS['date'] = pd.to_datetime(dfSMS['date'].str.split(' ').str[0], format = '%m/%d/%y').dt.date

dfGNG['date'] = pd.to_datetime(dfGNG['date']).dt.date


outGNG = []
dictSleep = defaultdict(dict)
dictSI = defaultdict(dict)
dictDesire = defaultdict(dict)
dictIntent = defaultdict(dict)
dictSH = defaultdict(dict)

for ID in IDlist:
    grpSMS = dfSMS.loc[dfSMS['ID'] == ID]
    grpGNG = dfGNG.loc[dfGNG['studyID'] == ID]

    dateList = grpGNG['date'].unique()

    for date in dateList:
        # print(f'GNG date: {date}')
        grpSMS['diffDays'] = grpSMS['date'] - date
        matchDate = grpSMS.loc[grpSMS['diffDays'] == grpSMS['diffDays'].min()]
        if len(matchDate) < 1:
            sleep = np.nan
            SI = np.nan
            desire = np.nan
            intent = np.nan
            sh = np.nan
        elif grpSMS['diffDays'].min() <= pd.Timedelta(7,unit='days'):
            sleep = matchDate['sleep'].mean()
            SI = matchDate['si_current_y_n'].mean()
            desire = matchDate['desire_to_die'].mean()
            intent = matchDate['suicide_intent'].mean()
            sh = matchDate['any_self_harm_y_n'].mean()
        else:
            sleep = np.nan
            SI = np.nan
            desire = np.nan
            intent = np.nan
            sh = np.nan



        dictSleep[ID][date] = sleep
        dictSI[ID][date] = SI
        dictDesire[ID][date] = desire
        dictIntent[ID][date] = intent
        dictSH[ID][date]= sh
  
dfGNG['sleep'] = dfGNG.apply(lambda x: dictSleep[x['studyID']][x['date']], axis=1)
dfGNG['SI'] = dfGNG.apply(lambda x: dictSI[x['studyID']][x['date']], axis=1)
dfGNG['desire'] = dfGNG.apply(lambda x: dictDesire[x['studyID']][x['date']], axis=1)
dfGNG['intent'] = dfGNG.apply(lambda x: dictIntent[x['studyID']][x['date']], axis=1)
dfGNG['self_harm'] = dfGNG.apply(lambda x: dictSH[x['studyID']][x['date']], axis=1)


dfGNG.to_csv('/home/mindy/Desktop/BiAffect-iOS/vanMeter/gng/gng_sms_processed_output.csv', index=False)

#%%
# # MATCH SMS TO EXACT GNG DATE
# outGNG = []
# for ID in IDlist:
#     grpSMS = dfSMS.loc[dfSMS['ID'] == ID]

#     dictSleep = dict(zip(grpSMS['date'], grpSMS['sleep']))
#     dictSI = dict(zip(grpSMS['date'], grpSMS['si_current_y_n']))
#     dictDesire = dict(zip(grpSMS['date'], grpSMS['desire_to_die']))
#     dictIntent = dict(zip(grpSMS['date'], grpSMS['suicide_intent']))
#     dictSH = dict(zip(grpSMS['date'], grpSMS['any_self_harm_y_n']))

#     grpGNG = dfGNG.loc[dfGNG['studyID'] == ID]

#     grpGNG['sleep'] = grpGNG['date'].map(dictSleep)
#     grpGNG['SI'] = grpGNG['date'].map(dictSI)
#     grpGNG['desire'] = grpGNG['date'].map(dictDesire)
#     grpGNG['intent'] = grpGNG['date'].map(dictIntent)
#     grpGNG['self_harm'] = grpGNG['date'].map(dictSH)

#     outGNG.append(grpGNG)

# dfGNGOut = pd.concat(outGNG,axis=0,ignore_index=True)

# %%
