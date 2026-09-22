
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import random

load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv('email')
SENDER_PASSKEY = os.getenv('passkey')

def SendEmail(to_email:str, subject:str, body:str):
    msg = MIMEMultipart()
    msg['To'] = to_email
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg.attach(MIMEText(body, 'plain'))
    try:
        #establish server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        # start server
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSKEY) # login to server
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        return True, "Mail Send to register email"

    except Exception as e:
        return False, f"Something wrong while sending an email:{e}"


# OTP generate
def generate_otp():
    otp = random.randint(1000, 9999)
    return otp

class EmailTemapltes:
    @staticmethod
    def OTPEmailTempalte(username:str="user"):
        otp = generate_otp()
        template = f""" Dear {username},
        Thank for choosing SNS app to manage your notes and files.
        
        your Registation OTP: {otp}
        
        If your not register for this app simply ingnore this email and
        don't share OTP with any one.
        
        
        Regards
        SNS App"""
        return template