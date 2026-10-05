import mysql.connector as SQLC


def DatabaseConnection():
    try:
        db_config = SQLC.connect(
            host = "localhost",
            user = "root",
            password = "root", # your sql password
            database = "ecommerce1"
        )
        return db_config
    except Exception as e:
        return f"Something wrong in Database Connection:{e}"