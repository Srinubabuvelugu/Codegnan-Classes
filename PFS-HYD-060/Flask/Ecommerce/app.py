from flask import Flask, redirect, render_template, url_for, session, request, flash

from database import createTables, AuthQueries, AdminQueries, UserQueries

import bcrypt
from werkzeug.utils import secure_filename
import uuid
import os

app = Flask(__name__)

app.secret_key = "srinubad;ofihbgp;w[R0IGNKA;OEP8EYQ0POHIENLKE,G]"



# create images folder in static if not exists
if not os.path.exists('static/images'):
    os.mkdir('static/images')

# create static/images/products folder
if not os.path.exists('static/images/products'):
    os.mkdir('static/images/products')


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
    _, products = AdminQueries.getAllProducts()
    _, categories = AdminQueries.getAllCategories()
    print(categories)
    return render_template('user/products.html', products=products, categories = categories)


@app.route('/products/<int:product_id>/details')
def product_details(product_id):
    _, product = AdminQueries.getAllProducts(product_id=product_id)
    return render_template('user/product_details.html', product= product)

@app.route('/cart')
def cart():
    cart_items = [{'cartid':1,
                   'productid':1,
                   'productname':'apple',
                   'category':'Fruits',
                   'storedpath':None,
                   'saleprice':50,
                   'quantity':5,
                   'subtotal':250
                   }]
    return render_template('user/cart.html', cart_items = cart_items)


# update cart qunatity
@app.route('/cart/<int:cartid>/update-quantity')
def update_cart_quantity(cartid):
    pass    

# checkout
@app.route('/checkout')
def checkout():
    pass    
@app.route('/products/<int:product_id>/add-to-cart', methods = ['POST'])
def add_to_cart(product_id):
    quanity = int(request.form.get('quantity'))
    status, msg = UserQueries.addCartItem(product_id=product_id,
                                        userid=session['id'],
                                        quantity=quanity)
    flash(msg,'msg' if status else 'err')
    return redirect('/products')

    

# ===============================================================================
#                               Admin Routes
# ===============================================================================
@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin/dashboard.html')


@app.route('/admin/products')
def admin_products():
    category = request.args.get('category')
    product_name  = request.args.get('search')
    page = int(request.args.get('page', 1))

    per_page = 7
    status, products = AdminQueries.getAllProducts(product_name=product_name,
                                                   category=category,
                                                   page_no=page,
                                                   per_page=per_page)
    print("*" * 50)   
    print(products)
    total = len(products)
    total_pages = len(products) // per_page + 1
    _, categories = AdminQueries.getAllCategories()
    return render_template('admin/products.html',
                           products = products,
                           categories = categories,
                           total_pages = total_pages,
                           page = page,
                           total = total,
                           per_page=per_page)     


@app.route('/admin/products/<int:product_id>/edit-product', methods = ['GET','POST'])
def admin_edit_product(product_id):
    if request.method == 'GET':
        # get the product info by using product_id
        _, product = AdminQueries.getAllProducts(product_id = product_id)
        _, categories = AdminQueries.getAllCategories()
        return render_template('admin/edit_product.html', 
                               product = product, categories = categories)
    if request.method == 'POST':
        product_name = request.form.get('name')
        category = request.form.get('category')
        
        price = request.form.get('price')
        stock = request.form.get('stock')
        description = request.form.get('description')
        image = request.files.get('image')
        if image:
            img_name = image.filename
            secure_img_name = secure_filename(img_name)
            unique_img_name = str(uuid.uuid1()) + "_" + secure_img_name

            # save image
            img_path = os.path.join('static', 'images', 'products', unique_img_name)

            image.save(img_path)
        else:
            _, product = AdminQueries.getAllProducts(product_id=product_id)
            unique_img_name = product['imgname']
            img_path = product['storedpath']
        data = (product_name, description, category,price, stock ,unique_img_name, img_path, product_id)
        status, msg = AdminQueries.updateProductRecord(product_data=data)
        flash(msg, 'msg' if status == True else 'err')
        return redirect(url_for('admin_products'))



        
    

    


@app.route('/admin/products/<int:product_id>/deactivate')
def admin_deactivate_product(product_id):
    pass



@app.route('/admin/products/add-product',methods = ['GET','POST'])
def admin_add_product():
    if request.method == 'GET':
        _, categories = AdminQueries.getAllCategories()
        print(categories)
        return render_template('admin/add_product.html', categories = categories)
    if request.method == 'POST':
        product_name = request.form.get('name')
        category = request.form.get('category')
        new_category = request.form.get('new_category')

        category = category or new_category
        
        price = request.form.get('price')
        stock = request.form.get('stock')
        description = request.form.get('description')
        image = request.files.get('image')

        img_name = image.filename
        secure_img_name = secure_filename(img_name)
        unique_img_name = str(uuid.uuid1()) + "_" + secure_img_name

        # save image
        img_path = os.path.join('static', 'images', 'products', unique_img_name)

        image.save(img_path)

        data = (product_name, description, category,price, stock ,unique_img_name, img_path)

        status, msg = AdminQueries.insertProductRecord(product_data=data)
        flash(msg, 'msg' if status == True else 'err')
        return redirect(url_for('admin_products'))



        

        

@app.route('/admin/categories')
def admin_category():
    pass     

@app.route('/admin/orders')
def admin_orders():
    pass     

@app.route('/admin/users')
def admin_users():
    # get all users 
    _, users = AdminQueries.getAllUsers()
    return render_template('admin/users.html', users =users)   


# user details
@app.route('/admin/users/int:user_id>/details')
def admin_user_details(user_id):
    pass

# user details
@app.route('/admin/users/int:user_id>/edit')
def admin_edit_user(user_id):
    pass

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# main
if __name__ == "__main__":
    print(createTables())
    app.run(debug=True)

