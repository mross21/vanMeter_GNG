# vanMeter_GNG

Uses these package versions: 
python version 3.7.4
pandas version 1.3.5

DATA PROCESSING

Clinical Data
    1. Reformat PRS file to long format using reformat_biaffectInterviewFile.py. 
        ◦ Change line 7 to list the file path and file name of the biaffect PRS data
        ◦ Change line 37 to the file path and file name of the where you would like the output file and what you would like to name it

GNG Data
    1. Download the GNG data using the participants.csv file and the script getGNG_blankTemplate.py. The participant file will need to be updated as more participants are added to the study.
        ◦ Input synapse username and password into lines 16 and 17
        ◦ Insert file path to location of participants.csv file in line 21
        ◦ Insert file path to desired location of output file
        ◦ Note: this download may take a while depending on how much data needs to be downloaded
    2. First processing of raw GNG data using GNG_preprocessing_blankTemplate.py.
        ◦ Insert file path to raw GNG data in line 13
        ◦ Insert file path to participants.csv in line 15
        ◦ Insert desired file path of output file in line 17
        ◦ Insert filename of raw GNG data in line 19 (will be GNG_rawData_withAccel_fromZIP.csv if no changes were made)
        ◦ Insert file containing participant list in line 21 (will be participants.csv if no changes were made)
    3. Add estimated reaction times from incorrect no-go trials using the GNG_add_estimatedRxnTime.py script.
        ◦ Insert file path and file name from the output file obtained following the above step in line 9
        ◦ Insert desired file path for output file in line 10
        ◦ This output file will be used to compare to the clinical data

Match Clinical and GNG Data
    1. Combine the clinical and GNG data into one file using the match_GNG_scores.py script.
        ◦ Change the file path and filename in line 7 to the location and filename of the GNG data file from step 3 above
        ◦ Change the file path and filename to the location and filename of the ID link file (with age and gender) in line 8
        ◦ Change the file path and filename to the location and filename of the PRS clinical data in line 10
        ◦ Change the file path in line 128 to the desired output folder location.
        ◦ This output file will be used in R for analysis

Analysis in R
    1. Use the GNG_analysis_v4.Rmd file to run the analyses.
        ◦ Change line 32 to list the file path and filename of the matched clinical and GNG data file from the above step.
        ◦ Output file will be saved in the same folder as location of input data using the filename GNG_analysis_v4.html. 