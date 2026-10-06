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
def getNotesByUserid(userid:int, notesid:int=None, title:str|None = None):
    try:
        db_config = DatabaseConnection()
        cursor = db_config.cursor(dictionary=True)
        query = """select * from notes where userid = %s"""
        values = [userid]
        if notesid:
            query += " and notesid = %s"
            values.append(notesid)
        if title:
            query += " and title like %s"
            values.append(f'%{title}%')
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

# update notes   
def updateNotes(title:str, content:str,userid:int,  notesid:int):
    try:
        db_config = DatabaseConnection()
        cursor = db_config.cursor()
        query = """update notes set title = %s, content = %s where userid = %s and notesid = %s;"""
        cursor.execute(query, (title, content, userid, notesid))
        db_config.commit()
        cursor.close()
        db_config.close()
        return True, "Notes Updated"
    except Exception as e:
        return False, f"Something wrong in database/utilisDB-updateNotes():{e}"

# update notes   
def deleteNotes(userid:int,  notesid:int):
    try:
        db_config = DatabaseConnection()
        cursor = db_config.cursor()
        query = """delete from notes where userid = %s and notesid = %s;"""
        cursor.execute(query, (userid, notesid))
        db_config.commit()
        cursor.close()
        db_config.close()
        return True, "Notes Deleted"
    except Exception as e:
        return False, f"Something wrong in database/utilisDB-deleteNotes():{e}"


def checkFileExists(userid:int, filename:str):
    try:
        db_config = DatabaseConnection()
        cursor = db_config.cursor()
        
        query = """select * from files where storedname = %s and userid = %s"""
        cursor.execute(query, (filename, userid))

        file = cursor.fetchone()
        cursor.close()
        db_config.close()
        if file: 
            return False, "File Already exists with the same name"
        return True, "File not exists"
    except Exception as e:
        return False, f"Something wrong in database/utilisDB-checkFileExists():{e}"


def insertFileMetaData(filedata:tuple[str|int]):
    try:
        db_config = DatabaseConnection()
        cursor = db_config.cursor()
        
        query = """insert into files(userid, orignalname, storedname,mimetype, size, path)
                values(%s,%s,%s, %s, %s, %s)"""
        cursor.execute(query, filedata)
        db_config.commit()
        cursor.close()
        db_config.close()
        return True, "File Saved"
    except Exception as e:
        return False, f"Something wrong in database/utilisDB-insertFileMetaData():{e}"

# get the files meta data by userid
#get the notes by userid
def getFilesByUserid(userid:int, fileid:int=None):
    try:
        db_config = DatabaseConnection()
        cursor = db_config.cursor(dictionary=True)
        query = """select * from files where userid = %s"""
        values = [userid]
        if fileid:
            query += " and fileid = %s"
            values.append(fileid)
        
        cursor.execute(query, tuple(values))
        if fileid:
            files = cursor.fetchone()
        else:
            files = cursor.fetchall()
        cursor.close()
        db_config.close()
        return True, files
    except Exception as e:
        return False, f"Something wrong in database/utilisDB-getFilesByUserid():{e}"
    
def deleteFiles(userid:int,  fileid:int):
    try:
        db_config = DatabaseConnection()
        cursor = db_config.cursor()
        query = """delete from files where userid = %s and fileid = %s;"""
        cursor.execute(query, (userid, fileid))
        db_config.commit()
        cursor.close()
        db_config.close()
        return True, "File Deleted"
    except Exception as e:
        return False, f"Something wrong in database/utilisDB-deleteFiles():{e}"
