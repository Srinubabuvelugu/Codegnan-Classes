from config import Config
import mysql.connector as sql
import random
import smtplib
from email.message import EmailMessage
from flask import Flask,render_template,redirect,url_for,request
import bcrypt

app=Flask(__name__)

DBConfig=Config()
from_email=DBConfig.from_email
email_app_password=DBConfig.email_app_password

# Encode - Str to Bytes
# Decode - Bytes to Str
# gensalt is used to generate a key
# how many rounds this key to iterate
# gensalt(4)
# b'$12' 
# $==$
# Login email==email,password==password
def generateHash(text):
    btext=text.encode('utf-8')
    cipher_text=bcrypt.hashpw(btext,bcrypt.gensalt(4))
    return cipher_text.decode('utf-8')
    print(cipher_text,len(cipher_text))

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
        try:
            cursor=connection.cursor()
            cursor.execute("INSERT INTO users (name,email,password_hash) values(%s,%s,%s)",(name,email,password_hash))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except:
            print('Data cant be inserted')
            return False

def readUserRecords():
    connection=getConnectionWithDB()
    if connection=='Connection Failed':
        return False
    else:
        cursor=connection.cursor()
        cursor.execute("SELECT * from users")
        data=cursor.fetchall()
        records=[]
        for record in data:
            temp={}
            temp['id']=record[0]
            temp['name']=record[1]
            temp['email']=record[2]
            temp['password_hash']=record[3]
            temp['is_verified']=record[4]
            temp['created_at']=record[5]
            records.append(temp)
        cursor.close()
        connection.close()
        return records

def readUserRecordByEmail(user_data):
    email=user_data['email']
    connection=getConnectionWithDB()
    if connection=='Connection Failed':
        return False
    else:
        cursor=connection.cursor()
        cursor.execute("SELECT * from users where email=%s",(email,))
        data=cursor.fetchone()
        try:
            record={
                'id':data[0],
                'name':data[1],
                'email':data[2],
                'password_hash':data[3],
                'is_verified':data[4],
                'created_at':data[5]
            }
            cursor.close()
            connection.close()
            return record
        except:
            cursor.close()
            connection.close()
            return 'No record'

def readUserRecordById(user_data):
    id=user_data['id']
    connection=getConnectionWithDB()
    if connection=='Connection Failed':
        return False
    else:
        cursor=connection.cursor()
        cursor.execute("SELECT * from users where id=%s",(id,))
        data=cursor.fetchone()
        try:
            record={
                'id':data[0],
                'name':data[1],
                'email':data[2],
                'password_hash':data[3],
                'is_verified':data[4],
                'created_at':data[5]
            }
            cursor.close()
            connection.close()
            return record
        except:
            cursor.close()
            connection.close()
            return 'No record'

def updateNameByIdorEmail(user_data):
    query_filter=''
    try:
        id=user_data['id']
        query_filter='id'
    except:
        email=user_data['email']
        query_filter='email'
    new_name=user_data['new_name']
    connection=getConnectionWithDB()
    if connection=='Connection Failed':
        return False
    else:
        cursor=connection.cursor()
        if query_filter=='id':
            query="UPDATE users SET name=%s WHERE id=%s"
            values=(new_name,id)
        elif query_filter=='email':
            query="UPDATE users SET name=%s WHERE email=%s"
            values=(new_name,email)
        cursor.execute(query,values)
        connection.commit()
        cursor.close()
        connection.close()
        return True


def updatePasswordByIdorEmail(user_data):
    query_filter=''
    try:
        id=user_data['id']
        query_filter='id'
    except:
        email=user_data['email']
        query_filter='email'
    new_password=user_data['new_password']
    connection=getConnectionWithDB()
    if connection=='Connection Failed':
        return False
    else:
        cursor=connection.cursor()
        if query_filter=='id':
            query="UPDATE users SET password_hash=%s where id=%s"
            values=(new_password,id)
        elif query_filter=='email':
            query="UPDATE users SET password_hash=%s where email=%s"
            values=(new_password,email)
        cursor.execute(query,values)
        connection.commit()
        cursor.close()
        connection.close()
        return True

def updateIsVerifiedByIdorEmail(user_data):
    query_filter=''
    try:
        id=user_data['id']
        query_filter='id'
    except:
        email=user_data['email']
        query_filter='email'
    is_verified=user_data['is_verified']
    connection=getConnectionWithDB()
    if connection=='Connection Failed':
        return False
    else:
        cursor=connection.cursor()
        if query_filter=='id':
            query="UPDATE users SET is_verified=%s WHERE id=%s"
            values=(is_verified,id)
        elif query_filter=='email':
            query="UPDATE users SET is_verified=%s WHERE email=%s"
            values=(is_verified,email)
        cursor.execute(query,values)
        connection.commit()
        cursor.close()
        connection.close()
        return True

def generateOTP():
    otp=random.randint(1000,9999)
    return otp

def sendOTPviaEmail(to_email,otp):
    message=EmailMessage()
    message['Subject']='OTP Notification'
    message['From']=from_email
    message['To']=to_email
    message.set_content(
        f"Your OTP is {otp}"
    )
    with smtplib.SMTP("smtp.gmail.com",587) as server:
        server.starttls()
        server.login(from_email,email_app_password)
        server.send_message(message)
    return True

def validateDataForRegister(user_data):
    errors=[]
    name=user_data['name']
    email=user_data['email']
    password=user_data['password']
    confirm_password=user_data['confirm_password']
    if name is None or len(name)<2:
        errors.append('Invalid Name')
    if email is None or len(email)<5:
        errors.append('Invalid Email')
    if password is None or len(password)<5:
        errors.append('Invalid Password')
    if password != confirm_password:
        errors.append('Passwords not matched')

    return errors

def verifyDuplicateEmail(user_data):
    record=readUserRecordByEmail(user_data)
    if (record=='No record'):
        return False # duplicate ledu
    else:
        return True # duplicate undi

@app.route('/')
def home():
    return render_template('index.html')

# Either through GET, POST you can reach this endpoint
@app.route('/register',methods=['GET','POST'])
def register():
    # request is GET {Browser}
    if (request.method=='GET'):
        # Displaying HTML FILE
        return render_template('register.html')
    # request is HTML FORM POST
    elif (request.method=='POST'):
        # Step-1: Input User Data
        name=request.form['name']
        email=request.form['email']
        password=request.form['password']
        confirm_password=request.form['confirm_password']
        user_data={
            "name":name,
            "email":email,
            "password":password,
            "confirm_password":confirm_password
        }
        # Step-2: Validate the User Data
        errors=validateDataForRegister(user_data)
        if len(errors)>0:
            # If errors, we have to display errors
            return render_template('register.html',errors=errors)
        else:
            # If no errors, we have to start BL
            # Whether account exist on this email
            is_duplicate=verifyDuplicateEmail(user_data)
            if is_duplicate==False: # duplicate ledu
                # if there is no account
                # convert password to hash value
                password_hash=generateHash(user_data['password'])
                # inserting this data into table
                name=user_data['name']
                email=user_data['email']
                status=insertUserRecord({
                    'name':name,
                    'email':email,
                    'password_hash':password_hash
                })
                # status of insertion
                if status==True:
                    return render_template('register.html',res='Registration Successfully Completed')
                else:
                    # insertion is failed
                    return render_template('register.html',err='Registration Failed')
            else: # duplicate undi
                return render_template('register.html',err="Account Already Exist")
    
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if (__name__=="__main__"):
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )

# REGISTRATION FLOW
# User -> Register.html <-> Registration Form -> POST <-> Python -> Collecting Data -> Validating -> Verifying -> Password to Password Hash <-> MySQL Table 

# HTML <-> Python <-> MySQL

# @app.route('/register',methods=['GET','POST'])
# def register():
#     if request.method=='GET':
#         renderHTMLPage()
#     elif request.method=='POST':
#         collectUserData()
#         validateUserData()
#         displayErrors()
#         status=verifyAccountExist()
#         if status:
#             insertRecord()
#         else:
#             displayErrorMessage()