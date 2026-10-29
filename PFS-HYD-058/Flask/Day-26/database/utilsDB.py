from database.connection import DatabaseConnction


class AuthQueries:
    @staticmethod
    def getUserData(email:str):
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)
            query = """select * from users where email = %s"""
            cursor.execute(query, (email, ))
            user = cursor.fetchone()
            cursor.close()
            db_config.close()
            if user:
                return True, user
            else:
                return False, "Email Not Exists"
        except Exception as e:
            return False, f"Something wrong in \
                    database/utilsDB.AuthQueries.getUserData():{e}"
    # insert user record
    @staticmethod
    def insertUserRecord(name:str, email:str, phone:str, password:str):
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)
            query = """insert into users(username, email, hashpassword, phone)
                        values(%s, %s, %s, %s)"""
            cursor.execute(query, (name,email,password,phone))
            db_config.commit()
            cursor.close()
            db_config.close()
            return True, "Successfully account created"
        except Exception as e:
            return False, f"Something wrong in \
                    database/utilsDB.AuthQueries.insertUserRecord():{e}"