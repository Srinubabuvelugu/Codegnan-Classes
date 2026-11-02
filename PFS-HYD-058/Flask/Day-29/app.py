from database import createTables, AuthQueries, AdminQueries, UserQueries

from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
import bcrypt
import uuid
import os
from dotenv import load_dotenv
from decimal import Decimal
from functools import wraps

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

def login_required(role=None):
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args,**kwargs):
            if not session.get('id') or not session.get('role'):
                flash('Please log in to continue.','err')
                return redirect(url_for('login',next=request.path))
            if role and session.get('role') != role:
                abort(403)
            return fn(*args,**kwargs)
        return wrapped
    return decorator

def user_required(fn): 
    return login_required('user')(fn)
def admin_required(fn):
    return login_required('admin')(fn)
def money(v): 
    return Decimal(str(v))
def cart_summary(uid):
    _,items=UserQueries.getCartItems(uid)
    items=items if isinstance(items,list) else []
    subtotal=sum((money(i['subtotal']) for i in items),Decimal('0.00'))
    shipping=(subtotal*Decimal('0.01')).quantize(Decimal('0.01'))
    return items,subtotal,shipping,subtotal+shipping


def razorpay_client():
    try:
        key = os.getenv('RAZORPAY_KEY_ID')
        secret_key = os.getenv('RAZORPAY_KEY_SECRET')
        print(key, secret_key)
        if not secret_key or not key:
            return "Not able to get razorpay keys from .env"
        
        client = razorpay.Client(auth=(key, secret_key))
        print(client )
       
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

# update cart item quantity
@app.route('/cart/update-quantity/<int:cartid>',methods=['POST'])
@user_required
def update_cart_quantity(cartid):
    ok,msg=UserQueries.updateCartQuantity(cartid,request.form.get('quantity'),session['id'])
    flash(msg,'msg' if ok else 'err')
    return redirect(url_for('cart'))

@app.route('/cart/remove/<int:cartid>',methods=['POST'])
@user_required
def remove_cart_item(cartid):
    ok,msg=UserQueries.removeCartItem(cartid,session['id'])
    flash(msg,'msg' if ok else 'err')
    return redirect(url_for('cart'))


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
        session['total'] = total
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

        # Validate required fields
        if not all([name, phone, address, city, state, pincode, payment_method]):
            flash("All fields are required", "err")
            return redirect(url_for('checkout'))

        full_address = f"{name}, {phone}, {address}, {city}, {state}, {pincode}"
        userid = session['id']
        # COD Payment
        if payment_method == 'COD':

            status, result = UserQueries.createOrder(
                userid=userid,
                address=full_address,
                payment_method='COD'
            )
            if status == False:
                flash(result, 'err')
            flash("Order placed successfully", "msg")
            return redirect('/orders')
        # Razorpay Payment
        elif payment_method != 'RAZORPAY':
        
            flash("Invalid payment method", "danger")
            return redirect(url_for('checkout'))
        
        else:
            client = razorpay_client()

            if not client:
                return "Razorpay authentication failed"

            total = session['total']
            amount = int(round(total * 100))

            print("Total:", total)
            print("Amount in paise:", amount)

            if amount < 100:
                flash("Minimum order amount is ₹1", "err")
                return redirect(url_for('checkout'))

            rp = client.order.create(data={
                'amount': amount,
                'currency': 'INR',
                'receipt': f'user{session["id"]}-{os.urandom(4).hex()}'
            })

            status, order = UserQueries.createOrder(
                userid=session['id'],
                address=full_address,
                payment_method='RAZORPAY',
                razorpay_order_id=rp['id']
            )

            if not status:
                flash(str(order), 'err')
                return redirect(url_for('checkout'))

            session['pending_order_id'] = order['order_id']

            _, user = AuthQueries.getUserData(session['email'])

            return render_template(
                'user/payment.html',
                amount=amount,
                razorpay_key_id=os.getenv('RAZORPAY_KEY_ID'),
                razorpay_order=rp,
                user=user or {}
            )

@app.route('/verify-payment',methods=['POST'])
@user_required
def verify_payment():
    payment_id=request.form.get('razorpay_payment_id','')
    rp_order_id=request.form.get('razorpay_order_id','')
    signature=request.form.get('razorpay_signature','')
    oid=session.get('pending_order_id')
    client=razorpay_client()
    if not client or not all([payment_id,rp_order_id,signature,oid]):
        flash('Payment verification details are missing.','err')
        return redirect(url_for('payment_failed'))
    try:
        client.utility.verify_payment_signature({'razorpay_order_id':rp_order_id,'razorpay_payment_id':payment_id,'razorpay_signature':signature})
    except Exception:
        app.logger.warning('Razorpay signature verification failed')
        flash('Payment could not be verified.','err')
        return redirect(url_for('payment_failed'))
    ok,msg=UserQueries.markPaid(session['id'],oid,rp_order_id,payment_id)
    if not ok:
        flash(msg,'err')
        return redirect(url_for('payment_failed'))
    return redirect(url_for('payment_success'))
@app.route('/payment/success')
@user_required
def payment_success():
    oid=session.get('pending_order_id')
    ok,order=UserQueries.getOrderDetails(oid,session['id']) if oid else (False,None)
    session.pop('pending_order_id',None)
    return render_template('user/payment_success.html',order=order if ok else None)

@app.route('/payment/failed',methods=['GET','POST'])
@user_required
def payment_failed():
    if request.method == 'POST':
        oid=request.form.get('order_id') or session.get('pending_order_id')
        reason=request.form.get('reason','Payment failed')
        if oid:
            ok,msg=UserQueries.failPayment(session['id'],int(oid),reason)
            flash(msg,'msg' if ok else 'err')
        session.pop('pending_order_id',None)
        return redirect(url_for('payment_failed'))
    return render_template('user/payment_failed.html',message=request.args.get('message'))

@app.route('/payment/cancel',methods=['POST'])
@user_required
def payment_cancel():
    oid=session.get('pending_order_id')
    if oid:
        ok,msg=UserQueries.cancelPendingOrder(session['id'],oid)
        flash(msg,'msg' if ok else 'err')
        session.pop('pending_order_id',None)
    return redirect(url_for('viewcart'))

@app.route('/orders')
@user_required
def orders():
    _,rows=UserQueries.getOrders(session['id'])
    print(rows)
    return render_template('user/orders.html',orders=rows or [])
@app.route('/orders/<int:order_id>')
@user_required
def order_details(order_id):
    ok,order=UserQueries.getOrderDetails(order_id,session['id'])
    if not ok:
        abort(404)
    return render_template('user/order_details.html',order=order)
@app.route('/orders/<int:order_id>/invoice')
@user_required
def invoice(order_id):
    ok,order=UserQueries.getOrderDetails(order_id,session['id'])
    if not ok:
        abort(404)
    return render_template('user/invoice.html',order=order)
@app.route('/orders/<int:order_id>/invoice/download')
@user_required
def download_invoice(order_id):
    return redirect(url_for('invoice',order_id=order_id))
@app.route('/profile')
@user_required
def profile():
    _,user=UserQueries.getUser(session['id'])
    return render_template('user/profile.html',user=user or {})
@app.route('/profile/edit',methods=['GET','POST'])
@user_required
def edit_profile():
    from database.connection import DatabaseConnction
    if request.method=='GET':
        _,user=UserQueries.getUser(session['id'])
        return render_template('user/edit_profile.html',user=user or {})
    name=request.form.get('username','').strip()
    phone=request.form.get('phone','').strip()
    dob=request.form.get('dob','').strip()
    gender=request.form.get('gender','').strip()


    db=DatabaseConnction()
    cur=db.cursor()
    try:
        cur.execute('UPDATE users SET username=%s,phone=%s, dateofbirth=%s, gender=%s WHERE userid=%s',(name,phone,dob, gender, session['id']))
        db.commit()
        session['username']=name
        flash('Profile updated.','msg')
    except Exception:
        db.rollback()
        flash('Could not update profile.','err')
    finally:cur.close();db.close()
    return redirect(url_for('profile'))

@app.route('/change-password',methods=['GET','POST'])
@user_required
def change_password():
    pass

@app.errorhandler(403)
def forbidden(e):
    return render_template('base.html'),403
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