from flask import Flask, request, redirect, render_template
from database import CreateTables, getUserByEmail
import random

from utils import sendEmail
from email_templates import EmailTemplates

# Flask instance
app = Flask(__name__)


# ======================================================
#                     Auth routes
# =====================================================
# home route
@app.route("/")
def home():
    return render_template('home.html')


# register route
@app.route('/register',methods = ['GET','POST'])
def register():
    if request.method =='GET':
        return render_template('register.html')
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        conform_password = request.form.get('conformpassword')
        # check password match
        print(password, type(password))
        print(conform_password, type(conform_password))
        if password != conform_password:
            # password miss match
            return redirect('/register')

        # check user already exists or not
        if getUserByEmail(email=email):
            # if user not exists
            # verify otp
            OTP = random.randint(1000,9999)
            # send otp email
            status, msg = sendEmail(to_email=email,
                                    subject="SNS- OTP Verification for Register",
                                    body=EmailTemplates.OTPEmailTemplate(
                                        username=username,
                                        otp=OTP
                                    ))
            if status == True:
                # reidect to verify otp page
                return msg
            else:
                return msg
        else:
            return "Email Already exists"


        # redirect to login page


# login route
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')


# main
if __name__ == "__main__":
    print(CreateTables())
    app.run(debug=True, port = 8000)