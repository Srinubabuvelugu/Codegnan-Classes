from database import createTables, AuthQueries

from flask import Flask, render_template, request, redirect, url_for, flash, session
import bcrypt
import uuid
import os

app = Flask(__name__)
app.secret_key = "Srinubabu@123423"

# create images folder
if not os.path.exists('static/images'):
    os.mkdir('static/images')

# create static/images/products folder
if not os.path.exists('static/images/products'):
    os.mkdir('static/images/products')





# ===============================================================
#                       Authentication Routes
# ===============================================================

#home route
@app.route('/')
def home():
    return render_template('home.html')

# login route
@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # check email exists or not
        status, user = AuthQueries.getUserData(email=email)
        print(user)
        if status == False:
            flash(user, 'err')
            return redirect('/register')
        
        #verify hashpassword
        verify_password = bcrypt.checkpw(password=password.encode('utf-8'),
                                hashed_password=user['hashpassword'].encode('utf-8'))
    
        if not verify_password:
            flash('Password incorrect')
            return redirect('/login')
        session.clear()
        session['id'] = user['userid']
        session['name'] = user['username']
        session['email'] = user['email']
        session['role'] = user['role']
        if session['role'] == 'admin':
            return redirect('/admin/dashboard')
        else:
            return redirect('/products')
        




        
# register route
@app.route('/register', methods = ['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # check password and confirm_password both same or not
        if password != confirm_password:
            print('Password missmatch', 'err')
            return redirect('/register')

        # check email exist or not
        status, msg = AuthQueries.getUserData(email=email)
        if status == True:
            print('Email Already exists', 'err')
            return redirect('/register')
        # generate hashpassword
        hash_password = bcrypt.hashpw(password=password.encode('utf-8'),
                                      salt = bcrypt.gensalt(4))
        
        # insert user data into users table
        status,msg = AuthQueries.insertUserRecord(name=name,
                                                  email=email,
                                                  password=hash_password,
                                                  phone=phone)
        # redirect to login page
        flash(msg, 'msg' if status else 'err')
        return redirect('/login')


        





# ===============================================================
#                       User Routes
# ===============================================================
# products route
@app.route('/products')
def products():
    if request.method == 'GET':
        return render_template('user/products.html')


# ===============================================================
#                       Admin Routes
# ===============================================================
# admin dashboard route
@app.route('/admin/dashboard')
def admin_dashboard():
    if request.method == 'GET':
        return render_template('admin/dashboard.html')


@app.route('/admin/products')
def admin_products():
    if request.method == 'GET':
        return render_template('admin/products.html', total_pages = 5,
                               page=3,
                               total = 25,
                               per_page= 7)

@app.route('/admin/products/add-product', methods = ['GET','POST'])
def admin_add_product():
    if request.method == 'GET':
        return render_template('admin/add_product.html')
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        new_categoy = request.form.get('new_categoy')
        category = category or new_categoy
        price = request.form.get('price')
        stock = request.form.get('stock')
        description = request.form.get('description')
        image = request.files.get('image')
        img_name = image.filename
        stored_name = str(uuid.uuid1()) + "_" + img_name
        img_path = os.path.join('static','images','products',stored_name)
        image.save(img_path)
        # store data in table
        
        
        
@app.route('/admin/category')
def admin_category():
    if request.method == 'GET':
        return render_template('admin/category.html')

@app.route('/admin/orders')
def admin_orders():
    if request.method == 'GET':
        return render_template('admin/orders.html')

@app.route('/admin/users')
def admin_users():
    if request.method == 'GET':
        return render_template('admin/users.html')
@app.route('/logout')
def logout():
    pass

#main
if __name__ == "__main__":
    print(createTables())
    app.run(debug=True)