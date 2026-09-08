from database.connection import DatabaseConnection


#check user alredy exist or not 
def getUserByEmail(email:str):
    try:
        db_config = DatabaseConnection()
        cusror = db_config.cursor()
        get_user_by_email = """SELECT * FROM USERS
                            WHERE EMAIL = %s;"""
        cusror.execute(get_user_by_email, (email,))
        user = cusror.fetchone() 
        cusror.close()
        db_config.close()
        if not user: # if record not found
            return True # user not exists
        else:
            return False # user exists
    except Exception as e:
        return f"Something wrong in database/utilityDB.py:getUserByEmail: {e}"
