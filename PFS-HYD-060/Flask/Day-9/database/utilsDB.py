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