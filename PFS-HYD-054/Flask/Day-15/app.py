from config import Config, emailTemplates

import mysql.connector as sql
import random
import smtplib
from email.message import EmailMessage
from flask import Flask,render_template,redirect,url_for,request,session
import bcrypt

from itsdangerous import URLSafeTimedSerializer, BadSignature, TimedSerializer

app=Flask(__name__)
app.secret_key="CodeGn@n123"

serializer = URLSafeTimedSerializer(app.secret_key)

DBConfig=Config()
from_email="dantavaidya@gmail.com" #DBConfig.from_email
email_app_password= "yfaqlvniiahfgdsn" #DBConfig.email_app_password


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
            host="localhost",
            user='root',
            password='root',
            database='students_notes_manager'
        )
        # print(connection)
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
    # print(connection)
    if connection=='Connection Failed':
        return False
    else:
        cursor=connection.cursor()
        cursor.execute("SELECT * from users where email=%s",(email,))
        data=cursor.fetchone()
        print(data)
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
    print(message)
    with smtplib.SMTP("smtp.gmail.com",587) as server:
        print(server)
        server.starttls()
        server.login(from_email,email_app_password)
        server.send_message(message)
    return True


def SendEmail(subject:str, to_email:str,body:str):
    message=EmailMessage()
    message['Subject']=subject
    message['From']=from_email
    message['To']=to_email
    message.set_content(body)
    # print(message)
    with smtplib.SMTP("smtp.gmail.com",587) as server:
        print(server)
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
    if password is None or len(password)<3:
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
            print(is_duplicate)
            if is_duplicate==False: # duplicate ledu
                
                # if there is no account
                # convert password to hash value
                OTP=generateOTP()
                password_hash=generateHash(user_data['password'])
                # inserting this data into table
                name=user_data['name']
                email=user_data['email']
                status=insertUserRecord({
                    'name':name,
                    'email':email,
                    'password_hash':password_hash
                })
                print("Insert record status:", status)
                # status of insertion
                
                if status==True:
                    session['username']=email
                    session['otp']=OTP
                    print(1)
                    SendEmail(subject="Verify Your Registration – Notes Management",
                              to_email=email,
                              body = emailTemplates.send_otp_template(username= name, otp =OTP)
                    )
                                               
                    return redirect('/verify')
                    #return render_template('register.html',res='Registration Successfully Completed')
                else:
                    # insertion is failed
                    return render_template('register.html',err='Registration Failed')
            else: # duplicate undi
                print(3)
                return render_template('register.html',err="Account Already Exist")
    
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template('login.html')
    elif request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        # we have to check account existed or not
        user_data = {
            'email':email
        }
        
        record = readUserRecordByEmail(user_data=user_data)
        print("login data:",record)
        if record:
            print(0)
            # if data exist, then we have to check is_verified is True
            if record['is_verified'] == True:
                print(1)
                # if account existed and verified, compare password
                login_status = bcrypt.checkpw(password.encode('utf-8'),
                                            record['password_hash'].encode('utf-8'))
                # print(login_status)
                print(2)
                if login_status:
                    print("Login status:",login_status)
                    # create a session, inside session we have to store email
                    session['email'] = email
                    session['id'] = record['id']
                    session['name'] = record['name']
                    print(3)
                    return redirect('/dashboard')
                else:
                    return redirect('/login')
            else:
                 return redirect('/login')
        else:
            return redirect('/login')



# reset password token generation
def resetPasswordTokenGenerate(email):
    token = serializer.dumps(
        email,
        salt="reset-password"
    )
    return token


# forgot password route
@app.route("/forgot_password",methods = ['GET','POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template("forgot_password.html")
    if request.method == 'POST':
        email = request.form.get('email', None)

        # check weather the email exists in database or not
        data = {'email':email}
        record = readUserRecordByEmail(user_data=data)
        if 'id' in record:
            # send email
            
            # generate token
            token = resetPasswordTokenGenerate(email=email)
            # reset password url 
            reset_url = url_for('reset_password', token=token, _external = True)
            email_status = SendEmail(
                subject="Reset Password -SNS",
                to_email=email,
                body=emailTemplates.send_reset_password_template(
                    username = record['name'],
                    url = reset_url,
                    time = 10
                ))
            if email_status:
                return render_template("forgot_password.html", msg = "Email send to you mail")
            else:
                return render_template("forgot_password.html", error = "Unable to send email")
        else:       
            return render_template("forgot_password.html", error = "Enter Valied email")

# validate token
def validateToken(token):
    try:
        data = serializer.loads(
            token,
            salt = "reset-password",
            max_age=600
        )
        return data
    except BadSignature: # if token changed
        return "Invalid"
    except TimedSerializer: # if token time out
        return "Timeout"


# reset password route
@app.route('/reset-password/<string:token>', methods = ['GET', 'POST'])
def reset_password(token):
    token_status = validateToken(token=token)
    if token_status == 'Invalid':
        return render_template('fotgot_password.html',error = "Invalid URL")
    elif token_status == "Timeout":
        return render_template("forgot_password.html", error = "URL Expired")
    email = token_status
    if request.method == 'GET':
        return render_template('reset_password.html', token=token)
    # post request
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        conform_password = request.form.get('conform_password')
        if new_password == conform_password:
            # generate hash password
            password_hash = generateHash(text=new_password)
            # update password in database
            data = {'email':email, 'new_password':password_hash}
            update = updatePasswordByIdorEmail(user_data=data)
            if update:
                # redirect to login page
                return redirect('/login')
            else:
                return render_template('reset_password.html')
        else:
            return render_template('reset_password.html', error = "Password Miss match")
    








@app.route('/dashboard')
def dashboard():
    # if user data not in session redirect to login page
    if "id" not in session:
        return redirect("/login")
    
    return render_template('dashboard.html', username = session['name'])

@app.route('/verify',methods=['GET','POST'])
def verify():
    if request.method=='GET':
        return render_template('verify.html')
    elif request.method=='POST':
        otp=request.form['otp']
        otp=int(otp)
        if otp==session['otp']:
            is_verify=True
            updateIsVerifiedByIdorEmail({'email':session['username'],'is_verified':is_verify})
            return redirect('/login')
        else:
            return render_template('verify.html',err="Invalid OTP")


#profile route
@app.route("/user/profile", methods=['GET'])
def profile():
    if "id" not in session:
        redirect("/login")
    name = session['name']
    email = session['email']
    return render_template("profile.html", email = email, name=name)


# logout route
@app.route("/logout", methods = ['GET'])
def logout():
    # if id in session:
    session.pop('id', None)
    session.pop('name', None)
    session.pop('email', None)
    return redirect('/login')

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

# Registration Flow
# User has to click on Get Started
# Register Page
# Name, Email, Password, Confirm Password and Submit
# verifyDuplicateEmail() - if account not existed
# generate otp
# send email with otp
# redirect to verify.html
# enter the otp received on email
# the otp entered with session otp
# if they are matched, it redirects to login
# if they are not matched, it redirects with a message