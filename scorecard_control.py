import os
import sys
import argparse
import time
import datetime as dt
import pandas as pd
import numpy as np
import get_survey_data as data
import ai_scoring_algorithm as ai
import pm_scoring_algorithm as pm
import crypto_scoring_algorithm as cr
import time_mgmnt_scoring_algorithm as tm
import uhnw_scoring_algorithm as uhnw
import retire_scoring_algorithm as wm
import scorecard_email as mail



def runAIsurvey(participant,mail_link,df):
    path = ai.produceScorecard(participant[0],df)
    mail.getEmail(participant,mail_link,path)

def runPMsurvey(participant,mail_link,df):
    path = pm.produceScorecard(participant[0],df)
    mail.getEmail(participant,mail_link,path)

def runCryptosurvey(participant,mail_link,df):
    path = cr.produceScorecard(participant[0],df)
    mail.getEmail(participant,mail_link,path)


def runTMsurvey(participant,mail_link,df):
    path = tm.produceScorecard(participant[0],df)
    mail.getEmail(participant,mail_link,path)

def runUHNWsurvey(participant,mail_link,df):
    path = uhnw.produceScorecard(participant[0],df)
    mail.getEmail(participant,mail_link,path)

def runWealthsurvey(participant,mail_link,df):
    path = wm.produceScorecard(participant[0],df)
    mail.getEmail(participant,mail_link,path)


def main(participant):
    df = data.getData()
    flag = 0
    surveys = [62, 66, 67, 13, 63, 64]

    surveys_complete = (
        df.loc[df.userid == participant[0], ['surveyid', 'questionid']]
          .groupby('surveyid')
          .nunique()
          .reset_index()
    )

    for i in range(len(surveys)):
        survey_id = surveys[i]

        matching = surveys_complete.loc[surveys_complete['surveyid'] == survey_id, 'questionid']

        if (
            participant[3] == survey_id
            and not matching.empty
            and matching.iloc[0] == 5
        ):
                  
            for j in range(len(surveys)):
                next_survey = surveys[j]
                
                if next_survey not in surveys_complete['surveyid'].values and flag == 0:
                    mail_link = next_survey
                    flag = 1
                elif flag ==0 and j==len(surveys)-1:
                    mail_link=0

            if participant[3]==62:
                runAIsurvey(participant,mail_link,df[df.surveyid==62])
            elif participant[3]==66:
                runPMsurvey(participant,mail_link,df[df.surveyid==66])
            elif participant[3]==67:
                runCryptosurvey(participant,mail_link,df[df.surveyid==67])
            elif participant[3]==13:
                runTMsurvey(participant,mail_link,df[df.surveyid==13])
            elif participant[3]==63:
                runUHNWsurvey(participant,mail_link,df[df.surveyid==63])
            elif participant[3]==64:
                runWealthsurvey(participant,mail_link,df[df.surveyid==64])       

    return surveys_complete,matching


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate and email a scorecard for a participant.")
    parser.add_argument("--userid", type=int, required=True, help="The participant's user ID")
    parser.add_argument("--name", type=str, required=True, help="The participant's full name")
    parser.add_argument("--email", type=str, required=True, help="The participant's email address")
    parser.add_argument("--surveyid", type=int, required=True, help="The survey ID to generate a scorecard for")

    args = parser.parse_args()

    participant = [args.userid, args.name, args.email, args.surveyid]

    main(participant)