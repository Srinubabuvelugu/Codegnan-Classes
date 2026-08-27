from dotenv import load_dotenv
import os

load_dotenv()

class Config():
    db_host=os.getenv('DB_HOST')
    db_port=os.getenv('DB_PORT')
    db_user=os.getenv('DB_USER')
    db_password=os.getenv('DB_PASSWORD')
    db_name=os.getenv('DB_NAME')
    from_email=os.getenv('FROM_EMAIL')
    email_app_password=os.getenv('EMAIL_APP_PASSWORD')