
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv


SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSKEY = os.getenv('SENDER_PASSKEY')
PORT = 587
SMTP_SERVER = "smtp.gmail.com"

def sendEmail(to_email:str, subject:str, body:str):
    msg =EmailMessage()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body,'plain'))
    try:
        server = smtplib.SMTP(SMTP_SERVER, PORT)
        server.starttls() # start server
        server.login(SENDER_EMAIL, SENDER_PASSKEY)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        return True, "Email Send"
    except Exception as e:
        return False, f"Someting wrong in email sending:{e}"
