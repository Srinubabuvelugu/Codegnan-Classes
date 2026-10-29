from database import createTables

from flask import Flask, render_template, redirect, request, flash, url_for, session, abort

from database import AuthQueries, AdminQueries, UserQueries
import bcrypt
from werkzeug.utils import secure_filename
import os
from functools import wraps
from decimal import Decimal, InvalidOperation
from pathlib import Path

import razorpay
import uuid
app = Flask(__name__)

app.secret_key = "Srinubabu@1234"

if not os.path.exists('static'):
    os.mkdir('static')

if not os.path.exists('static/images'):
    os.mkdir('static/images')

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
    key=os.getenv('RAZORPAY_KEY_ID')
    secret=os.getenv('RAZORPAY_KEY_SECRET')
    if not key or not secret: 
        return None
    try:
        
        return razorpay.Client(auth=(key,secret))
    except ImportError: 
        return None
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
            return redirect('/products')

# ================================================================
#                       User Routes
# ================================================================

# dahsboard
@app.route('/products')
def products():
    search = request.form.get('search')

    status, products = UserQueries.getAllProducts(category=search)
    print(products)
    _,categories = AdminQueries.getCategories()
    return render_template('user/products.html', 
                           categories=categories, 
                           products=products)


# product details
@app.route('/products/<int:product_id>/details')
def product_details(product_id):
    # get product details based on product id
    status,product = UserQueries.getAllProducts(product_id=product_id)
    return render_template('user/product_details.html', product=product)

# cart
@app.route('/cart')
def viewcart():
    status, items = UserQueries.getCartItems(userid=session['id'])
    print(len(items))
    print(items)
    sub_total = 0
    for item in items:
        sub_total += item['quantity'] * item['saleprice']
    shipping  = sub_total * 0.01
    total = sub_total + shipping
    
    return render_template('user/cart.html', cart_items = items, subtotal = sub_total, shipping = shipping, total=total)


@app.route('/cart')
def cart():
    status, items = UserQueries.getCartItems(userid=session['id'])
    print(len(items))
    print(items)
    sub_total = 0
    for item in items:
        sub_total += item['quantity'] * item['saleprice']
    shipping  = int(sub_total * 0.01)
    total = sub_total + shipping
    
    return render_template('user/cart.html', cart_items = items, subtotal = sub_total, shipping = shipping, total=total)

# @app.route('/cart/checkout', methods = ['GET', 'POST'])
# def checkout():
#     if request.method == 'GET':
#         status, items = UserQueries.getCartItems(userid=session['id'])
#         sub_total = 0
#         for item in items:
#             sub_total += item['quantity'] * item['saleprice']
#         shipping  = sub_total * 0.01
#         total = sub_total + shipping
#         return render_template('user/checkout.html', subtotal = sub_total, shipping = shipping, total=total )

#     if request. method == "POST":
#         name = request.form.get('name')
#         phone = request.form.get('phone')
#         address = request.form.get('address')
#         city = request.form.get('city')
#         state = request.form.get('state')
#         pincode = request.form.get('pincode')
#         payment_method = request.form.get('payment_method')

#         address_data = (name, phone, address, city, state, pincode, payment_method)
        

# add to cart
@app.route('/products/<int:product_id>/add-to-cart', methods = ['POST'])
def add_to_cart(product_id:int):
    quantity = request.form.get('quantity')
    # insert item in cart
    status, msg = UserQueries.addItemToCart(userid=session['id'],
                                            productid=product_id,
                                            quantity=quantity)
    
    flash(msg,'msg' if status else 'err')
    print(status, msg)
    return redirect(url_for('product_details', product_id = product_id))



# update cart item quantity
@app.route('/cart/update-quantity/<int:cartid>',methods=['POST'])
@user_required
def update_cart_quantity(cartid):
    ok,msg=UserQueries.updateCartQuantity(cartid,request.form.get('quantity'),session['id'])
    flash(msg,'msg' if ok else 'err')
    return redirect(url_for('viewcart'))

@app.route('/cart/remove/<int:cartid>',methods=['POST'])
@user_required
def remove_cart_item(cartid):
    ok,msg=UserQueries.removeCartItem(cartid,session['id'])
    flash(msg,'msg' if ok else 'err')
    return redirect(url_for('viewcart'))


@app.route('/checkout',methods=['GET','POST'])
@user_required
def checkout():
    items,subtotal,shipping,total=cart_summary(session['id'])
    if not items:
        flash('Your cart is empty.','err')
        return redirect(url_for('viewcart'))
    if request.method=='GET':
        return render_template('user/checkout.html',cart_items=items,subtotal=subtotal,shipping=shipping,total=total)
    fields=['name','phone','address','city','state','pincode']
    data={k:request.form.get(k,'').strip() for k in fields}
    if any(not v for v in data.values()):
        flash('Complete all delivery address fields.','err')
        return redirect(url_for('checkout'))
    address=', '.join([data['name'],data['phone'],data['address'],data['city'],data['state'],data['pincode']])
    method=request.form.get('payment_method','COD').upper()
    if method=='COD':
        ok,order=UserQueries.createOrder(session['id'],address,'COD')
        if not ok:
            flash(str(order),'err')
            return redirect(url_for('checkout'))
        ok,msg=UserQueries.completeCOD(session['id'],order['order_id'])
        flash(msg,'msg' if ok else 'err')
        return redirect(url_for('orders'))
    if method!='RAZORPAY':
        flash('Invalid payment method.','err')
        return redirect(url_for('checkout'))
    client=razorpay_client()
    if not client:
        flash('Razorpay is not configured. Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET.','err')
        return redirect(url_for('checkout'))
    try:
        rp=client.order.create(data={'amount':int(total*100),'currency':'INR','receipt':f'user{session["id"]}-{os.urandom(4).hex()}'})
    except Exception:
        app.logger.exception('Razorpay order creation failed')
        flash('Could not start payment. Please try again.','err')
        return redirect(url_for('checkout'))
    ok,order=UserQueries.createOrder(session['id'],address,'RAZORPAY',rp['id'])
    if not ok:
        flash(str(order),'err');
        return redirect(url_for('checkout'))
    session['pending_order_id']=order['order_id']
    _,user=UserQueries.getUser(session['id'])
    return render_template('user/payment.html',amount=order['amount'],razorpay_key_id=os.getenv('RAZORPAY_KEY_ID'),razorpay_order=rp,user=user or {})

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
    db=DatabaseConnction();cur=db.cursor()
    try:
        cur.execute('UPDATE users SET username=%s,phone=%s WHERE userid=%s',(name,phone,session['id']))
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


# ================================================================
#                       Admin Routes
# ================================================================


# # admin dahsboard
# @app.route('/admin/dashboard')
# def admin_dashboard():
#     return render_template('admin/dashboard.html')

# @app.route('/admin/products')
# def admin_products():
#     # get all products
#     search = request.args.get('search')
#     category = request.args.get('category')
#     status = request.args.get('status')
#     stock = request.args.get('stock')
#     min_price = request.args.get('min_price')
#     max_price = request.args.get('max_price')
#     page = 1

#     _ , produts = AdminQueries.getAllProducts()
#     total_produts = len(produts)
#     per_page = 7
#     total_pages = total_produts // per_page + 1
    
#     print(produts)


#     return render_template('admin/products.html', 
#                            products = produts,
#                            total_pages = total_pages, 
#                            page =page, 
#                            total=total_produts, 
#                            per_page=7)

# @app.route('/admin/products/edit/<int:product_id>', methods = ['GET','POST'])
# def admin_edit_product(product_id):
#     if request.method =='GET':
#         # get product details based on procuct id
#         status, product = AdminQueries.getAllProducts(productid=product_id)
#         _, categories = AdminQueries.getCategories()
#         if status==False or not product:
#             flash("Product Not Found", "err")
#             return redirect(url_for('admin_products'))
#         return render_template("admin/edit_product.html", 
#                                product=product, 
#                                categories=categories)
#     if request.method == 'POST':
#         product_name = request.form.get('name').capitalize()
#         category = request.form.get('category').title()
    
#         price = request.form.get('price')
#         stock = request.form.get('stock')
#         description =  request.form.get('description')
#         img = request.files.get('image') 
#         img_name = img.filename
#         img_secure_name = secure_filename(img_name)
#         stored_name = str(uuid.uuid1()) + img_secure_name
#         img_path = os.path.join('static','images','products', stored_name)
#         img.save(img_path) # save image
#         # print(product_name, category, price, stock, description, img_name, stored_name)
#         if img :
#             data = data = (product_name, description,category,stock,price, stored_name,img_path, product_id)
#             status, msg = AdminQueries.updateProductData(product_data=data, img = True)
#         else:
#             data = (product_name, description,category,stock,price, product_id)
#             status, msg = AdminQueries.updateProductData(product_data=data)
#         flash(msg, 'msg' if status else 'err')
#         return redirect(url_for('admin_products'))

    


# @app.route("/admin/products/deactivate/<int:product_id>", methods=['POST'])
# def admin_deactivate_product(product_id):
#     status, msg = AdminQueries.chengeProductActivateStatus(product_id=product_id)
#     flash(msg, 'msg')    
#     return redirect(url_for('admin_products'))

# # activate product
# @app.route("/admin/products/activate/<int:product_id>", methods=['POST'])
# def admin_activate_product(product_id):
#     status, msg = AdminQueries.chengeProductActivateStatus(product_id=product_id, active=True)
#     flash(msg, 'msg')    
#     return redirect(url_for('admin_products'))

# # add product
# @app.route('/admin/products/add', methods =['GET','POST'])
# def admin_add_product():
#     if request.method == 'GET':
#         _, categories = AdminQueries.getCategories()
#         return render_template('admin/add_product.html', categories=categories)

#     if request.method == 'POST':
#         product_name = request.form.get('name').capitalize()
#         category = request.form.get('category').title()
#         new_category = request.form.get('new_category').title()
#         category = category or new_category
#         price = request.form.get('price')
#         stock = request.form.get('stock')
#         description =  request.form.get('description')
#         img = request.files.get('image')
#         img_name = img.filename
#         img_secure_name = secure_filename(img_name)
#         stored_name = str(uuid.uuid1()) + img_secure_name
#         img_path = os.path.join('static','images','products', stored_name)
#         img.save(img_path) # save image
#         print(product_name, category, price, stock, description, img_name, stored_name)

#         data = (product_name, description,category,stock,price, stored_name,img_path)
#         status, msg = AdminQueries.insertProductRecord(product_data=data)
#         flash(msg, 'msg' if status else 'err')
#         return redirect(url_for('admin_products'))


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():

    _, products = AdminQueries.getAllProducts()
    _, users = AdminQueries.getUsers()
    _, orders = AdminQueries.getOrders()

    products = products or []
    users = users or []
    orders = orders or []
    print("Orders:",orders)

    # Total products
    total_products = len(products)

    # Total users
    total_users = len(users)

    # Total orders
    total_orders = len(orders)

    # Categories are stored directly in products.category
    categories = set()

    for product in products:
        category = product.get('category')

        if category:
            categories.add(category)

    total_categories = len(categories)

    # Latest 5 orders
    recent_orders = orders[:5]

    return render_template(
        'admin/dashboard.html',
        total_products=total_products,
        total_categories=total_categories,
        total_orders=total_orders,
        total_users=total_users,
        recent_orders=recent_orders
    )
@app.route('/admin/products')
@admin_required
def admin_products():

    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    status = request.args.get('status', '').strip()
    stock = request.args.get('stock', '').strip()

    try:
        min_price = float(request.args.get('min_price', 0))
    except ValueError:
        min_price = 0

    try:
        max_price = float(request.args.get('max_price', 0))
    except ValueError:
        max_price = 0

    page = request.args.get('page', 1, type=int)

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
    print(result)
    products = result['products']
    total = result['total']
    categories = result['categories']

    total_pages = (total + per_page - 1) // per_page

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
        per_page = 10
    )

@app.route('/admin/products/add',methods=['GET','POST'])
@admin_required
def admin_add_product():
    if request.method=='GET':
        return render_template('admin/add_product.html')
    name=request.form.get('name','').strip()
    category=request.form.get('category','').strip() or request.form.get('new_category','').strip()
    description=request.form.get('description','')
    image=request.files.get('image')
    try: 
        buy=money(request.form.get('buyprice','0'))
        price=money(request.form.get('price','0'))
        stock=int(request.form.get('stock','0'))
    except (InvalidOperation,ValueError):
        flash('Enter valid prices and stock.','err')
        return redirect(url_for('admin_add_product'))
    if not name or not category or stock<0 or buy<0 or price<0 or not image or not image.filename or '.' not in image.filename or image.filename.rsplit('.',1)[1].lower() not in ALLOWED_EXTENSIONS:
        flash('Provide valid product details and a JPG, PNG, WEBP or GIF image.','err')
        return redirect(url_for('admin_add_product'))
    imgname=secure_filename(image.filename)
    target=Path(app.root_path)/'static'/'images'/'products'
    target.mkdir(parents=True,exist_ok=True)
    # Avoid collisions between uploads.
    
    imgname=f'{uuid.uuid4().hex}_{imgname}'
    storedpath=f'static/images/products/{imgname}'
    ok,msg=AdminQueries.insertProductRecord((name,description,category,stock,buy,price,imgname,storedpath))
    if ok:
        image.save(target/imgname)
        flash(msg,'msg')
    else:
        flash(msg,'err')
    return redirect(url_for('admin_products'))


@app.route('/admin/products/delete/<int:product_id>',methods=['POST','GET'])
@admin_required
def admin_delete_product(product_id):
    ok,msg=AdminQueries.deleteProduct(product_id)
    flash(msg,'msg' if ok else 'err')
    return redirect(url_for('admin_products'))

@app.route('/admin/products/deactivate/<int:product_id>', methods=['POST'])
@admin_required
def admin_deactivate_product(product_id):

    success = AdminQueries.deactivateProduct(product_id)

    if success:
        flash("Product deactivated successfully.", "msg")
    else:
        flash("Unable to deactivate product.", "err")


    return redirect(url_for('admin_products'))

@app.route('/admin/products/activate/<int:product_id>', methods=['POST'])
@admin_required
def admin_activate_product(product_id):

    success = AdminQueries.activateProduct(product_id)

    if success:
        flash("Product activated successfully.", "msg")
    else:
        flash("Unable to activate product.", "err")

    return redirect(url_for('admin_products'))
@app.route('/admin/products/edit/<int:product_id>',methods=['GET','POST'])
@admin_required
def admin_edit_product(product_id):
    if request.method=='GET':
        ok,p=AdminQueries.getAllProducts(product_id)
        if not ok:
            abort(404)
        return render_template('admin/edit_product.html',product=p)
    try:
        data=(request.form['name'].strip(),request.form.get('description',''),request.form['category'].strip(),int(request.form['stock']),money(request.form.get('buyprice',0)),money(request.form['price']))
    except (ValueError,KeyError,InvalidOperation):
        flash('Invalid product values.','err')
        return redirect(url_for('admin_edit_product',product_id=product_id))
    ok,msg=AdminQueries.updateProduct(product_id,data)
    flash(msg,'msg' if ok else 'err')
    return redirect(url_for('admin_products'))


@app.route('/admin/category')
@admin_required
def admin_category():
    _,products=AdminQueries.getAllProducts()
    categories=sorted({p['category'] for p in (products or []) if p.get('category')})
    return render_template('admin/category.html',categories=categories)


@app.route('/admin/category/add-category',methods=['GET','POST'])
@admin_required
def admin_add_category():
    flash('Categories are stored as text on products; add a category while creating/editing a product.','msg')
    return redirect(url_for('admin_category'))


@app.route('/admin/users')
@admin_required
def admin_users():
    _,users=AdminQueries.getUsers()
    return render_template('admin/users.html',users=users or [])


@app.route('/admin/users/<int:user_id>')
@admin_required
def admin_user_details(user_id):
    ok,user=AdminQueries.getUserDetails(user_id)
    if not ok:
        abort(404)
    return render_template('admin/user_details.html',user=user)


@app.route('/admin/users/<int:user_id>/edit',methods=['GET','POST'])
@admin_required
def admin_edit_user(user_id):
    if request.method == 'GET':
        ok,user=AdminQueries.getUserById(user_id)
        if not ok: 
            abort(404)
        return render_template('admin/edit_user.html',user=user)
    data={
        'username': request.form.get('name','').strip(),
        'email': request.form.get('email','').strip().lower(),
        'phone': request.form.get('phone','').strip(),
        'role': request.form.get('role','user').lower(),
    }
    ok,msg=AdminQueries.updateUser(user_id,data)
    flash(msg,'msg' if ok else 'err')
    return redirect(url_for('admin_user_details',user_id=user_id))


# ============================================================
# ADMIN ORDERS
# ============================================================

@app.route('/admin/orders')
@admin_required
def admin_orders():

    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()

    page = request.args.get('page', 1, type=int)

    if page < 1:
        page = 1

    per_page = 10

    _,result = AdminQueries.getOrders(
        search=search,
        status=status
    )
    print(result)
    orders = result
    total = len(result)

    total_pages = (total + per_page - 1) // per_page

    # If requested page doesn't exist
    if total_pages > 0 and page > total_pages:

        return redirect(
            url_for(
                'admin_orders',
                page=total_pages,
                search=search,
                status=status
            )
        )

    return render_template(
        'admin/orders.html',
        orders=orders,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


# ============================================================
# VIEW ORDER DETAILS
# ============================================================

@app.route('/admin/orders/<int:order_id>')
@admin_required
def admin_order_details(order_id):

    order = AdminQueries.getOrderById(order_id)

    if not order:

        flash('Order not found.', 'err')

        return redirect(
            url_for('admin_orders')
        )

    items = AdminQueries.getOrderItems(order_id)

    return render_template(
        'admin/order_details.html',
        order=order,
        items=items
    )


# ============================================================
# UPDATE ORDER
# ============================================================

@app.route(
    '/admin/orders/<int:order_id>/edit',
    methods=['GET', 'POST']
)
@admin_required
def admin_edit_order(order_id):

    order = AdminQueries.getOrderById(order_id)

    if not order:

        flash('Order not found.', 'err')

        return redirect(
            url_for('admin_orders')
        )

    if request.method == 'POST':

        status = request.form.get('status', '').strip().upper()

        allowed_statuses = [
            'PENDING',
            'PROCESSING',
            'SHIPPED',
            'DELIVERED',
            'CANCELLED'
        ]

        if status not in allowed_statuses:

            flash(
                'Invalid order status.',
                'err'
            )

            return redirect(
                url_for(
                    'admin_edit_order',
                    order_id=order_id
                )
            )

        success = AdminQueries.updateOrderStatus(
            order_id,
            status
        )

        if success:

            flash(
                'Order status updated successfully.',
                'msg'
            )

            return redirect(
                url_for(
                    'admin_order_details',
                    order_id=order_id
                )
            )

        else:

            flash(
                'Failed to update order status.',
                'err'
            )

    return render_template(
        'admin/order_edit.html',
        order=order
    )


# @app.route('/admin/orders/<int:order_id>/status',methods=['POST'])
# @admin_required
# def admin_edit_order(order_id):
#     ok,msg=AdminQueries.updateOrderStatus(order_id,request.form.get('status',''))
#     flash(msg,'msg' if ok else 'err')
#     return redirect(url_for('admin_order_details',order_id=order_id))


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# main
if __name__ == "__main__":
    print(createTables())
    app.run(debug=True)