from database.connection import DatabaseConnection


#check user alredy exist or not 
def getUserByEmail(email:str, data=False):
    try:
        db_config = DatabaseConnection()
        cusror = db_config.cursor(dictionary=True)
        get_user_by_email = """SELECT * FROM USERS
                            WHERE EMAIL = %s;"""
        cusror.execute(get_user_by_email, (email,))
        user = cusror.fetchone() 
        cusror.close()
        db_config.close()
        if data==True:
            if user:
                return True, user
            else:
                return False, "Check your user credentials"
        
            
        if not user: # if record not found
            return True # user not exists
        else:
            return False # user exists
    except Exception as e:
        return f"Something wrong in database/utilityDB.py:getUserByEmail: {e}"


# insert user data into table
def insertUserRecord(name:str, email:str, hash_pasword:bytes):
    try:
        db_config = DatabaseConnection()
        cusror = db_config.cursor()
        insert_record_query = """INSERT INTO USERS(USERNAME,EMAIL, HASHPASSWORD, IS_ACTIVE)
                                VALUES(%s, %s, %s, %s);"""
        cusror.execute(insert_record_query, (name,email,hash_pasword, 1))
        db_config.commit()
        cusror.close()
        db_config.close()
        return True, "User Successfully Registred"
    except Exception as e:
        return False, f"Something wrong in database/utilityDB.py:getUserByEmail: {e}"


# insert notes into table

def insertNotesRecord(userid:int, title:str, content:str):
    try:
        db_config = DatabaseConnection()
        cusror = db_config.cursor()
        insert_record_query = """INSERT INTO NOTES(USERID,TITLE, CONTENT)
                                VALUES(%s, %s, %s);"""
        cusror.execute(insert_record_query, (userid, title, content))
        db_config.commit()
        cusror.close()
        db_config.close()
        return True, "Notes Added"
    except Exception as e:
        return False, f"Something wrong in database/utilityDB.py:insertNotesRecord: {e}"



# get Notes by userid
def getNotesByUserid(userid:int):
    try:
        db_config = DatabaseConnection()
        cusror = db_config.cursor(dictionary=True)
        get_notes_query = """select * from notes where userid = %s 
                            order by updated_at desc;"""
        cusror.execute(get_notes_query, (userid,))
        notes = cusror.fetchall()
        cusror.close()
        db_config.close()
        return True, notes
    except Exception as e:
        return False, f"Something wrong in database/utilityDB.py:getNotesByUserid: {e}"


# get notes by notes id
def getNotesByNotesid(notesid:int):
    try:
        db_config = DatabaseConnection()
        cusror = db_config.cursor(dictionary=True)
        get_notes_query = """select * from notes where notesid = %s;"""
        cusror.execute(get_notes_query, (notesid,))
        notes = cusror.fetchone()
        cusror.close()
        db_config.close()
        return True, notes
    except Exception as e:
        return False, f"Something wrong in database/utilityDB.py:getNotesByNotesid: {e}"

