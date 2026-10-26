from database.connection import DatabaseConnection



class AuthQueries:
    @staticmethod
    def checkEmailExists(email:str, data:bool=False):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)
            query = """select * from users where email = %s"""
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            db_config.close()
            cursor.close()
            if user:
                if data:
                    return True, user
                else:
                    return True, "Email Exists"
            else:
                return False, "Email Not Exists"

        except Exception as e:
            return False, f"Something wrong in \
        database/utilsDB.py-AuthQueries.checkEmailExists():{e}"


    @staticmethod
    def insertUserRecord(username:str,email:str,hash_password:str):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()
            query = """insert into users(username, email, hashpassword)
                        values(%s, %s, %s)"""
            cursor.execute(query, (username, email,hash_password))
            db_config.commit()
            db_config.close()
            cursor.close()
            return True, "Successfully Registered"

        except Exception as e:
            return False, f"Something wrong in \
        database/utilsDB.py-AuthQueries.insertUserRecord():{e}"

    # update password
    @staticmethod
    def updatePassword(email:str,hash_password:str):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()
            query = """update users set hashpassword = %s where email = %s"""
            cursor.execute(query, (hash_password, email))
            db_config.commit()
            db_config.close()
            cursor.close()
            return True, "Password updated Successfully"

        except Exception as e:
            return False, f"Something wrong in \
        database/utilsDB.py-NotesQueries.updatePassword():{e}"


# notes queries
class NotesQueries:
    @staticmethod
    def insertNotesRecord(userid:int, title:str, content:str):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()
            query = """insert into notes(userid, title, content) values(%s, %s, %s)"""
            cursor.execute(query, (userid, title, content))
            db_config.commit()
            db_config.close()
            cursor.close()
            return True, "Notes saved successfully"

        except Exception as e:
            return False, f"Something wrong in \
        database/utilsDB.py-NotesQueries.insertNotesRecord():{e}"

# get all notes
    @staticmethod
    def getAllNotes(userid:int, notesid:int=None):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)
            query = """select * from notes where userid = %s"""
            values = [userid]
            if notesid:
                query += " and notesid = %s"
                values.append(notesid)
                cursor.execute(query, tuple(values))
                notes = cursor.fetchone()
            else:
                query += " order by updated_at desc"
                cursor.execute(query, (userid,))
                notes = cursor.fetchall()
            db_config.close()
            cursor.close()
            return True, notes

        except Exception as e:
            return False, f"Something wrong in \
        database/utilsDB.py-NotesQueries.getAllNotes():{e}"

    # update notes
    @staticmethod
    def updateNotes(notesid:int, title:str, content:str):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)
            query = """update notes set title = %s, content = %s where notesid = %s"""
            cursor.execute(query, (title, content, notesid))
            db_config.commit()
            db_config.close()
            cursor.close()
            return True, "Notes Updated"

        except Exception as e:
            return False, f"Something wrong in \
        database/utilsDB.py-NotesQueries.updateNotes():{e}"


    # delete notes
    @staticmethod
    def deleteNotes(notesid:int):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)
            query = """delete from notes where notesid = %s"""
            cursor.execute(query, (notesid,))
            db_config.commit()
            db_config.close()
            cursor.close()
            return True, "Notes Deleted"

        except Exception as e:
            return False, f"Something wrong in \
        database/utilsDB.py-NotesQueries.deleteNotes():{e}"


# Files queries
class FilesQueries:
    @staticmethod
    def insertFileRecord(file_data:tuple[str|int]):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()
            query = """insert into files(userid, originalname, storedname, 
                    mimetype, size, filepath) values(%s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, file_data)
            db_config.commit()
            cursor.close()
            db_config.close()
            return True, "File Uploaded"
        except Exception as e:
            return False, f"Something wrong in \
                                    database/utilsDB.FilesQueries.insertFileRecord():{e}"

    @staticmethod
    def getAllFiles(userid:int, fileid:int=None):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)
            query = """select * from files where userid = %s"""
            values = [userid]
            if fileid:
                query += " and fileid = %s"
                values.append(fileid)
                cursor.execute(query, tuple(values))
                files = cursor.fetchone()
            else:
                query += " order by created_at desc"
                cursor.execute(query, (userid,))
                files = cursor.fetchall()
            db_config.close()
            cursor.close()
            return True, files

        except Exception as e:
            return False, f"Something wrong in \
        database/utilsDB.py-FilesQueries.getAllFiles():{e}"

    # delete File
    @staticmethod
    def deleteFile(fileid:int):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)
            query = """delete from files where fileid = %s"""
            cursor.execute(query, (fileid,))
            db_config.commit()
            db_config.close()
            cursor.close()
            return True, "File Deleted"

        except Exception as e:
            return False, f"Something wrong in \
        database/utilsDB.py-FilesQueries.deleteFile():{e}"