from database.connection import DatabaseConnction


# check user exist of not 
def getUserByEmail(email:str, data:bool = False):
    try:
        db_config = DatabaseConnction()
        cursor = db_config.cursor(dictionary=True)

        get_user_by_email = """select * from users where email = %s;"""
        cursor.execute(get_user_by_email, (email,))

        user = cursor.fetchone()
        cursor.close()
        db_config.close()
        if user:
            if data == True:
                return True, user
        else:
            return False, "Email not Found"
    except Exception as e:
        return False, f"Somthing Wrong in database/authDB.py-getUserByEmail():{e}"
    
        
        