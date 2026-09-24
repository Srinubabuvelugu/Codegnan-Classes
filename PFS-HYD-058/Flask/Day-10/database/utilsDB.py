from database.connection import DatabaseConnection

# check user email already exists or not
def getUserDataByEmail(email:str):
    try:
        db_config = DatabaseConnection()
        cursor = db_config.cursor()
        query = "select * from users where email = %s;"
        cursor.execute(query, (email, ))
        user = cursor.fetchone()
        cursor.close()
        db_config.close()
        if user:
            return True, user
        else:
            return False, "Email Not exists"
    except Exception as e:
        return False, f"Something wrong in database/utilisDB-getUserByEmail():{e}"


# insert user record
def insertUserRecord(email:str, username:str, hash_password:str):
    try:
        db_config = DatabaseConnection()
        cursor = db_config.cursor()
        query = "insert into users(email, username, hashpassword) values(%s, %s, %s);"
        cursor.execute(query, (email,username, hash_password))
        db_config.commit()
        cursor.close()
        db_config.close()
        return True, "Registerd Successfully"
    except Exception as e:
        return False, f"Something wrong in database/utilisDB-insertUserRecord():{e}"
