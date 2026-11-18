from database.connection import DatabaseConnection

class AuthenticationQuaries:
    @staticmethod
    def getUserData(email:str):
        db_config = cursor = None
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)
            query = "select * from users where email = %s"
            cursor.execute(query,(email, ))
            user = cursor.fetchone()
            return user 
        except Exception as e:
            return f"Something wrong in \
                        database.utilsDB.AuthneticationQueries.getUserData():{e}"
        finally:
            if cursor: 
                cursor.close()
            if db_config: 
                db_config.close()