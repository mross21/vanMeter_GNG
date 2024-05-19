#%%
import pandas as pd
import numpy as np
from collections import defaultdict

gngFile = '/home/mindy/Desktop/BiAffect-iOS/vanMeter/processed_output/AllUsers_GNGdata_fromZIP_allResponseTimes.csv'
IDlinkFile = '/home/mindy/Desktop/BiAffect-iOS/vanMeter/raw_input/ID_link_updated_05182024.csv'
smsFile = '/home/mindy/Desktop/BiAffect-iOS/vanMeter/raw_input/BiAffect_SMS.csv'
interviewFile = '/home/mindy/Desktop/BiAffect-iOS/vanMeter/raw_input/BiAffect_Interview_Data_longFormat-v3.csv'
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
# dictSex = dict(zip(dfIDs['ID'], dfIDs['sex']))
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

# set output list
outGNG = []

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
    # sex = dictSex.get(ID)
    gender = dictGender.get(ID)

    # make list of all GNG dates
    dateList = grpGNG['date'].unique()

    # loop through all GNG dates
    for date in dateList:
        # print(f'GNG date: {date}')
        gngTask = grpGNG.loc[grpGNG['date'] == date]

        gngTask['age'] = age
        # gngTask['sex'] = sex
        gngTask['gender'] = gender

        # get closest SMS values for each GNG up to one week
        # SMS
        grpSMS['diffDays'] = grpSMS['date'] - date
        matchDate = grpSMS.loc[grpSMS['diffDays'] == grpSMS['diffDays'].min()]
        # if no SMS found, set values as NaN
        if len(matchDate) < 1:
            gngTask['sms_sleep'] = np.nan
            gngTask['sms_SI'] = np.nan
            gngTask['sms_desire'] = np.nan
            gngTask['sms_intent'] = np.nan
            gngTask['sms_self_harm'] = np.nan
        # skip if min gap is greater than 1 week
        elif abs(matchDate['diffDays'].min()) > pd.Timedelta(7,'days'):
            gngTask['sms_sleep'] = np.nan
            gngTask['sms_SI'] = np.nan
            gngTask['sms_desire'] = np.nan
            gngTask['sms_intent'] = np.nan
            gngTask['sms_self_harm'] = np.nan
        # record SMS values if one week or less from GNG date
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
        # find interview values when GNG date is between interview week start/end
        interviewRow = grpInterview.loc[(grpInterview['weekDate'] <= date) & 
                                         (grpInterview['weekDateEnd'] >= date)]
        gngTask['interview_dep_score'] = interviewRow['dep_score'].mean()
        gngTask['interview_SI_score'] = interviewRow['suic_score'].mean()
        gngTask['interview_mania_score'] = interviewRow['mania_score'].mean()
        gngTask['interview_anx_score'] = interviewRow['anx_score'].mean()

        # self-report
        # find self-report values when GNG date is between self-report week start/end
        selfReportRow = grpSelfReport.loc[(grpSelfReport['date'] >= date) & (grpSelfReport['monthStart'] < date)]
        gngTask['self_report_dep_score'] = selfReportRow['self_report_depression'].mean()
        gngTask['self_report_mania_score'] = selfReportRow['self_report_mania'].mean()
        # gngTask['self_report_sleepDisturbance_score'] = selfReportRow['sleep_disturbance'].mean()
        gngTask['self_report_anx_score'] = selfReportRow['self_report_anxiety'].mean()

        # append GNG
        outGNG.append(gngTask)

# concat all rows into one dataframe
dfOut = pd.concat(outGNG)
# save output file
dfOut.to_csv('/home/mindy/Desktop/BiAffect-iOS/vanMeter/gng/gng_sms_processed_output-v4.csv', index=False)

print('finish')
# %%
