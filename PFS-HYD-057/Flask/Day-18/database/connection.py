import mysql.connector as SQLC

def DatabaseConnection():
    try:
        db_config = SQLC.connect(
            host="localhost",
            user="root",
            password="root", # your mysql workbench password
            database="sns_management"
        )
        return db_config
    except Exception as e:
        return f"Something wrong in database/connection.py:{e}"
