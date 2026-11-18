import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv


SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = ?
SENDER_PASSKEY = ?

def sendEmail(to_email:str, subject:str, body:str):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # SMTP configuration
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls() # server start
        server.login(SENDER_EMAIL, SENDER_PASSKEY)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        return True, "Email send to register email address"
    
    except Exception as e:
        return False, f'Something wrong while sending an email:{e}'

