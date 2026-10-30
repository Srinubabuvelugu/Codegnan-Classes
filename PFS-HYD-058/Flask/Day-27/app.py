from database import createTables, AuthQueries, AdminQueries, UserQueries

from flask import Flask, render_template, request, redirect, url_for, flash, session
import bcrypt
import uuid
import os
from dotenv import load_dotenv

import razorpay

load_dotenv()

app = Flask(__name__)
app.secret_key = "Srinubabu@123423"

# create images folder
if not os.path.exists('static/images'):
    os.mkdir('static/images')

# create static/images/products folder
if not os.path.exists('static/images/products'):
    os.mkdir('static/images/products')

def razorpay_client():
    try:
        key = os.getenv('RAZORPAY_KEY')
        secret_key = os.getenv('RAZORPAY_KEY_SECRET')
        client = razorpay.Client(auth=(key, secret_key))
        return client
    except Exception as e:
        return "Razorpay client config failed"





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
        #get products
        _, all_products = AdminQueries.getAllProducts()
        return render_template('user/products.html', products=all_products)

@app.route('/prodducts/<int:product_id>/details')
def product_details(product_id):

    _, product = AdminQueries.getAllProducts(product_id = product_id)
    return render_template('user/product_details.html', product=product)

# add to cart
@app.route('/products/<int:product_id>/add-to-cart',methods=['POST'])
def add_to_cart(product_id):
    quantity = request.form.get('quantity')
    _, msg = UserQueries.addToCart(product_id=product_id,
                                   user_id=session['id'],
                                   quantity=quantity)
    flash(msg)
    return redirect('/products')


# add to cart
@app.route('/cart')
def cart():
    _, items = UserQueries.cartItems(user_id=session['id'])
    print(items)
    sub_total = 0
    for item in items:
        sub_total += item['subtotal']

    shipping = sub_total * 0.01
    total = sub_total + shipping

    return render_template('user/cart.html',
                            cart_items = items,
                            subtotal = sub_total,
                            shipping = shipping,
                            total = total
                            )

# update cart qauntity
@app.route('/cart/<int:cartid>/update-quantity')
def update_cart_quantity(cartid):
    pass

#checkout 
@app.route('/checkout', methods = ['GET','POST'])
def checkout():
    if request.method == 'GET':
        _, items = UserQueries.cartItems(user_id=session['id'])
           
        sub_total = 0
        for item in items:
            sub_total += item['subtotal']
        
        shipping = sub_total * 0.01
        total = sub_total + shipping
        return render_template('user/checkout.html',
                                    cart_items = items,
                                    subtotal = sub_total,
                                    shipping = shipping,
                                    total = total
                                    )
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        pincode = request.form.get('pincode')
        payment_method = request.form.get('payment_method').upper()

        if payment_method == 'COD':
            # place order
            # add cart items to order details
            pass
            # 

        
    

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
        prodcut_name = request.args.get('search')
        category = request.args.get('category')
        status, products = AdminQueries.getAllProducts(productname=prodcut_name,
                                                    category=category)
        total_products_count = len(products)
        total_pages_count = total_products_count // 7 + 1

        return render_template('admin/products.html', 
                               products = products,
                               total_pages = total_pages_count,
                               page=1,
                               total = total_products_count,
                               per_page= 7)

@app.route('/admin/products/add-product', methods = ['GET','POST'])
def admin_add_product():
    if request.method == 'GET':
        _, categories = AdminQueries.getAllCategories()
        return render_template('admin/add_product.html', categories=categories)
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        new_categoy = request.form.get('new_category')
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
        data = (name, description, category, stock, price, stored_name, img_path)
        stutus, msg = AdminQueries.insertProductRecord(product_data=data)
        flash(msg)
        return redirect(url_for('admin_products'))



@app.route('/admin/products/<int:product_id>/edit-product', methods = ['GET', 'POST'])
def admin_edit_product(product_id):
    if request.method == 'GET':
        _, product = AdminQueries.getAllProducts(product_id=product_id)
        _, categories = AdminQueries.getAllCategories()
        print(categories)
        return render_template('admin/edit_product.html', 
                               product = product,
                               categories = categories)
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        
        price = request.form.get('price')
        stock = request.form.get('stock')
        description = request.form.get('description')

        image = request.files.get('image')
        img_name = image.filename
        
        if img_name != "":
            
            stored_name = str(uuid.uuid1()) + "_" + img_name
            img_path = os.path.join('static','images','products',stored_name)
            image.save(img_path)
        else:
            _, product = AdminQueries.getAllProducts(product_id=product_id)
            print(product)
            stored_name = product['imgname']
            img_path = product['storedpath']
            print(stored_name, img_path)
        
        # store data in table
        data = (name, description, category, stock, price, stored_name, img_path, product_id)
        print(data)
        # update product data in database
        status, msg = AdminQueries.updateProductRecord(product_data=data)

        flash(msg)
        return redirect(url_for('admin_products'))
    

    

@app.route('/admin/products/<int:product_id>/deactivate')
def admin_deactivate_product(product_id):
    pass
        
        
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
        # get all users for users table
        _, users = AdminQueries.getAllUsers()
        return render_template('admin/users.html', users= users)

@app.route('/admin/users/<int:user_id>/details')
def admin_user_details(user_id):
    pass


@app.route('/admin/users/<int:user_id>/edit')
def admin_edit_user(user_id):
    pass

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

#main
if __name__ == "__main__":
    print(createTables())
    app.run(debug=True)