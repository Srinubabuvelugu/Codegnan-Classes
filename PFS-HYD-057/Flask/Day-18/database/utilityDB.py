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
def getNotesByUserid(userid:int, title:str=None, limit:int=None):
    try:
        db_config = DatabaseConnection()
        cusror = db_config.cursor(dictionary=True)

        get_notes_query = """select * from notes where userid = %s"""
        values = [userid]
        if title:
            get_notes_query += " and title like %s"
            values.append(f"%{title}%")

        get_notes_query += " order by updated_At desc"
        if limit:
            get_notes_query += " limit %s;"
            values.append(limit)


        cusror.execute(get_notes_query, tuple(values))
        notes = cusror.fetchall()
        cusror.close()
        db_config.close()
        return True, notes
    except Exception as e:
        return False, f"Something wrong in database/utilityDB.py:getNotesByUserid: {e}"


# get notes by notes id
def getNotesByNotesid(notesid:int, userid:int):
    try:
        db_config = DatabaseConnection()
        cusror = db_config.cursor(dictionary=True)
        get_notes_query = """select * from notes where notesid = %s and userid = %s;"""
        cusror.execute(get_notes_query, (notesid,userid))
        notes = cusror.fetchone()
        cusror.close()
        db_config.close()
        if notes:
            return True, notes
        else:
            return False, "Notes id not found"
    except Exception as e:
        return False, f"Something wrong in database/utilityDB.py:getNotesByNotesid: {e}"



# update notes by notes id
def updateNotesByNotesid(notesid:int, userid:int, title:str, content:str):
    try:
        db_config = DatabaseConnection()
        cusror = db_config.cursor()
        update_notes_query = """update notes set title = %s, content = %s
                            where notesid = %s and userid = %s;"""
        cusror.execute(update_notes_query, (title, content, notesid,userid))
        db_config.commit()
        cusror.close()
        db_config.close()

        return True, "Notes Updated"
      
    except Exception as e:
        return False, f"Something wrong in database/utilityDB.py:getNotesByNotesid: {e}"

# delete notes by notes id
def deleteNotesByNotesid(notesid:int, userid:int):
    try:
        db_config = DatabaseConnection()
        cusror = db_config.cursor()
        delete_notes_query = """delete from notes 
                            where notesid = %s and userid = %s;"""
        cusror.execute(delete_notes_query, (notesid,userid))
        db_config.commit()
        cusror.close()
        db_config.close()

        return True, "Notes Deleted"
      
    except Exception as e:
        return False, f"Something wrong in database/utilityDB.py:deleteNotesByNotesid: {e}"




# check file duplicate exists or not
def checkFileDuplicate(filename:int, userid:int):
    try:
        db_config = DatabaseConnection()
        cusror = db_config.cursor()
        get_file_query = """select * from files 
                            where storedname = %s and userid = %s;"""
        cusror.execute(get_file_query, (filename,userid))
        file = cusror.fetchone()
        cusror.close()
        db_config.close()
        if file:
            return False, "File already exists"
        else:
            return True, "File Not Exists"
      
    except Exception as e:
        return False, f"Something wrong in database/utilityDB.py:checkFileDuplicate: {e}"


# insert file metadata record 
def insertFileMetaDataRecord(filemetadata:tuple[str]):
    try:
        db_config = DatabaseConnection()
        cusror = db_config.cursor()
        insert_record_query = """insert into files
                            (userid, originalname, storedname, mimetype, size, filepath)
                            values(%s, %s, %s, %s, %s, %s);"""
        cusror.execute(insert_record_query,filemetadata)
        db_config.commit()
        cusror.close()
        db_config.close()
        return True, "File saved"
      
    except Exception as e:
        return False, f"Something wrong in database/utilityDB.py:insertFileMetaDataRecord(): {e}"


# get files by userid
def getFilesByUserid(userid:int):
    try:
        db_config = DatabaseConnection()
        cusror = db_config.cursor(dictionary=True)
        get_files_query = """select * from files where userid = %s 
                            order by created_at desc;"""
        cusror.execute(get_files_query, (userid,))
        files = cusror.fetchall()
        cusror.close()
        db_config.close()
        return True, files
    except Exception as e:
        return False, f"Something wrong in database/utilityDB.py:getFilesByUserid(): {e}"


# get total files and notes count

def getFileAndNotesCount(userid:int):
    try:
        db_config = DatabaseConnection()
        cusror = db_config.cursor()
        get_files_count = """select count(*) from files where userid = %s;"""
        cusror.execute(get_files_count, (userid,))
        files_count = cusror.fetchone()[0]
        cusror.execute("select count(*) from notes where userid = %s;", (userid,))
        notes_count = cusror.fetchone()[0]
        cusror.close()
        db_config.close()
        return notes_count, files_count
    except Exception as e:
        return False, f"Something wrong in database/utilityDB.py:getFilesAndNotesCount(): {e}"



# 