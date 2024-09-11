"""
@author: Mindy Ross
python version 3.7.4
"""
import pandas as pd

file = '/home/mindy/Desktop/BiAffect-iOS/vanMeter/raw_input/BiAffect_PRS_Data_09092024.csv'
df = pd.read_csv(file, index_col=False)

df['psr_startdate'] = pd.to_datetime(df['psr_startdate']).dt.date
df['psr_enddate'] = pd.to_datetime(df['psr_enddate']).dt.date

dfDep = df.iloc[:,[0,1,2,3,4,5,6,7,8,9,10,11,12]]
dfSuic = df.iloc[:,[0,1,2,3,13,14,15,16,17,18,19,20,21]]
dfMania = df.iloc[:,[0,1,2,3,22,23,24,25,26,27,28,29,30]]
dfAnx = df.iloc[:,[0,1,2,3,31,32,33,34,35,36,37,38,39]]

dfList = [dfDep, dfSuic, dfMania, dfAnx]
dfOut = pd.melt(dfDep, id_vars=['participant_id','psr_startdate','psr_enddate','prs_numweeks'],
            var_name='weekFromEnd', value_name='score').sort_values(by=['participant_id',
            'psr_startdate']).dropna(subset = ['score']).reset_index(drop=True)
dfOut['weekFromEnd'] = dfOut['weekFromEnd'].str.extract('(\d+)').astype(int)
dfOut = dfOut.iloc[:,0:5]

for d in dfList:
    dfLong = pd.melt(d, id_vars=['participant_id','psr_startdate','psr_enddate','prs_numweeks'],
            var_name='weekFromEnd', value_name=('score')).sort_values(by=['participant_id','psr_startdate'])
    dfLong = dfLong.dropna(subset = ['score']).reset_index(drop=True)
    score_type = dfLong['weekFromEnd'].str.split('_').str[0][0]
    dfLong.rename(columns={"score": score_type + '_score'}, inplace=True)
    dfLong['weekFromEnd'] = dfLong['weekFromEnd'].str.extract('(\d+)').astype(int)
    dfLong.insert(5, 'weekDate', dfLong['psr_enddate'] - (dfLong['weekFromEnd'] * pd.Timedelta(7, 'days')) - pd.Timedelta(7, 'days'))
    dfLong.insert(6, 'weekDateEnd', dfLong['psr_enddate'] - (dfLong['weekFromEnd'] * pd.Timedelta(7, 'days')))

    dfOut = pd.merge(dfOut, dfLong, how='outer')

dfOut.to_csv('/home/mindy/Desktop/BiAffect-iOS/vanMeter/raw_input/BiAffect_Interview_Data_longFormat-v4.csv', index=False)


