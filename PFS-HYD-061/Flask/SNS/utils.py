import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import random
import bcrypt

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSKEY = os.getenv('SENDER_PASSKEY')

def sendEmail(to_email:str, subject:str, body:str):
    print(SENDER_EMAIL, SENDER_PASSKEY)
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



def generateOTP():
    return random.randint(10000, 99999)

def generateHashPassword(password:str):
    hash = bcrypt.hashpw(password=password.encode('utf-8'),
                         salt = bcrypt.gensalt())
    return hash

def verifyHashPassword(password:str, hash_password:str):
    status = bcrypt.checkpw(password=password.encode('utf-8'),
                            hashed_password= hash_password.encode('utf-8'))
    return status