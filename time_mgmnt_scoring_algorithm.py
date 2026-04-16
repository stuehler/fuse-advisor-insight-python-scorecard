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




## Scoring from Loren
question_display = [[r'1. What percentage of your time is spent focused on clients -- including plan development, client servicing and client meetings -- per week?'],
                    [r'2. What percentage of your time is spent on business development and client acquisition per week?'],
                    [r'3. What percentage of your time is spent on investment research and portfolio management per week?'],
                    [r'4. What percentage of your time is spent on practice management and administrative activities per week?'],
                    [r'5. What single topic would you choose to spend more time on if you could?']]

question_scoring = [[28,'s',[119,0,"Clients need to see that you're spending time on them, so make that a focus.",'red'],
               [120,1,"Boost your time spent on client service to improve relationships and retention.",'yellow'],
               [121,2,"Good. Continue building deeper relationships so client support is part of your brand.",'green-light'],
               [122,2,"Good. Continue building deeper relationships so client support is part of your brand.",'green-light'],
               [123,3,"Client service is a defining strength, so continue using it to differentiate your practice.",'green-dark'],
               [124,3,"Client service is a defining strength, so continue using it to differentiate your practice.",'green-dark']],
        [29,'s',[128,0,"Make growth a bigger priority, at least to expand service and offset turnover.",'red'],
               [129,0,"Make growth a bigger priority, at least to expand service and offset turnover.",'red'],
               [130,1,"Up your focus on client acquisition to build a more consistent and scalable growth plan.",'yellow'],
               [131,2,"You prioritize business development; think about how to refine your approach.",'green-light'],
               [132,2,"You prioritize business development; think about how to refine your approach.",'green-light'],
               [134,3,"Business development is a real strength! Meanwhile, focus enough on client support.",'green-dark']],
        [30,'s',[138,0,"Consider making investments a more visible part of your practice and client value.",'red'],
               [139,1,"Take care to differentiate the value of your investment focus (or outsourcing).",'yellow'],
               [140,2,"So much time on investing makes sense if you can show your expertise to clients.",'green-light'],
               [141,2,"So much time on investing makes sense if you can show your expertise to clients.",'green-light'],
               [142,2,"So much time on investing makes sense if you can show your expertise to clients.",'green-light'],
               [143,3,"Make sure your value proposition reflects your big commitment to investments.",'green-dark']],
        [31,'s',[148,3,"Good work. Monitor your processes to protect your focus on clients and growth.",'green-dark'],
               [149,2,"You manage administrative time fairly well, but look for things to delegate or automate.",'green-light'],
               [150,1,"Better tech and prioritization should help you save time on these tasks.",'yellow'],
               [151,0,"These duties take up too much time. Consider part-time help and outsourcing.",'red'],
               [152,0,"These duties take up too much time. Consider part-time help and outsourcing.",'red']],
        [39,'s',[158,3,"Good! Retention and word-of-mouth are the foundations of a healthy practice.",'green-dark'],
               [160,1,"Tech-driven efficiency is important, but only pays off if it boosts client service.",'yellow'],
               [161,2,"Expanding non-investment capabilities will help keep clients and win new ones.",'green-light'],
               [162,0,"Marketing is necessary, but referrals / organic growth are surer bets for growth.",'red'],
               [164,3,"Good! Retention and word-of-mouth are the foundations of a healthy practice.",'green-dark']]]

grades = [[0,'C+',"Rebalance your time toward more client service and business development for more of a payoff."],
          [1,'C+',"Rebalance your time toward more client service and business development for more of a payoff."],
          [2,'B-',"Improve practice effectiveness by spending more of your time on clients and prospects."],
          [3,'B-',"Improve practice effectiveness by spending more of your time on clients and prospects."],
          [4,'B-',"Improve practice effectiveness by spending more of your time on clients and prospects."],
          [5,'B',"You allocate time fairly well; further cut admin work and limit investments to 30% of your time."],
          [6,'B',"You allocate time fairly well; further cut admin work and limit investments to 30% of your time."],
          [7,'B',"You allocate time fairly well; further cut admin work and limit investments to 30% of your time."],
          [8,'B',"You allocate time fairly well; further cut admin work and limit investments to 30% of your time."],
          [9,'B+',"Make sure the areas where you spend more time provide noticeable value for clients and prospects."],
          [10,'B+',"Make sure the areas where you spend more time provide noticeable value for clients and prospects."],
          [11,'B+',"Make sure the areas where you spend more time provide noticeable value for clients and prospects."],
          [12,'A-',"You manage your time well; maintain a strong balance across client service, growth, and investing."],
          [13,'A-',"You manage your time well; maintain a strong balance across client service, growth, and investing."],
          [14,'A',"You have an exceptional time allocation model; continue protecting this balance as your practice grows."],
          [15,'A',"You have an exceptional time allocation model; continue protecting this balance as your practice grows."]]




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
        total[total.questionid==28][['Response','You','All Advisors']]
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
        total[total.questionid==29][['Response','You','All Advisors']]
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
        total[total.questionid==30][['Response','You','All Advisors']]
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
        total[total.questionid==31][['Response','You','All Advisors']]
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
        total[total.questionid==39][['Response','You','All Advisors']]
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
    <title>Time Management</title>

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

      <div class="title">Survey: Time Management</div>

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


    html_file = os.path.join(SCORECARDS_DIR, f"time_scorecard_{user}.html")
    pdf_path = os.path.join(SCORECARDS_DIR, f"time_scorecard_{user}.pdf")

    
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
