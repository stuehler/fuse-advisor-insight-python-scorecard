import os
from dotenv import load_dotenv
import time
import smtplib
import ssl
import get_survey_data as data
from email.message import EmailMessage

from dotenv import load_dotenv

# Email settings
SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))  # 587 for STARTTLS, 465 for SSL
SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
EMAIL_FROM = os.environ.get("EMAIL_FROM")

topic = {13:'Time Management',
             62:'AI',
             63:'UHNW Investors',
             64:'the Convergence of Wealth and Retirement',
             66:'Private Markets',
             67:'Crypto'}

email_subject = ['Your Advisor Insight Scorecard Is Ready! See How You Compare']

def getEmail(participant,mail_link,path):
    folder_path = os.path.dirname(os.path.abspath(__file__))
    if mail_link == 0:
        ## html email
        file_name = 'email2_html.html'
        subject_line = email_subject[0]

        file_path = os.path.join(folder_path, file_name)

        with open(file_path, "r", encoding="utf-8") as f:
            email = f.read()

        first_name = participant[1].split()[0]
        email = email.replace("{{name}}", first_name)

        ## text email
        file_name_text = 'email2_text.txt'

        file_path_text = os.path.join(folder_path, file_name_text)

        with open(file_path_text, "r", encoding="utf-8") as f:
            email_text = f.read()

        first_name = participant[1].split()[0]
        email_text = email_text.replace("{{name}}", first_name)
    else:
        ## html email
        file_name = 'email1_html.html'
        subject_line = email_subject[0]
        token = data.getToken(mail_link,participant[2])

        file_path = os.path.join(folder_path, file_name)

        with open(file_path, "r", encoding="utf-8") as f:
            email = f.read()

        first_name = participant[1].split()[0]
        email = email.replace("{{name}}", first_name)  
        email = email.replace("{{topic}}", topic[mail_link])
        email = email.replace("{{invite}}", token[0])

        ## text email
        file_name_text = 'email1_text.txt'

        file_path_text = os.path.join(folder_path, file_name_text)

        with open(file_path_text, "r", encoding="utf-8") as f:
            email_text = f.read()

        first_name = participant[1].split()[0]
        email_text = email_text.replace("{{name}}", first_name)
        email_text = email_text.replace("{{topic}}", topic[mail_link])
        email_text = email_text.replace("{{invite}}", token[0])

    sendEmail(email, email_text, subject_line, path, participant)


def sendEmail(email, email_text, subject_line, path, participant):
    
    msg = EmailMessage()
    msg["From"] = EMAIL_FROM
    msg["To"] = participant[2]
    msg["Subject"] = subject_line

    body = f"""{email_text}"""

    html_body = f"""{email}"""
    
    msg.set_content(body)
    msg.add_alternative(html_body,subtype="html")

    attachment_path = path

    with open(attachment_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="pdf",
            filename=os.path.basename(attachment_path)
        )

    context = ssl.create_default_context()

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)