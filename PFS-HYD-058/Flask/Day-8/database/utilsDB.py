from database.connection import DatabaseConnection

# check user email already exists or not
def getUserDataByEmail(email:str):
    try:
        db_config = DatabaseConnection()
        cursor = db_config.cursor()
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
