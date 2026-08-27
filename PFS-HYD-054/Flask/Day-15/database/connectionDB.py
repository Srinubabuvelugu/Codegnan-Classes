import mysql.connector as SQLC


def DatabaseConection():
    db_config = SQLC.connect(
        host = "localhost",
        user = 'root',
        password = 'root',
        database = 'sns_management'
    )
    return db_config