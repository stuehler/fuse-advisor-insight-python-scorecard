import pandas as pd
import numpy as np
import datetime as dt
import os
from io import StringIO
from playwright.sync_api import sync_playwright
from matplotlib.ticker import PercentFormatter
from dotenv import load_dotenv

load_dotenv()

SCORECARDS_DIR = os.path.abspath(os.environ.get("SCORECARDS_DIR", "/home/ubuntu/python/scorecards"))



##df = pd.read_csv('c:\\users\\rledb\\fuse\\fuse_advisor_business\\scoring_algorithm\\production\\retire_scoring_data_9apr2026.txt',sep='\t',header=0) ## Ultimately switch this to db sql query
##df['completed'] = pd.to_datetime(df.completed).dt.date
##df['answer'] = df['answer'].fillna('None')


## Scoring from Loren
question_display = [[r'1. How many Defined Contribution plans do you currently serve?'],
                    [r'2. Among the DC plans that you advise, which services have you provided to plan participants:'],
                    [r'3. How often have you tried to convert participants in the DC plans you serve into clients of your general wealth management practice?'],
                    [r'4. What percentage of participants in the DC plans you serve have you converted to wealth management clients?'],
                    [r'5. How did converting DC plan participants into wealth management clients compare in difficulty with acquiring new wealth management clients in other ways (referrals, marketing, etc.)?']]

question_scoring = [[96,'s',[409,0,"You need to start or partner with a DC specialist to serve more business owners.",'red'],
               [410,1,"Build on this start to bolster your relationships with small business owner clients.",'yellow'],
               [411,1,"Build on this start to bolster your relationships with small business owner clients.",'yellow'],
               [412,2,"Think about growing this specialty to reach more small businesses.",'green-light'],
               [414,3,"You could make DC plans a strategic niche. Consider an AIF or other designation.",'green-dark'],
               [416,3,"You could make DC plans a strategic niche. Consider an AIF or other designation.",'green-dark']],
        [97,'m',[0,0,"If you serve any DC plans, you need to provide at least some participant services.",'red'],
               [1,1,"Good start. You should see how you can expand interactions with participants.",'yellow'],
               [2,2,"Round out these services if you hope to convert any participants into wealth clients.",'green-light'],
               [3,2,"Round out these services if you hope to convert any participants into wealth clients.",'green-light'],
               [4,3,"You're doing well, and should be engaging participants on broad financial topics. ",'green-dark'],
               [5,3,"You're doing well, and should be engaging participants on broad financial topics. ",'green-dark']],
        [98,'s',[423,3,"To go even further, create marketing materials specifically for these situations.",'green-dark'],
               [424,2,"Good. You can probably have more non-retirement discussions than you think.",'green-light'],
               [425,1,"Your position is understandable, but think about new, more flexible agreements.",'yellow'],
               [426,0,"If you serve DC plans, consider how to enhance value without overreaching.",'red']],
        [99,'s',[427,0,"Plan participants often need general advice. Start with offers of basic planning.",'red'],
               [428,1,"Not bad. Providing occasional wealth reviews and other services could help.",'yellow'],
               [429,2,"Build more momentum with added personalized and proactive wealth services.",'green-light'],
               [430,3,"You're ahead of the pack. Consider serving more DC plans if you have the capacity.",'green-dark'],
               [431,3,"You're ahead of the pack. Consider serving more DC plans if you have the capacity.",'green-dark'],
               [433,3,"You're ahead of the pack. Consider serving more DC plans if you have the capacity.",'green-dark']],
        [100,'s',[434,3,"A solid route for client acquisition! Make sure your services stay close to best practices.",'green-dark'],
               [435,3,"A solid route for client acquisition! Make sure your services stay close to best practices.",'green-dark'],
               [436,2,"You may need more participant contact and/or a clearer wealth-advisor pitch.",'green-light'],
               [437,1,"Make this easier with a more structured outreach process for participants.",'yellow'],
               [438,0,"This shouldn't be so difficult. Talk with peers and diagnose your approach.",'red']]]

grades = [[0,'C+',"Consider more attention to DC plans, as their growth will increasingly make it easier to connect to small business owners."],
          [1,'C+',"Consider more attention to DC plans, as their growth will increasingly make it easier to connect to small business owners."],
          [2,'B-',"Expand your DC offering with participant outreach and a program to convert plan participants into wealth clients."],
          [3,'B-',"Expand your DC offering with participant outreach and a program to convert plan participants into wealth clients."],
          [4,'B-',"Expand your DC offering with participant outreach and a program to convert plan participants into wealth clients."],
          [5,'B',"Up your DC game by adding more participant engagement, rollover support, and ongoing wealth conversion efforts."],
          [6,'B',"Up your DC game by adding more participant engagement, rollover support, and ongoing wealth conversion efforts."],
          [7,'B',"Up your DC game by adding more participant engagement, rollover support, and ongoing wealth conversion efforts."],
          [8,'B',"Up your DC game by adding more participant engagement, rollover support, and ongoing wealth conversion efforts."],
          [9,'B+',"Improve integration between DC plan services and broader wealth management relationships."],
          [10,'B+',"Improve integration between DC plan services and broader wealth management relationships."],
          [11,'B+',"Improve integration between DC plan services and broader wealth management relationships."],
          [12,'A-',"Good progress! Continue innovating to deepen participant relationships and conversion success."],
          [13,'A-',"Good progress! Continue innovating to deepen participant relationships and conversion success."],
          [14,'A',"The biggest question is whether you want to expand these efforts or simply maintain your edge."],
          [15,'A',"The biggest question is whether you want to expand these efforts or simply maintain your edge."]]




def multiSelectQuestionScore(question_scoring,t2):
    score = 0
    recommendation = ''
    color = ''
    for i in np.arange(0,len(question_scoring)):
        if t2.questionid == question_scoring[i][0]:
            for j in np.arange(2,len(question_scoring[i])):
                if t2.answer == question_scoring[i][j][0]:
                    score = question_scoring[i][j][1]
                    recommendation = question_scoring[i][j][2]
                    color = question_scoring[i][j][3]
                    
    return [t2.questionid,score,recommendation,color]

def singleSelectQuestionScore(question_scoring,t2):
    score = 0
    recommendation = ''
    color = ''
    for i in np.arange(0,len(question_scoring)):
        if t2.questionid.iloc[0] == question_scoring[i][0]:
            for j in np.arange(2,len(question_scoring[i])):
                if t2.multipleChoiceAnswerId.iloc[0] == question_scoring[i][j][0]:
                    score = question_scoring[i][j][1]
                    recommendation = question_scoring[i][j][2]
                    color = question_scoring[i][j][3]
                    
    return [t2.questionid.iloc[0],score,recommendation,color]


def score_user(question_scoring,user,df):
    user_grading = []
    t1 = df[df.userid==user][['questionid','multipleChoiceQuestionTypeId','userid','answer']].groupby(['questionid','multipleChoiceQuestionTypeId','userid']).count().reset_index()
    sa = df[(df.userid==user)&(df.multipleChoiceQuestionTypeId==1)][['questionid','multipleChoiceAnswerId']].reset_index(drop=True)
    user_score = 0

    for q in t1.index:
        if t1.loc[q].multipleChoiceQuestionTypeId == 2:
            user_grading.append(multiSelectQuestionScore(question_scoring,t1.loc[q]))
        elif t1.loc[q].multipleChoiceQuestionTypeId == 1:
            user_grading.append(singleSelectQuestionScore(question_scoring,sa[sa.questionid==t1.loc[q].questionid]))

    return user_grading

def assignSummary(output):
    score = 0
    summary = ''
    for i in np.arange(0,len(output)):
        score = score+output[i][1]

    for i in np.arange(0,len(grades)):
        if score==grades[i][0]:
            grade = grades[i][1]
            summary = grades[i][2].split('|')

    return [score,grade,summary]


def produceScorecard(user,df):
    output = score_user(question_scoring,user,df)
    summary = assignSummary(output)


    you = df[df.userid==user][['questionid','question','answer','userid']].groupby(['questionid','question','answer']).count()
    total = df[['questionid','question','answer','userid','displayorder']].groupby(['questionid','question','answer','displayorder']).count()
    total_count = df[['answer','questionid','userid']].groupby(['questionid','userid']).count().reset_index()
    total_user = total_count[['questionid','userid']].groupby('questionid').count()
    total = total.join(total_user,rsuffix='_total')
    total['percent'] = total.userid/total.userid_total
    total = total.join(you,how='left',rsuffix='_you').sort_values(['questionid','displayorder']).reset_index()
    total['You'] = ''
    total.loc[total[total.userid_you==1].index,'You'] = chr(10003)
    total.loc[total[total.percent.isnull()].index,'percent'] = 0




    total = total.rename(columns={
        'answer':'Response',
        'percent':'All Advisors'
    })

    questions = total[['questionid','question']].drop_duplicates().reset_index(drop=True)

    items = summary[2]

    summary_html = "<ul>" + "".join(
        f"<li>{item}</li>" for item in items
    ) + "</ul>"


    ## Table 1
    table_df1 = (
        total[total.questionid==96][['Response','You','All Advisors']]
        .head(10)
    )

    table_html1 = (
        '<div style="max-width: 400px;">'
        + table_df1.to_html(
            index=False,
            classes="score-table",
            float_format="{:.0%}".format,
            border=0
        )
        + '</div>'
    )

    rec1 = output[0][2]
    color1 = output[0][3]

    ## Table 2
    table_df2 = (
        total[total.questionid==97][['Response','You','All Advisors']]
        .head(10)
    )

    table_html2 = (
        '<div style="max-width: 400px;">'
        + table_df2.to_html(
            index=False,
            classes="score-table",
            float_format="{:.0%}".format,
            border=0
        )
        + '</div>'
    )

    rec2 = output[1][2]
    color2 = output[1][3]

    ## Table 3
    table_df3 = (
        total[total.questionid==98][['Response','You','All Advisors']]
        .head(10)
    )

    table_html3 = (
        '<div style="max-width: 400px;">'
        + table_df3.to_html(
            index=False,
            classes="score-table",
            float_format="{:.0%}".format,
            border=0
        )
        + '</div>'
    )

    rec3 = output[2][2]
    color3 = output[2][3]

    ## Table 4
    table_df4 = (
        total[total.questionid==99][['Response','You','All Advisors']]
        .head(10)
    )

    table_html4 = (
        '<div style="max-width: 400px;">'
        + table_df4.to_html(
            index=False,
            classes="score-table",
            float_format="{:.0%}".format,
            border=0
        )
        + '</div>'
    )

    rec4 = output[3][2]
    color4 = output[3][3]

    ## Table 5
    table_df5 = (
        total[total.questionid==100][['Response','You','All Advisors']]
        .head(10)
    )

    table_html5 = (
        '<div style="max-width: 400px;">'
        + table_df5.to_html(
            index=False,
            classes="score-table",
            float_format="{:.0%}".format,
            border=0
        )
        + '</div>'
    )

    rec5 = output[4][2]
    color5 = output[4][3]


    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Wealth/Retirement Convergence</title>

    <style>
      * {{
        box-sizing: border-box;
      }}

      body {{
        margin: 0;
        background: #f3f3f3;
        font-family: Calibri, Arial, sans-serif;
        color: #111;
      }}

      .page {{
        width: 1000px;
        margin: 15px auto;
        padding: 25px 35px 25px;
        background: #f3f3f3;
      }}

      .topbar {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 16px;
      }}

      .brand {{
        display: flex;
        align-items: center;
        gap: 10px;
      }}

      .brand-badge {{
        background: #8f0f2d;
        color: #fff;
        font-weight: 700;
        font-size: 40px;
        padding: 8px 14px;
        border-radius: 5px;
      }}

      .brand-text {{
        font-size: 40px;
        color: #444;
      }}

      .grade-box {{
        width: 160px;
        background: #8f0f2d;
        color: #fff;
        border-radius: 5px;
        text-align: center;
        padding: 10px;
      }}

      .grade-box .label {{
        font-size: 14px;
        text-transform: uppercase;
        margin-bottom: 4px;
      }}

      .grade-box .grade {{
        font-size: 54px;
        font-weight: 700;
      }}

      .title {{
        font-size: 22px;
        font-weight: 600;
        margin: 6px 0 14px;
      }}

      .takeaway {{
        border: 1.5px solid #9d4b57;
        border-radius: 12px;
        padding: 10px 12px;
        font-size: 14px;
        margin-bottom: 16px;
        background: #fafafa;
      }}

      .score-table {{
      border-collapse: collapse;
      width: 100%;
        }}

        .score-table th:first-child,
        .score-table td:first-child {{
          text-align: left;
        }}

        .score-table td, 
        .score-table th {{
          padding: 4px 6px;
          text-align: right;
          vertical-align: top;
          font-size: 0.9rem;
        }}

        .score-table th {{
          background: #f7f7f7;
        }}

        .score-table tr:nth-child(odd) {{
          background: #B6D0E2;
        }}


      .grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 14px 16px;
      }}

      .card {{
        border: 1.5px solid #9d4b57;
        border-radius: 12px;
        padding: 12px;
        background: #f7f7f7;
        height: auto;
        min-height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
      }}

      .card h2 {{
        font-size: 14px;
        margin: 0 0 8px;
        line-height: 1.25;
        font-weight: 600;
      }}

      .recommendation {{
        display: flex;
        margin-top: 12px;
        align-items: flex-start;
        gap: 8px;
        font-size: 14px;
        line-height: 1.3;
      }}

      .color-box {{
        width: 18px;
        height: 14px;
        margin-top: 2px;
        border: 1px solid rgba(0,0,0,0.3);
        flex: 0 0 auto;
      }}

      .green-dark {{ background: #2E7D32; }}
      .green-light {{ background: #8bc34a; }}
      .red {{ background: #D64541; }}
      .yellow {{ background: #F4B400; }}

      .recommendation strong {{
        font-weight: 600;
      }}

      .footer-note {{
        padding-top: 30px;
        font-size: 14px;
      }}

      .footer-line {{
        border-top: 1.5px solid #222;
        margin-bottom: 14px;
        width: 90%;
      }}

      .footer-note p {{
        margin: 0 0 10px;
      }}

      .footer-note a {{
        color: #4f7f96;
        text-decoration: underline;
      }}

    </style>
    </head>

    <body>
    <div class="page">

      <div class="topbar">
        <div class="brand">
          <div class="brand-badge">fuse</div>
          <div class="brand-text">Advisor Insight</div>
        </div>

        <div class="grade-box">
          <div class="label">Your Overall Grade</div>
          <div class="grade">{summary[1]}</div>
        </div>
      </div>

      <div class="title">Survey: Wealth/Retirement Convergence</div>

      <div class="takeaway">
        <strong>KEY TAKEAWAY:</strong>
        {items[0]}
      </div>

      <div class="grid">

        <div class="card">
          <div>
            <h2>{question_display[0][0]}</h2>
            <div>{table_html1}</div>
          </div>
          <div class="recommendation">
            <span class="color-box {color1}"></span>
            <div><strong>Recommendation: </strong>{rec1}</div>
          </div>
        </div>

        <div class="card">
          <div>
            <h2>{question_display[1][0]}</h2>
            <div>{table_html2}</div>
          </div>
          <div class="recommendation">
            <span class="color-box {color2}"></span>
            <div><strong>Recommendation: </strong>{rec2}</div>
          </div>
        </div>

        <div class="card">
          <div>
            <h2>{question_display[2][0]}</h2>
            <div>{table_html3}</div>
          </div>
          <div class="recommendation">
            <span class="color-box {color3}"></span>
            <div><strong>Recommendation: </strong>{rec3}</div>
          </div>
        </div>

        <div class="card">
          <div>
            <h2>{question_display[3][0]}</h2>
            <div>{table_html4}</div>
          </div>
          <div class="recommendation">
            <span class="color-box {color4}"></span>
            <div><strong>Recommendation: </strong>{rec4}</div>
          </div>
        </div>

        <div class="card">
          <div>
            <h2>{question_display[4][0]}</h2>
            <div>{table_html5}</div>
          </div>
          <div class="recommendation">
            <span class="color-box {color5}"></span>
            <div><strong>Recommendation: </strong>{rec5}</div>
          </div>
        </div>

        <div class="footer-note">
          <div class="footer-line"></div>
          <p>
            Overall grade is based on responses compared with peers and best practices.
          </p>
          <p>
            Questions? Contact Loren Fox at 
            <a href="mailto:lfox@fuse-research.com">lfox@fuse-research.com</a>
          </p>
        </div>

      </div>

    </div>
    </body>
    </html>
    """


    html_file = os.path.join(SCORECARDS_DIR, f"retire_scorecard_{user}.html")
    pdf_path = os.path.join(SCORECARDS_DIR, f"retire_scorecard_{user}.pdf")

    
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html)


    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        page.goto(f"file:///{html_file}", wait_until="networkidle")

        page.pdf(
            path=pdf_path,
            format="A4",
            landscape=False,   # portrait
            print_background=True,
            scale=0.72         # key change
        )

        browser.close()

    if os.path.exists(html_file):
        os.remove(html_file)

    return pdf_path
