from database.connection import DatabaseConnection



class AuthQueries:
    @staticmethod
    def checkEmailExists(email:str):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()
            query = """select * from users where email = %s"""
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            db_config.close()
            cursor.close()
            if user:
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