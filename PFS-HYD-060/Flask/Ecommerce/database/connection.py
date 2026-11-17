
import psycopg2
import os

def DatabaseConnection():
    try:
        db_config = psycopg2.connect(
            host=os.environ.get("DB_HOST"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            dbname=os.environ.get("DB_NAME"),
            port=os.environ.get("DB_PORT", 5432),
            sslmode="require"
        )
        return db_config

    except Exception as e:
        return f"Something wrong in Database/connection.py: {e}"
