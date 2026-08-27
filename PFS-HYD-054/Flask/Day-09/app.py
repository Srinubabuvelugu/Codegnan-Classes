from config import Config
import mysql.connector as sql

DBConfig=Config()

def getConnectionWithDB():
    db_host=DBConfig.db_host
    db_port=DBConfig.db_port
    db_user=DBConfig.db_user
    db_password=DBConfig.db_password
    db_name=DBConfig.db_name
    try:
        connection=sql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        return connection
    except:
        return 'Connection Failed'

def insertUserRecord(user_data):
    name=user_data['name']
    email=user_data['email']
    password_hash=user_data['password_hash']
    connection=getConnectionWithDB()
    if connection=='Connection Failed':
        return False
    else:
        cursor=connection.cursor()
        cursor.execute("INSERT INTO users (name,email,password_hash) values(%s,%s,%s)",(name,email,password_hash))
        connection.commit()
        cursor.close()
        connection.close()
        return True

data={
    'name':'Madhu',
    'email': 'madhu@codegnan.com',
    'password_hash': '1a2b3c4d'
}
print(insertUserRecord(data)) 
