import mysql.connector as SQLC

def DatabaseConnction():
    try:
        db_config = SQLC.connect(
            host = 'localhost',
            user = 'root',
            password = 'root1234', # your Mysql Password
            database = "ecommerce"
        )
        return db_config
    except Exception as e:
        return f"Something wrong in Database/conncetion.py: {e}"