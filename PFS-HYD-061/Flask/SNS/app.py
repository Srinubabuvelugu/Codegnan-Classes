from flask import Flask, render_template, request, redirect


from database import createTables, AuthenticationQuaries
from utils import sendEmail, generateOTP, generateHashPassword, verifyHashPassword

# flask instance
app = Flask(__name__)

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
        # redirect to verify otp
        return msg





# main
if __name__ == "__main__":
    print(createTables())
    app.run(debug=True, port = 5001)
