from flask import Flask, render_template, request, redirect, session, url_for, flash


from database import createTables, AuthenticationQuaries, NotesQueries
from utils import sendEmail, generateOTP, generateHashPassword, verifyHashPassword

# flask instance
app = Flask(__name__)
app.secret_key = "aieflbjkadfbhvlenh iulrnhgw; oeurhgq;iorhgj 4l5iu4"
# ======================================================================
#                              Authentication Routes
# ======================================================================
@app.route('/')
def home():
    return render_template('home.html')


# login route
@app.route('/login', methods =['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = AuthenticationQuaries.getUserData(email=email)
        hash_password = user.get('hashpassword')
        if not hash_password:
            print("Email Not Exists")
            return redirect('/login')
        status = verifyHashPassword(password=password, hash_password=hash_password)
        if status == False:
            print("Incorrect Password")
            return redirect('/login')
        # strore user data in session
        session.clear()
        session['id'] = user['userid']
        session['email'] =email
        session['username'] = user['username']
        return redirect('/dashboard')




# register route
@app.route('/register', methods =['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        print(username, email, password, confirm_password)

        # check password and confirm_password both are same or not
        if password != confirm_password:
            print("Password missmatch")
            return redirect('/register')

        # check user email already exists in database or not
        user = AuthenticationQuaries.getUserData(email= email)
        if isinstance(user, dict) and user.get('userid'):
            print("Email Already Exists")
            return redirect('/register')

        # generate otp 
        otp = generateOTP()
        # send otp via email
        content = f"""Hi {username},

Welcome to SNM!  
To complete your registration, please use the One-Time Password (OTP) below:

🔑 OTP: {otp}

This code will expire in **10 minutes** for security purposes.

If you did not request this code, please ignore this email.

Thank you for joining us,  
The SNM Team"""

        status, msg = sendEmail(to_email=email,
                                subject="OTP Verification for SNM Register!!!",
                                body =content )
        if status == False:
            print(msg)
            return redirect('/register')
        # store user data in session
        session.clear()
        session['otp'] = otp
        session['email'] = email
        session['password'] = password
        session['username'] = username
        # redirect to verify otp
        return redirect('/verifyotp')


@app.route('/verifyotp', methods=['GET','POST'])
def verify_otp():
    if request.method == 'GET':
        return render_template('verifyotp.html')
    if request.method == 'POST':
        otp = request.form.get('otp', type=int)
        # if otp is incorrect
        if otp != session['otp']:
            print("Incorrect OTP")
            return redirect('/verifyotp')
        # otp correct and store user data in database
        hash_password = generateHashPassword(password=session['password'])
        msg = AuthenticationQuaries.createUserAccount(name=session['username'],
                                                      email=session['email'],
                                                      password=hash_password)
        print(msg)
        return redirect('/login')




@app.route('/dashboard')
def dashboard():
    if request.method == 'GET':
        return render_template('dashboard.html')

@app.route('/dashboard/notes')
def mynotes():
    # get user note from databse
    all_notes = NotesQueries.getNotesByUserId(userid=session['id'])
    return render_template('/notes.html', notes = all_notes)

@app.route('/dashboard/notes/add-notes', methods = ['GET','POST'])
def addnotes():
    if request.method == 'GET':
        return render_template('addnotes.html')
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        msg = NotesQueries.addNotes(userid=session['id'], title=title, content=content)
        flash(msg)
        return redirect(url_for('mynotes'))



# main
if __name__ == "__main__":
    print(createTables())
    app.run(debug=True, port = 5001)
