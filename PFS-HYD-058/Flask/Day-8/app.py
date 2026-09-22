from flask import Flask, render_template, request, redirect, flash

from database import createTables

from database import getUserDataByEmail
from utils import SendEmail, EmailTemapltes

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
        status, msg = SendEmail(to_email=email,
                                subject="SNS Registation OTP",
                                body=EmailTemapltes.OTPEmailTempalte(username=name))
        if status == False:
            flash(msg)
            return redirect('/register')
        flash(msg)
        # redirect tot Verifyotp page
        return redirect('/verifyotp')







#verify otp route
@app.route('/verifyotp', methods = ['GET','POST'])
def verifyotp():
    if request.method == 'GET':
        return render_template('verifyotp.html')

# Login Route
@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')



# main
if __name__ == "__main__":
    print(createTables())
    app.run(debug=True)
