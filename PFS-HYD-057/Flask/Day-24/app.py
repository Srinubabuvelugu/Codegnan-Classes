from database import createTables

from flask import Flask, render_template, redirect, request, flash, url_for, session

from database import AuthQueries, AdminQueries
import bcrypt
from werkzeug.utils import secure_filename
import os

import uuid
app = Flask(__name__)

app.secret_key = "Srinubabu@1234"

if not os.path.exists('static'):
    os.mkdir('static')

if not os.path.exists('static/images'):
    os.mkdir('static/images')

if not os.path.exists('static/images/products'):
    os.mkdir('static/images/products')
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



# dahsboard
@app.route('/dashboard')
def dashboard():
    return "User Dashboard"

# ================================================================
#                       Admin Routes
# ================================================================


# admin dahsboard
@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin/dashboard.html')

@app.route('/admin/products')
def admin_products():
    # get all products
    return render_template('admin/products.html', 
                           total_pages = 10, 
                           page =2, 
                           total=100, 
                           per_page=7)

# add product
@app.route('/admin/products/add', methods =['GET','POST'])
def admin_add_product():
    if request.method == 'GET':
        return render_template('admin/add_product.html')

    if request.method == 'POST':
        product_name = request.form.get('name')
        category = request.form.get('category')
        new_category = request.form.get('new_category')
        category = category or new_category
        price = request.form.get('price')
        stock = request.form.get('stock')
        description =  request.form.get('description')
        img = request.files.get('image')
        img_name = img.filename
        img_secure_name = secure_filename(img_name)
        stored_name = str(uuid.uuid1()) + img_secure_name
        img_path = os.path.join('static','images','products', stored_name)
        img.save(img_path) # save image
        print(product_name, category, price, stock, description, img_name, stored_name)

        data = (product_name, description,category,stock,price, stored_name,img_path)
        status, msg = AdminQueries.insertProductRecord(product_data=data)
        flash(msg, 'msg' if status else 'err')
        return redirect(url_for('admin_products'))



@app.route('/admin/categorey')
def admin_category():
    pass


@app.route('/admin/orders')
def admin_orders():
    pass

@app.route('/admin/users')
def admin_users():
    pass



@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# main
if __name__ == "__main__":
    print(createTables())
    app.run(debug=True)