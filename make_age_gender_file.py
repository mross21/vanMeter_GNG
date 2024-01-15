#%%
import pandas as pd

demoFile = '/home/mindy/Desktop/BiAffect-iOS/vanMeter/raw_input/BiAffect_Participant_Self-Report.csv'
IDfile = '/home/mindy/Desktop/BiAffect-iOS/vanMeter/raw_input/ID_link.csv'

dfDemo = pd.read_csv(demoFile, index_col=False).dropna()
dfID = pd.read_csv(IDfile, index_col=False)

# dictID = dict(zip(dfID['Health Code'], dfID['ID']))
dictAge = dict(zip(dfDemo['participant_id'], dfDemo['age_baseline_pt']))
dictSex = dict(zip(dfDemo['participant_id'], dfDemo['baseline_sex']))
dictGender = dict(zip(dfDemo['participant_id'], dfDemo['baseline_gender']))

dfID['age'] = dfID['ID'].map(dictAge)
dfID['sex'] = dfID['ID'].map(dictSex)
dfID['gender'] = dfID['ID'].map(dictGender)


dfID.to_csv('/home/mindy/Desktop/BiAffect-iOS/vanMeter/raw_input/ID_link_withDemographics.csv', index=False)

# %%
