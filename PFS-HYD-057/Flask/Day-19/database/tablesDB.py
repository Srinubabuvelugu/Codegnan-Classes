from database.connection import DatabaseConnection


def CreateTables():
    try:
        db_config = DatabaseConnection()
        cursor = db_config.cursor()
        user_table_query = """CREATE TABLE IF NOT EXISTS USERS(
                            USERID BIGINT AUTO_INCREMENT,
                            USERNAME VARCHAR(50) NOT NULL,
                            EMAIL VARCHAR(50) NOT NULL UNIQUE,
                            HASHPASSWORD VARCHAR(255) NOT NULL,
                            IS_ACTIVE BOOLEAN DEFAULT FALSE,
                            CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            PRIMARY KEY(USERID)
                        );"""
        notes_table_query = """CREATE TABLE IF NOT EXISTS NOTES(
                            NOTESID BIGINT AUTO_INCREMENT,
                            USERID BIGINT,
                            TITLE VARCHAR(255) NOT NULL,
                            CONTENT TEXT NOT NULL,
                            CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                            PRIMARY KEY(NOTESID),
                            FOREIGN KEY(USERID) REFERENCES USERS(USERID) ON DELETE CASCADE
                        );"""
        files_table_query = """CREATE TABLE IF NOT EXISTS FILES(
                            FILEID BIGINT AUTO_INCREMENT,
                            USERID BIGINT,
                            ORIGINALNAME VARCHAR(255),
                            STOREDNAME VARCHAR(255),
                            MIMETYPE VARCHAR(255),
                            SIZE INT,
                            FILEPATH VARCHAR(255),
                            CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            PRIMARY KEY(FILEID),
                            FOREIGN KEY(USERID) REFERENCES USERS(USERID) ON DELETE CASCADE
                        );"""
        cursor.execute(user_table_query)
        cursor.execute(notes_table_query)
        cursor.execute(files_table_query)
        cursor.close()
        db_config.close()
        return "Tables Created"
        


    except Exception as e:
        return f"Something wrong in database/tablesDB:{e}"
