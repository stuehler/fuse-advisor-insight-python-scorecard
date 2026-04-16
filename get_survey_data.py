import os
from dotenv import load_dotenv
import time
import pandas as pd
from sqlalchemy import create_engine, text
import urllib

load_dotenv()  # Loads variables from .env into os.environ

SQL_SERVER   = os.environ.get("SQL_SERVER")
SQL_DATABASE = os.environ.get("SQL_DATABASE")
SQL_USERNAME = os.environ.get("SQL_USERNAME")
SQL_PASSWORD = os.environ.get("SQL_PASSWORD")
SQL_DRIVER   = os.environ.get("SQL_DRIVER", "ODBC Driver 17 for SQL Server")


SQL_QUERY = os.environ.get(
    "SQL_QUERY",
    "select surveyid, a.questionid, b.multipleChoiceAnswerId, multipleChoiceQuestionTypeId, a.text as question, b.text as answer, b.shorttext as shortAnswer, \
    b.displayOrder as displayorder,d.userid, aum, submitted as completed \
    from multiple_choice_questions a inner join multiple_choice_answer_choices b on a.questionId = b.questionId \
    inner join multiple_choice_responses d on d.multiplechoiceanswerid = b.multiplechoiceanswerid \
    inner join advisor_profile f on f.userid = d.userid inner join survey_questions g on g.questionid = a.questionid \
    where surveyid in (13,62,63,64,66,67) \
    order by surveyid,d.userid,b.displayorder"
)

CREATE_TOKEN = os.environ.get(
    "CREATE_TOKEN",
    "EXEC uspCreateInvitation  @email = :email, @survey_id = :survey, @expires_at = null"
)


GET_TOKEN = os.environ.get(
    "GET_TOKEN",
    "select token from invitations where email = :email and survey_id = :survey"
)

TRACK_STATUS = os.environ.get(
    "TRACK_STATUS",
    "EXEC uspTrackScorecardStatus  @email = :email, @surveyid = :survey"
)


def get_engine():
    engine = create_engine(
        f"mssql+pyodbc://{SQL_USERNAME}:{SQL_PASSWORD}@{SQL_SERVER}/{SQL_DATABASE}"
        f"?driver={SQL_DRIVER.replace(' ', '+')}"
    )
    return engine

engine = get_engine()


def run_query() -> pd.DataFrame | None:
    with engine.connect() as conn:
        df = pd.read_sql(text(SQL_QUERY), conn)
        return df if not df.empty else None
    

def getData():
    while True:
        try:
            result = run_query()
            return result
        except Exception as exc:
            print(f"[ERROR] {exc}")
            

def create_token(survey: int, email: str) -> tuple[str] | None:
    with engine.connect() as conn:
        conn.execute(text(CREATE_TOKEN), {"email": email, "survey": survey})
        conn.commit()

        result = conn.execute(text(GET_TOKEN), {"email": email, "survey": survey})
        row = result.fetchone()
        return row if row else None

def getToken(survey: int, email: str) -> list[str] | None:
    while True:
        try:
            return create_token(survey, email)
        except Exception as exc:
            print(f"[ERROR] {exc}")
            break

def scorecardStatus(participant: tuple[int,str,str,int]) -> None:
      with engine.connect() as conn:
        conn.execute(text(TRACK_STATUS),{"email":participant[2],"survey":participant[3]})
        conn.commit()