from flask import Flask, render_template, request, redirect, session

from database import createTables, AuthQueries
import random
from utils import EmailTemaples, sendEmail
from utils import generateHashPassword,validateHashPassword

app = Flask(__name__)
app.secret_key = "Srinubabu@1123"

# home route
@app.route('/')
def home():
    return render_template('home.html')

# login 
@app.route("/login", methods = ['GET','POST'])
def login():
    # get request
    if request.method == 'GET':
        return render_template('login.html')
    # Post request
    if request.method =='POST':
        email = request.form.get('email')
        password = request.form.get('password')
        status, user = AuthQueries.checkEmailExists(email=email, data=True)
        if status == False:
            print(user)
            return redirect('/login')
        # match password
        status = validateHashPassword(password=password,
                                    hash_password=user['hashpassword'])
        if status == False:
            print("Password incorrect")
            return redirect('/login')
        # redicte to dash board page
        return redirect('/dashboard')






# register 
@app.route('/register', methods =['GET','POST'])
def register():
    # get request
    if request.method == 'GET':
        return render_template('register.html')
    # Post request
    if request.method == 'POST':
        name = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        print(name, email, password, confirm_password)
        # check password and confirm_password both are same or not
        # check email already exist or not
        # generate otp
        # send otp via email
        # redirect ti verify otp page
        if password != confirm_password:
            print("Password miss match")
            return redirect('/register')

        status, msg = AuthQueries.checkEmailExists(email=email)
        if status == True:
            print(msg)
            return redirect('/login')
        print(msg)

        otp = random.randint(1000,9999) # it generate 4 digit random number
        body = EmailTemaples.registerEmailTemplate(otp=otp, username=name)
        status, msg = sendEmail(to_email=email,
                                subject="SNS managment Register!!!",
                                body = body)
        if status == False:
            print(msg)
            return redirect('/register')
        session.clear()
        session['otp'] = otp
        session['username'] = name
        session['email'] = email
        session['password'] = password
        # redirect to verify otp page
        return redirect('/verify-otp')

@app.route('/verify-otp', methods=['GET','POST'])
def verifyotp():
    if request.method =='GET':
        return render_template('verifyotp.html')
    if request.method == "POST":
        otp = int(request.form.get('otp'))
        # match otp
        if otp!= session['otp']:
            print("OTP Incorrect")
            return redirect('/vefiry-otp')
        hash_password = generateHashPassword(password=session['password'])
        status, msg = AuthQueries.insertUserRecord(username=session['username'],
                                                   email=session['email'],
                                                   hash_password= hash_password)
        if status == False:
            print(msg)
            return redirect('/')
        print(msg)
        return redirect('/login')

        #store user data in database

    
# forgot - password
@app.route('/forgot-password', methods = ['GET','POST'])
def forgot_password():
    if request.method =='GET':
        return render_template('forgot_password.html')
        

# dashboard 
@app.route("/dashboard")
def dashboard():
    return "This dashboard page"

#main
if __name__ == "__main__":
    print(createTables())
    app.run(debug=True)
