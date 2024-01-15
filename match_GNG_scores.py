#%%
import pandas as pd
import numpy as np
import datetime
from collections import defaultdict

gngFile = '/home/mindy/Desktop/BiAffect-iOS/vanMeter/processed_output/AllUsers_GNGdata_fromZIP_allResponseTimes.csv'
IDlinkFile = '/home/mindy/Desktop/BiAffect-iOS/vanMeter/raw_input/ID_link_withDemographics.csv'
smsFile = '/home/mindy/Desktop/BiAffect-iOS/vanMeter/raw_input/BiAffect_SMS.csv'
interviewFile = '/home/mindy/Desktop/BiAffect-iOS/vanMeter/raw_input/BiAffect_Interview_Data_longFormat-v2.csv'
selfReportFile = '/home/mindy/Desktop/BiAffect-iOS/vanMeter/raw_input/BiAffect_Participant_Self-Report_01112024.csv'

dfGNG = pd.read_csv(gngFile, index_col=False)
dfIDs = pd.read_csv(IDlinkFile, index_col=False)
dfSMS = pd.read_csv(smsFile, index_col=False)
dfInterview = pd.read_csv(interviewFile, index_col=False)
dfSelfReport = pd.read_csv(selfReportFile, index_col=False)

# match userIDs to IDs
dictIDs = dict(zip(dfIDs['Health Code'], dfIDs['ID']))
dfGNG['studyID'] = dfGNG['healthCode'].map(dictIDs)
dfGNG = dfGNG.dropna(subset = ['studyID'])

IDlist = dfGNG['studyID'].unique()
# IDlist = IDlist[~(np.isnan(IDlist))]

# make dictionaries for age/sex/gender
dictAge = dict(zip(dfIDs['ID'], dfIDs['age']))
dictSex = dict(zip(dfIDs['ID'], dfIDs['sex']))
dictGender = dict(zip(dfIDs['ID'], dfIDs['gender']))

# remove weird dates
dfSMS['date'] = np.where(dfSMS['date'] == '1/0/00 0:00', float('NaN'), dfSMS['date'])
dfSMS.dropna(subset=['date'], inplace=True)
dfSMS['date'] = pd.to_datetime(dfSMS['date'].str.split(' ').str[0], format = '%m/%d/%y').dt.date

# set pd.datetime
dfGNG['date'] = pd.to_datetime(dfGNG['date']).dt.date
dfInterview['weekDate'] = pd.to_datetime(dfInterview['weekDate']).dt.date
dfInterview['weekDateEnd'] = pd.to_datetime(dfInterview['weekDateEnd']).dt.date
dfSelfReport['date'] = pd.to_datetime(dfSelfReport['date']).dt.date


outGNG = []
# dictSleep = defaultdict(dict)
# dictSI = defaultdict(dict)
# dictDesire = defaultdict(dict)
# dictIntent = defaultdict(dict)
# dictSH = defaultdict(dict)

for ID in IDlist:
    grpSMS = dfSMS.loc[dfSMS['ID'] == ID]
    grpGNG = dfGNG.loc[dfGNG['studyID'] == ID]
    grpInterview = dfInterview.loc[dfInterview['participant_id'] == ID]
    grpSelfReport = dfSelfReport.loc[dfSelfReport['participant_id'] == ID]

    # add month start date to self-report file
    grpSelfReport['monthStart'] = np.where((grpSelfReport['date'] - pd.Timedelta(30, unit='days')) < grpSelfReport['date'].shift(1),
                                        grpSelfReport['date'].shift(1), (grpSelfReport['date'] - pd.Timedelta(30, unit='days')))
    
    # get age, sex, and gender
    age = dictAge.get(ID)
    sex = dictSex.get(ID)
    gender = dictGender.get(ID)
    # age = np.unique(grpSelfReport['age_baseline_pt'])
    # age = age[~np.isnan(age)][0]
    # sex = np.unique(grpSelfReport['baseline_sex'])
    # sex = sex[~np.isnan(sex)][0]
    # gender = np.unique(grpSelfReport['baseline_gender'])
    # gender = gender[~np.isnan(gender)][0]


    dateList = grpGNG['date'].unique()

    for date in dateList:
        # print(f'GNG date: {date}')
        gngTask = grpGNG.loc[grpGNG['date'] == date]

        gngTask['age'] = age
        gngTask['sex'] = sex
        gngTask['gender'] = gender

        # SMS
        grpSMS['diffDays'] = grpSMS['date'] - date
        matchDate = grpSMS.loc[grpSMS['diffDays'] == grpSMS['diffDays'].min()]
        if len(matchDate) < 1:
            gngTask['sms_sleep'] = np.nan
            gngTask['sms_SI'] = np.nan
            gngTask['sms_desire'] = np.nan
            gngTask['sms_intent'] = np.nan
            gngTask['sms_self_harm'] = np.nan
        elif grpSMS['diffDays'].min() <= pd.Timedelta(7,unit='days'):
            gngTask['sms_sleep'] = matchDate['sleep'].mean()
            gngTask['sms_SI'] = matchDate['si_current_y_n'].mean()
            gngTask['sms_desire'] = matchDate['desire_to_die'].mean()
            gngTask['sms_intent'] = matchDate['suicide_intent'].mean()
            gngTask['sms_self_harm'] = matchDate['any_self_harm_y_n'].mean()
        else:
            gngTask['sms_sleep'] = np.nan
            gngTask['sms_SI'] = np.nan
            gngTask['sms_desire'] = np.nan
            gngTask['sms_intent'] = np.nan
            gngTask['sms_self_harm'] = np.nan

        # INTERVIEW
        interviewRow = grpInterview.loc[(grpInterview['weekDate'] <= date) & 
                                         (grpInterview['weekDateEnd'] >= date)]
        
        gngTask['interview_dep_score'] = interviewRow['dep_score'].mean()
        gngTask['interview_SI_score'] = interviewRow['suic_score'].mean()
        gngTask['interview_mania_score'] = interviewRow['mania_score'].mean()
        gngTask['interview_anx_score'] = interviewRow['anx_score'].mean()


        # self-report
        selfReportRow = grpSelfReport.loc[(grpSelfReport['date'] >= date) & (grpSelfReport['monthStart'] < date)]

        gngTask['self_report_dep_score'] = selfReportRow['self_report_depression'].mean()
        gngTask['self_report_mania_score'] = selfReportRow['self_report_mania'].mean()
        # gngTask['self_report_sleepDisturbance_score'] = selfReportRow['sleep_disturbance'].mean()
        gngTask['self_report_anx_score'] = selfReportRow['self_report_anxiety'].mean()

        # append GNG
        outGNG.append(gngTask)

dfOut = pd.concat(outGNG)

        # # dict of ID, date, and scores
        # dictSleep[ID][date] = sleep
        # dictSI[ID][date] = SI
        # dictDesire[ID][date] = desire
        # dictIntent[ID][date] = intent
        # dictSH[ID][date]= sh

# dfGNG['sleep'] = dfGNG.apply(lambda x: dictSleep[x['studyID']][x['date']], axis=1)
# dfGNG['SI'] = dfGNG.apply(lambda x: dictSI[x['studyID']][x['date']], axis=1)
# dfGNG['desire'] = dfGNG.apply(lambda x: dictDesire[x['studyID']][x['date']], axis=1)
# dfGNG['intent'] = dfGNG.apply(lambda x: dictIntent[x['studyID']][x['date']], axis=1)
# dfGNG['self_harm'] = dfGNG.apply(lambda x: dictSH[x['studyID']][x['date']], axis=1)


dfOut.to_csv('/home/mindy/Desktop/BiAffect-iOS/vanMeter/gng/gng_sms_processed_output-v3.csv', index=False)

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
