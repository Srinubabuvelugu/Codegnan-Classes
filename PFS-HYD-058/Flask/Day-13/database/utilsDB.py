from database.connection import DatabaseConnection

# check user email already exists or not
def getUserDataByEmail(email:str):
    try:
        db_config = DatabaseConnection()
        cursor = db_config.cursor(dictionary=True)
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


# update password 
def updatePassword(email:str,hash_password:str):
    try:
        db_config = DatabaseConnection()
        cursor = db_config.cursor()
        query = "update users set hashpassword = %s where email = %s;"
        cursor.execute(query, (email,hash_password))
        db_config.commit()
        cursor.close()
        db_config.close()
        return True, "Password updated successfully"
    except Exception as e:
        return False, f"Something wrong in database/utilisDB-updatepassword():{e}"


def insertNotesRecord(title:str, content:str,userid:int):
    try:
        db_config = DatabaseConnection()
        cursor = db_config.cursor()
        query = """insert into notes(userid, title, content)
                values(%s, %s,%s);"""
        cursor.execute(query, (userid, title, content))
        db_config.commit()
        cursor.close()
        db_config.close()
        return True, "Notes Saved"
    except Exception as e:
        return False, f"Something wrong in database/utilisDB-inserNotesRecord():{e}"

#get the notes by userid
def getNotesByUserid(userid:int, notesid:int=None):
    try:
        db_config = DatabaseConnection()
        cursor = db_config.cursor(dictionary=True)
        query = """select * from notes where userid = %s"""
        values = [userid]
        if notesid:
            query += " and notesid = %s"
            values.append(notesid)
        query += " order by updated_at desc"
        cursor.execute(query, tuple(values))
        if notesid:
            notes = cursor.fetchone()
        else:
            notes = cursor.fetchall()
        cursor.close()
        db_config.close()
        return True, notes
    except Exception as e:
        return False, f"Something wrong in database/utilisDB-getBotesByUserid():{e}"
    
