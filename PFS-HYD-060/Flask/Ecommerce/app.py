from flask import Flask, redirect, render_template, url_for, session, request, flash

from database import createTables, AuthQueries

import bcrypt

app = Flask(__name__)

app.secret_key = "srinubad;ofihbgp;w[R0IGNKA;OEP8EYQ0POHIENLKE,G]"




# ==================================================================
#                       Authentication Routes
# ==================================================================
# home route
@app.route('/')
def home():
    return render_template('home.html')


# Register
@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template('register.html')
    if request.method == 'POST':
        # get register data from form
        # check email already exists or not
        # check password and confirm_password both are same or not
        # store user data
        # reirect to login

        name = request.form.get('name').strip()
        email = request.form.get('email').strip()
        phone = request.form.get('phone')
        password:str = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        status, user = AuthQueries.getUserData(email=email)
        if status == True:
            flash("Email Already Exists", 'err')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash("Password miss match", 'err')
            return redirect(url_for('register'))

        hash_password = bcrypt.hashpw(password=password.encode('utf-8'),
                                      salt=bcrypt.gensalt(4))

        status, msg = AuthQueries.createUserAccount(name=name, email=email,
                                                    password=hash_password,phone=phone)
        if status == False:
            flash(msg, 'err')
            return redirect(url_for('register'))        
        flash(msg, 'msg')
        return redirect(url_for('login'))
        


        
            
        





# login
@app.route("/login", methods = ['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        # get form data
        # check email exists or not
        # verify hash password
        # redirect user to products if 'user' role, otherwise 'admin' role dashboard
        email = request.form.get('email').strip()
        password = request.form.get('password').strip()
        status, user = AuthQueries.getUserData(email=email)
        if status == False:
            flash(user, 'err')
            return redirect('/login')
        verify_password_status = bcrypt.checkpw(password=password.encode('utf-8'),
                                    hashed_password=user['hashpassword'].encode('utf-8'))
        if verify_password_status == False:
            flash('Password incorrect','err')
            return redirect('/login')
        # store user data in session
        session['username'] = user['username']
        session['role'] = user['role']
        session['id'] = user['userid']
        session['email'] = email

        if user['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('products'))


# ===============================================================================
#                               User Routes
# ===============================================================================
@app.route('/products')
def products():
    return "User dashboard"


# ===============================================================================
#                               Admin Routes
# ===============================================================================
@app.route('/admin/dashboard')
def admin_dashboard():
    return "Admin dashboard"



# main
if __name__ == "__main__":
    print(createTables())
    app.run(debug=True)

