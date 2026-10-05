from database.connection import DatabaseConnction
from werkzeug.security import generate_password_hash


def getUserByEmail(email: str, data: bool = True):
    db = DatabaseConnction()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute('SELECT * FROM users WHERE email=%s AND is_active=1', (email,))
        user = cur.fetchone()
        return (True, user) if user else (False, 'Email not found')
    except Exception as e:
        return False, str(e)
    finally:
        cur.close()
        db.close()


def createUser(username, email, password, phone=None):
    """Create a normal customer account in the users table."""
    db = DatabaseConnction()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute('SELECT userid FROM users WHERE email=%s', (email,))
        if cur.fetchone():
            return False, 'Email is already registered'

        cur.execute(
            '''INSERT INTO users(username,email,hashpassword,role,phone,is_active)
               VALUES(%s,%s,%s,'user',%s,1)''',
            (username, email, generate_password_hash(password), phone or None)
        )
        user_id = cur.lastrowid
        db.commit()
        return True, user_id
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        cur.close()
        db.close()
