
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
import bcrypt

load_dotenv()

SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSKEY = os.getenv('SENDER_PASSKEY')
PORT = 587
SMTP_SERVER = "smtp.gmail.com"

def sendEmail(to_email:str, subject:str, body:str):
    
    msg =MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body,'plain'))
    print(1)
    try:
        print(11)
        print(to_email)
        server = smtplib.SMTP(SMTP_SERVER, PORT)
        print(2)
        server.starttls() # start server
        server.login(SENDER_EMAIL, SENDER_PASSKEY)
        print(3)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        print(4)
        server.quit()
        return True, "Email Send"
    except Exception as e:
        return False, f"Someting wrong in email sending:{e}"

# generate hash password
def generateHashPassword(password:str):
    hash_password = bcrypt.hashpw(password=password.encode('utf-8'),
                                  salt=bcrypt.gensalt(4)
                                  )
    return hash_password

# verify hash password
def verifyHashPassword(user_password:str, hash_password:str):
    status = bcrypt.checkpw(user_password.encode('utf-8'),hash_password)
    return status