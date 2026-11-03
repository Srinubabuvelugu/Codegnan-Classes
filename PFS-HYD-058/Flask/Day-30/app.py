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
    ok, order = UserQueries.getOrderDetails(
        order_id, session['id']
    )
    print(order)

    if not ok:
        abort(404)

    return render_template('user/invoice.html', order=order, order_items=order['items'] or [])


@app.route('/orders/<int:order_id>/invoice/download')
@user_required
def download_invoice(order_id):

    ok, order = UserQueries.getOrderDetails(
        order_id, session['id']
    )
    print(order)

    if not ok:
        abort(404)

    return render_template('user/invoice.html', order=order, order_items=order['items'] or [])
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
# ============================================================
# ADMIN ROUTES
# Replace your existing admin routes section with this code.
#
# Required imports/dependencies in app.py:
# from flask import request, render_template, redirect, url_for, flash, abort
# from pathlib import Path
# from decimal import InvalidOperation
# from werkzeug.utils import secure_filename
# import uuid
# from database.adminDB import AdminQueries
#
# This code also expects your existing:
# app, admin_required, money, ALLOWED_EXTENSIONS
# ============================================================


# ------------------------------------------------------------
# ADMIN DASHBOARD
# ------------------------------------------------------------
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():

    _, products = AdminQueries.getAllProducts()
    _, users = AdminQueries.getUsers()
    _, orders = AdminQueries.getOrders()

    products = products if isinstance(products, list) else []
    users = users if isinstance(users, list) else []
    orders = orders if isinstance(orders, list) else []

    total_products = len(products)
    total_users = len(users)
    total_orders = len(orders)

    categories = set()

    for product in products:
        category = product.get('category')
        if category:
            categories.add(category)

    total_categories = len(categories)
    recent_orders = orders[:5]

    return render_template(
        'admin/dashboard.html',
        total_products=total_products,
        total_categories=total_categories,
        total_orders=total_orders,
        total_users=total_users,
        recent_orders=recent_orders
    )


# ------------------------------------------------------------
# VIEW PRODUCTS
# ------------------------------------------------------------
@app.route('/admin/products')
@admin_required
def admin_products():

    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    status = request.args.get('status', '').strip()
    stock = request.args.get('stock', '').strip()

    try:
        min_price = float(request.args.get('min_price', 0))
    except (ValueError, TypeError):
        min_price = 0

    try:
        max_price = float(request.args.get('max_price', 0))
    except (ValueError, TypeError):
        max_price = 0

    page = request.args.get('page', 1, type=int)
    if page < 1:
        page = 1

    per_page = 10

    result = AdminQueries.getProducts(
        search=search,
        category=category,
        status=status,
        stock=stock,
        min_price=min_price,
        max_price=max_price,
        page=page,
        per_page=per_page
    )

    products = result['products']
    total = result['total']
    categories = result['categories']

    total_pages = (total + per_page - 1) // per_page

    if total_pages > 0 and page > total_pages:
        return redirect(url_for(
            'admin_products',
            page=total_pages,
            search=search,
            category=category,
            status=status,
            stock=stock,
            min_price=min_price,
            max_price=max_price
        ))

    return render_template(
        'admin/products.html',
        products=products,
        categories=categories,
        page=page,
        total_pages=total_pages,
        total=total,
        search=search,
        category=category,
        status=status,
        stock=stock,
        min_price=min_price,
        max_price=max_price,
        per_page=per_page
    )


# ------------------------------------------------------------
# ADD PRODUCT
# ------------------------------------------------------------
@app.route('/admin/products/add', methods=['GET', 'POST'])
@admin_required
def admin_add_product():

    if request.method == 'GET':
        return render_template('admin/add_product.html')

    name = request.form.get('name', '').strip()
    category = (
        request.form.get('category', '').strip()
        or request.form.get('new_category', '').strip()
    )
    description = request.form.get('description', '')
    image = request.files.get('image')

    try:
        buy = money(request.form.get('buyprice', '0'))
        price = money(request.form.get('price', '0'))
        stock = int(request.form.get('stock', '0'))
    except (ValueError, TypeError):
        flash('Enter valid prices and stock.', 'err')
        return redirect(url_for('admin_add_product'))

    if (
        not name or not category or stock < 0
        or buy < 0 or price < 0
        or not image or not image.filename
        or '.' not in image.filename
        or image.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS
    ):
        flash(
            'Provide valid product details and a JPG, PNG, WEBP or GIF image.',
            'err'
        )
        return redirect(url_for('admin_add_product'))

    imgname = secure_filename(image.filename)

    target = Path(app.root_path) / 'static' / 'images' / 'products'
    target.mkdir(parents=True, exist_ok=True)

    # Generate a unique filename to avoid overwriting another product image.
    imgname = f'{uuid.uuid4().hex}_{imgname}'
    storedpath = f'static/images/products/{imgname}'

    product_data = (
        name,
        description,
        category,
        stock,
        buy,
        price,
        imgname,
        storedpath
    )

    ok, msg = AdminQueries.insertProductRecord(product_data)

    if ok:
        image.save(target / imgname)
        flash(msg, 'msg')
    else:
        flash(msg, 'err')

    return redirect(url_for('admin_products'))


# ------------------------------------------------------------
# DELETE / DEACTIVATE PRODUCT
# Soft delete is used because order_details may reference products.
# ------------------------------------------------------------
@app.route('/admin/products/delete/<int:product_id>', methods=['POST', 'GET'])
@admin_required
def admin_delete_product(product_id):

    ok, msg = AdminQueries.deleteProduct(product_id)
    flash(msg, 'msg' if ok else 'err')

    return redirect(url_for('admin_products'))


@app.route('/admin/products/deactivate/<int:product_id>', methods=['POST'])
@admin_required
def admin_deactivate_product(product_id):

    success = AdminQueries.deactivateProduct(product_id)

    if success:
        flash('Product deactivated successfully.', 'msg')
    else:
        flash('Unable to deactivate product.', 'err')

    return redirect(url_for('admin_products'))


@app.route('/admin/products/activate/<int:product_id>', methods=['POST'])
@admin_required
def admin_activate_product(product_id):

    success = AdminQueries.activateProduct(product_id)

    if success:
        flash('Product activated successfully.', 'msg')
    else:
        flash('Unable to activate product.', 'err')

    return redirect(url_for('admin_products'))


# ------------------------------------------------------------
# EDIT PRODUCT
# ------------------------------------------------------------
@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(product_id):

    if request.method == 'GET':
        ok, product = AdminQueries.getAllProducts(product_id)

        if not ok:
            abort(404)

        return render_template(
            'admin/edit_product.html',
            product=product
        )

    try:
        data = (
            request.form['name'].strip(),
            request.form.get('description', ''),
            request.form['category'].strip(),
            int(request.form['stock']),
            money(request.form.get('buyprice', '0')),
            money(request.form.get('price', '0'))
        )

        if (
            not data[0] or not data[2]
            or data[3] < 0 or data[4] < 0 or data[5] < 0
        ):
            raise ValueError

    except (ValueError, KeyError, TypeError):
        flash('Invalid product values.', 'err')
        return redirect(url_for(
            'admin_edit_product',
            product_id=product_id
        ))

    ok, msg = AdminQueries.updateProduct(product_id, data)
    flash(msg, 'msg' if ok else 'err')

    return redirect(url_for('admin_products'))


# ------------------------------------------------------------
# CATEGORIES
# Category values are stored in products.category.
# There is no separate categories table in this database.
# ------------------------------------------------------------
@app.route('/admin/category')
@admin_required
def admin_category():

    _, products = AdminQueries.getAllProducts()

    if not isinstance(products, list):
        products = []

    categories = sorted({
        product['category']
        for product in products
        if product.get('category')
    })

    return render_template(
        'admin/category.html',
        categories=categories
    )


@app.route('/admin/category/add-category', methods=['GET', 'POST'])
@admin_required
def admin_add_category():

    flash(
        'Categories are stored in products.category. '
        'Add a category while creating or editing a product.',
        'msg'
    )

    return redirect(url_for('admin_category'))


# ------------------------------------------------------------
# USERS
# ------------------------------------------------------------
@app.route('/admin/users')
@admin_required
def admin_users():

    _, users = AdminQueries.getUsers()

    return render_template(
        'admin/users.html',
        users=users if isinstance(users, list) else []
    )


@app.route('/admin/users/<int:user_id>')
@admin_required
def admin_user_details(user_id):

    ok, user = AdminQueries.getUserDetails(user_id)

    if not ok:
        abort(404)

    return render_template(
        'admin/user_details.html',
        user=user
    )


@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(user_id):

    if request.method == 'GET':
        ok, user = AdminQueries.getUserById(user_id)

        if not ok:
            abort(404)

        return render_template(
            'admin/edit_user.html',
            user=user
        )

    data = {
        'username': request.form.get('name', '').strip(),
        'email': request.form.get('email', '').strip().lower(),
        'phone': request.form.get('phone', '').strip(),
        'role': request.form.get('role', 'user').strip().lower()
    }

    ok, msg = AdminQueries.updateUser(user_id, data)
    flash(msg, 'msg' if ok else 'err')

    if ok:
        return redirect(url_for(
            'admin_user_details',
            user_id=user_id
        ))

    return redirect(url_for(
        'admin_edit_user',
        user_id=user_id
    ))


# ------------------------------------------------------------
# ADMIN ORDERS
# payments information is stored in payments, not orders.
# getOrders() in adminDB.py returns (success, list_of_orders).
# ------------------------------------------------------------
@app.route('/admin/orders')
@admin_required
def admin_orders():

    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()

    page = request.args.get('page', 1, type=int)
    if page < 1:
        page = 1

    per_page = 10

    ok, result = AdminQueries.getOrders(
        search=search,
        status=status
    )

    orders = result if ok and isinstance(result, list) else []

    total = len(orders)
    total_pages = (total + per_page - 1) // per_page

    if total_pages > 0 and page > total_pages:
        return redirect(url_for(
            'admin_orders',
            page=total_pages,
            search=search,
            status=status
        ))

    # Pagination is applied here because getOrders() returns a list.
    start = (page - 1) * per_page
    end = start + per_page
    paginated_orders = orders[start:end]

    return render_template(
        'admin/orders.html',
        orders=paginated_orders,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        search=search,
        status=status
    )


# ------------------------------------------------------------
# VIEW ORDER DETAILS
# ------------------------------------------------------------
@app.route('/admin/orders/<int:order_id>')
@admin_required
def admin_order_details(order_id):

    order = AdminQueries.getOrderById(order_id)

    if not order:
        flash('Order not found.', 'err')
        return redirect(url_for('admin_orders'))

    items = AdminQueries.getOrderItems(order_id)

    subtotal = sum(float(item['subtotal']) for item in items)
    shipping = round(float(order['total']) - subtotal, 2)

    order['items'] = items
    order['subtotal'] = subtotal
    order['shipping'] = shipping

    return render_template(
        'admin/order_details.html',
        order=order,
        items=items
    )


# ------------------------------------------------------------
# EDIT ORDER STATUS
# Valid orders.status enum values:
# pending, shipped, delivered, cancelled
# ------------------------------------------------------------
@app.route('/admin/orders/<int:order_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_order(order_id):

    order = AdminQueries.getOrderById(order_id)

    if not order:
        flash('Order not found.', 'err')
        return redirect(url_for('admin_orders'))

    if request.method == 'POST':

        status = request.form.get('status', '').strip().lower()

        allowed_statuses = [
            'pending',
            'shipped',
            'delivered',
            'cancelled'
        ]

        if status not in allowed_statuses:
            flash('Invalid order status.', 'err')
            return redirect(url_for(
                'admin_edit_order',
                order_id=order_id
            ))

        success = AdminQueries.updateOrderStatus(
            order_id,
            status
        )

        if success:
            flash('Order status updated successfully.', 'msg')
            return redirect(url_for(
                'admin_order_details',
                order_id=order_id
            ))

        flash(
            'Failed to update order status. Check the order status and database.',
            'err'
        )

    return render_template(
        'admin/order_edit.html',
        order=order
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

#main
if __name__ == "__main__":
    print(createTables())
    app.run(debug=True)