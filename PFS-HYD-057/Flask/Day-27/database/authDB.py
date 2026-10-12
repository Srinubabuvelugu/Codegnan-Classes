from database.connection import DatabaseConnction


class AuthQueries:
    @staticmethod
    def checkEmailExists(email:str):
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)
            query = """select * from users where email = %s"""
            cursor.execute(query, (email,))
            data = cursor.fetchone()
            if data:
                return True, data
            else:
                return False, "Email Not Exists"
        except Exception as e:
            return False,f"Something wrong in database/authDB-checkEmailExists():{e}"

    @staticmethod
    def insertUserRecord(user_data:tuple[str|int]):
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)
            query = """insert into users(username, email,hashpassword, phone)
                    values(%s, %s, %s, %s)"""
            cursor.execute(query,user_data)
            db_config.commit()
            cursor.close()
            db_config.close()
            return True, "Succesfully Registerd"
        except Exception as e:
            return False,f"Something wrong in database/authDB-checkEmailExists():{e}"

