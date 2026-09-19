import mysql.connector as SQLC

def DatabaseConnection():
    try:
        db_config = SQLC.connect(
            host = "locahost",
            user = "root",
            password = "root", # your sql password,
            database = "sns_management1"
        )
        return db_config
    except Exception as e:
        return f"Something wrong in database/connection.py:{e}"