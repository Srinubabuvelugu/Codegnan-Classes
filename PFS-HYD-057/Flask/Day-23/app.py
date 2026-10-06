from database import createTables

from flask import Flask, render_template, redirect, request, flash, url_for, session

from database import AuthQueries
import bcrypt

app = Flask(__name__)

app.secret_key = "Srinubabu@1234"

# =============================================
#               Auth Routes
# =============================================
#home
@app.route('/')
def home():
    return render_template('home.html')



#register
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            flash('Password miss match', 'err')
            return redirect('/register')
        # check email exists in database
        status, user = AuthQueries.checkEmailExists(email=email)
        if status == True:
            flash("Email Alredy Exist",'err')
            return redirect('/register')
        # generate hash password
        # insert user data into table
        hash_password = bcrypt.hashpw(password=password.encode('utf-8'),
                                      salt=bcrypt.gensalt(4))
        # if you want you can register user by otp verification
        data = (name, email,hash_password, phone)
        status, msg = AuthQueries.insertUserRecord(user_data=data)
        if status == False:
            flash(msg, 'err')
            return redirect('/register')
        flash(msg, 'msg')
        return redirect('/login')
        

    
#login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        status, user = AuthQueries.checkEmailExists(email=email)
        if status == False:
            flash(user, 'err')
            return redirect('/login')
        valid_password = bcrypt.checkpw(
            password=password.encode('utf-8'),
            hashed_password=user['hashpassword'].encode('utf-8')
        )
        if not valid_password:
            flash('Check your credentials','err')
            return redirect('/login')
        session.clear()
        session['id'] = user['userid']
        session['username'] = user['username']
        session['email'] = user['email']
        session['role'] = user['role']
        role = session['role']

        if role == 'admin':
            return redirect('/admin/dashboard')
        else:
            return redirect('/dashboard')



# admin dahsboard
@app.route('/admin/dashboard')
def admin_dashboard():
    return "Admin Dashboard"


# dahsboard
@app.route('/dashboard')
def dashboard():
    return "User Dashboard"

# main
if __name__ == "__main__":
    print(createTables())
    app.run(debug=True)