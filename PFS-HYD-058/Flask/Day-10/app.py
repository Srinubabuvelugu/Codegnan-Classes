from flask import Flask, render_template, request, redirect, flash, session

from database import createTables

from database import getUserDataByEmail, insertUserRecord
from utils import SendEmail, EmailTemapltes, generate_otp, generateHashPassword, verifyHashPassword

app = Flask(__name__)
app.secret_key="Srinubabu@123"

# home route
@app.route("/")
def home():
    return render_template('home.html')


# Register route
@app.route('/register', methods = ['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        print(email, name, password, confirm_password)

        # check password and confirm_password both are same or not
        if password != confirm_password:
            flash("Password doesn't match", "err")
            return redirect('/register')
        #check user email already exists or not
        status, msg = getUserDataByEmail(email=email)
        if status == True:
            flash("User Email Already Exists", "err")
            return redirect('/register')
        # send OTP via Email
        otp = generate_otp()
        status, msg = SendEmail(to_email=email,
                                subject="SNS Registation OTP",
                                body=EmailTemapltes.OTPEmailTempalte(otp=otp,username=name))
        if status == False:
            flash(msg)
            return redirect('/register')
        flash(msg)
        # redirect tot Verifyotp page
        # store user data in session
        session.clear()
        session['name'] = name
        session['email'] = email
        session['password'] = password
        session['otp'] = otp
        return redirect('/verifyotp')







#verify otp route
@app.route('/verifyotp', methods = ['GET','POST'])
def verifyotp():
    if request.method == 'GET':
        return render_template('verifyotp.html')
    if request.method == 'POST':
        otp = request.form.get('otp')
        # match otp
        if int(otp) == session['otp']:
            #store user data in table
            # generate hash password
            hash_password = generateHashPassword(password=session['password'])
            status, msg = insertUserRecord(email=session['email'],
                                           username=session['name'],
                                           hash_password=hash_password)
            if status == False:
                flash(msg,"err")
                print(msg)
                return redirect('/register')
            else:
                flash(msg, "msg")
                print(msg)
                return redirect('/login')
        else:
            flash("Invalid OTP", "err")
            return redirect('/verifyotp')



# Login Route
@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        # check email exists in table or not
        status, user = getUserDataByEmail(email=email)
        if status == False:
            flash(user, "err")
            print(user)
            return redirect('/login')
        # if user exist verify password
        status = verifyHashPassword(hash_password=user['hashpassword'],
                                    password=password)
        if status == False:
            flash("Check login credentials", 'err')
            print("Check login credentials")
            return redirect('/login')
        # redirect to dashboard 
        session.clear()
        session['id'] = user['userid']
        session['email'] = email
        session['name'] = user['username']
        return redirect('/dashboard')


# dashboard route
@app.route('/dashboard')
def dashboard():
    if "id" not in session:
        return redirect('/login')
    if request.method == 'GET':
        return render_template('dashboard.html', name = session['name'])



# main
if __name__ == "__main__":
    print(createTables())
    app.run(debug=True)
