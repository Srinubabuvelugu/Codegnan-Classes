
from database.connection import DatabaseConnection
from psycopg2.extras import RealDictCursor


class AuthQueries:

    # get user data using email
    @staticmethod
    def getUserData(email: str):
        db_config = cursor = None
        try:
            db_config = DatabaseConnection()

            if db_config is None:
                return False, "Database connection failed"

            cursor = db_config.cursor(cursor_factory=RealDictCursor)

            query = """SELECT * FROM users WHERE email = %s"""
            cursor.execute(query, (email,))

            user = cursor.fetchone()

            if user:
                return True, user
            else:
                return False, "Email Not Exists"

        except Exception as e:
            return False, f"Something wrong in database/utilsDB.AuthQueries.getUserData(): {e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    # create account
    @staticmethod
    def createUserAccount(name: str, email: str, password: str, phone: str):
        db_config = cursor = None
        try:
            db_config = DatabaseConnection()

            if db_config is None:
                return False, "Database connection failed"

            cursor = db_config.cursor(cursor_factory=RealDictCursor)

            query = """
                INSERT INTO users(username, email, hashpassword, phone)
                VALUES (%s, %s, %s, %s)
            """

            cursor.execute(query, (name, email, password, phone))
            db_config.commit()

            return True, "Account created"

        except Exception as e:
            if db_config:
                db_config.rollback()

            return False, f"Something wrong in database/utilsDB.AuthQueries.createUserAccount(): {e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()
