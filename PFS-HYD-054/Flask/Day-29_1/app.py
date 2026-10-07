from flask import Flask, render_template, url_for, session, redirect, request, flash, abort
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from decimal import Decimal, InvalidOperation
from pathlib import Path
import os
from dotenv import load_dotenv
from database import createTables, AdminDBQueries, UserDBQueries
from database.authDB import getUserByEmail, createUser
import uuid

load_dotenv()
app=Flask(__name__)
app.secret_key=os.getenv('FLASK_SECRET_KEY','dev-only-change-this-secret')
app.config['MAX_CONTENT_LENGTH']=5*1024*1024
ALLOWED_EXTENSIONS={'png','jpg','jpeg','webp','gif'}

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
    _,items=UserDBQueries.getCartItems(uid)
    items=items if isinstance(items,list) else []
    subtotal=sum((money(i['subtotal']) for i in items),Decimal('0.00'))
    shipping=(subtotal*Decimal('0.01')).quantize(Decimal('0.01'))
    return items,subtotal,shipping,subtotal+shipping

def razorpay_client():
    key=os.getenv('RAZORPAY_KEY_ID')
    secret=os.getenv('RAZORPAY_KEY_SECRET')
    if not key or not secret: return None
    try:
        import razorpay
        return razorpay.Client(auth=(key,secret))
    except ImportError: return None

@app.route('/')
def home():
    _,items=UserDBQueries.getAllProducts()
    return render_template('home.html',products=items if isinstance(items,list) else [])

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='GET': 
        return render_template('register.html')
    username=request.form.get('username',request.form.get('name','')).strip()
    email=request.form.get('email','').strip().lower()
    password=request.form.get('password','')
    confirm=request.form.get('confirm_password','')
    phone=request.form.get('phone','').strip()
    if not username or not email or len(password)<8:
        flash('Enter a name, valid email and password with at least 8 characters.','err'); return redirect(url_for('register'))
    if password != confirm:
        flash('Passwords do not match.','err')
        return redirect(url_for('register'))
    ok,result=createUser(username,email,password,phone)
    if ok:
        flash('Registration successful. Your account has been created in the users table. Please log in.','msg')
        return redirect(url_for('login'))
    flash(result,'err')
    return redirect(url_for('register'))

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='GET': return render_template('login.html')
    email=request.form.get('email','').strip().lower()
    password=request.form.get('password','')
    ok,user=getUserByEmail(email)
    if not ok or not user or not check_password_hash(user['hashpassword'],password):
        flash('Invalid email or password.','err')
        return redirect(url_for('login'))
    session.clear()
    session['id']=user['userid']
    session['role']=user['role']
    session['username']=user['username']
    session['email']=user['email']
    target=request.args.get('next','')
    if target.startswith('/') and not target.startswith('//'):
        return redirect(target)
    return redirect(url_for('admin_dashboard' if user['role']=='admin' else 'products'))

@app.route('/logout',methods=['GET','POST'])
def logout(): 
    session.clear()
    flash('You have been logged out.','msg')
    return redirect(url_for('home'))

@app.route('/admin')
@admin_required
def admin():
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():

    _, products = AdminDBQueries.getAllProducts()
    _, users = AdminDBQueries.getUsers()
    _, orders = AdminDBQueries.getOrders()

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

    result = AdminDBQueries.getProducts(
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
    ok,msg=AdminDBQueries.insertProductRecord((name,description,category,stock,buy,price,imgname,storedpath))
    if ok:
        image.save(target/imgname)
        flash(msg,'msg')
    else:
        flash(msg,'err')
    return redirect(url_for('admin_products'))


@app.route('/admin/products/delete/<int:product_id>',methods=['POST','GET'])
@admin_required
def admin_delete_product(product_id):
    ok,msg=AdminDBQueries.deleteProduct(product_id)
    flash(msg,'msg' if ok else 'err')
    return redirect(url_for('admin_products'))

@app.route('/admin/products/deactivate/<int:product_id>', methods=['POST'])
@admin_required
def admin_deactivate_product(product_id):

    success = AdminDBQueries.deactivateProduct(product_id)

    if success:
        flash("Product deactivated successfully.", "msg")
    else:
        flash("Unable to deactivate product.", "err")


    return redirect(url_for('admin_products'))

@app.route('/admin/products/activate/<int:product_id>', methods=['POST'])
@admin_required
def admin_activate_product(product_id):

    success = AdminDBQueries.activateProduct(product_id)

    if success:
        flash("Product activated successfully.", "msg")
    else:
        flash("Unable to activate product.", "err")

    return redirect(url_for('admin_products'))
@app.route('/admin/products/edit/<int:product_id>',methods=['GET','POST'])
@admin_required
def admin_edit_product(product_id):
    if request.method=='GET':
        ok,p=AdminDBQueries.getAllProducts(product_id)
        if not ok:
            abort(404)
        return render_template('admin/edit_product.html',product=p)
    try:
        data=(request.form['name'].strip(),request.form.get('description',''),request.form['category'].strip(),int(request.form['stock']),money(request.form.get('buyprice',0)),money(request.form['price']))
    except (ValueError,KeyError,InvalidOperation):
        flash('Invalid product values.','err')
        return redirect(url_for('admin_edit_product',product_id=product_id))
    ok,msg=AdminDBQueries.updateProduct(product_id,data)
    flash(msg,'msg' if ok else 'err')
    return redirect(url_for('admin_products'))


@app.route('/admin/category')
@admin_required
def admin_category():
    _,products=AdminDBQueries.getAllProducts()
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
    _,users=AdminDBQueries.getUsers()
    return render_template('admin/users.html',users=users or [])


@app.route('/admin/users/<int:user_id>')
@admin_required
def admin_user_details(user_id):
    ok,user=AdminDBQueries.getUserDetails(user_id)
    if not ok:
        abort(404)
    return render_template('admin/user_details.html',user=user)


@app.route('/admin/users/<int:user_id>/edit',methods=['GET','POST'])
@admin_required
def admin_edit_user(user_id):
    if request.method == 'GET':
        ok,user=AdminDBQueries.getUserById(user_id)
        if not ok: 
            abort(404)
        return render_template('admin/edit_user.html',user=user)
    data={
        'username': request.form.get('name','').strip(),
        'email': request.form.get('email','').strip().lower(),
        'phone': request.form.get('phone','').strip(),
        'role': request.form.get('role','user').lower(),
    }
    ok,msg=AdminDBQueries.updateUser(user_id,data)
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

    _,result = AdminDBQueries.getOrders(
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

    order = AdminDBQueries.getOrderById(order_id)

    if not order:

        flash('Order not found.', 'err')

        return redirect(
            url_for('admin_orders')
        )

    items = AdminDBQueries.getOrderItems(order_id)

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

    order = AdminDBQueries.getOrderById(order_id)

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

        success = AdminDBQueries.updateOrderStatus(
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
#     ok,msg=AdminDBQueries.updateOrderStatus(order_id,request.form.get('status',''))
#     flash(msg,'msg' if ok else 'err')
#     return redirect(url_for('admin_order_details',order_id=order_id))

@app.route('/products')
def products():
    _,items=UserDBQueries.getAllProducts(category=request.args.get('category'),search=request.args.get('q'));return render_template('user/products.html',products=items if isinstance(items,list) else [])
@app.route('/products/<int:product_id>')
def product_details(product_id):
    ok,p=UserDBQueries.getAllProducts(id=product_id)
    if not ok:abort(404)
    return render_template('user/product_details.html',product=p)
@app.route('/products/cart')
@user_required
def cart():return redirect(url_for('viewcart'))
@app.route('/products/cart/add-to-cart/<int:product_id>',methods=['POST'])
@user_required
def add_to_cart(product_id):
    try:q=int(request.form.get('quantity',1))
    except ValueError:q=0
    ok,msg=UserDBQueries.addToCart(session['id'],product_id,q);flash(msg,'msg' if ok else 'err');return redirect(url_for('product_details',product_id=product_id))
@app.route('/cart')
@user_required
def viewcart():
    items,subtotal,shipping,total=cart_summary(session['id']);return render_template('user/cart.html',cart_items=items,subtotal=subtotal,shipping=shipping,total=total)
@app.route('/cart/update-quantity/<int:cartid>',methods=['POST'])
@user_required
def update_cart_quantity(cartid):
    ok,msg=UserDBQueries.updateCartQuantity(cartid,request.form.get('quantity'),session['id']);flash(msg,'msg' if ok else 'err');return redirect(url_for('viewcart'))
@app.route('/cart/remove/<int:cartid>',methods=['POST'])
@user_required
def remove_cart_item(cartid):
    ok,msg=UserDBQueries.removeCartItem(cartid,session['id']);flash(msg,'msg' if ok else 'err');return redirect(url_for('viewcart'))

@app.route('/checkout',methods=['GET','POST'])
@user_required
def checkout():
    items,subtotal,shipping,total=cart_summary(session['id'])
    if not items:flash('Your cart is empty.','err');return redirect(url_for('viewcart'))
    if request.method=='GET':return render_template('user/checkout.html',cart_items=items,subtotal=subtotal,shipping=shipping,total=total)
    fields=['name','phone','address','city','state','pincode'];data={k:request.form.get(k,'').strip() for k in fields}
    if any(not v for v in data.values()):flash('Complete all delivery address fields.','err');return redirect(url_for('checkout'))
    address=', '.join([data['name'],data['phone'],data['address'],data['city'],data['state'],data['pincode']]);method=request.form.get('payment_method','COD').upper()
    if method=='COD':
        ok,order=UserDBQueries.createOrder(session['id'],address,'COD')
        if not ok:flash(str(order),'err');return redirect(url_for('checkout'))
        ok,msg=UserDBQueries.completeCOD(session['id'],order['order_id']);flash(msg,'msg' if ok else 'err');return redirect(url_for('orders'))
    if method!='RAZORPAY':flash('Invalid payment method.','err');return redirect(url_for('checkout'))
    client=razorpay_client()
    if not client:flash('Razorpay is not configured. Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET.','err');return redirect(url_for('checkout'))
    try:rp=client.order.create(data={'amount':int(total*100),'currency':'INR','receipt':f'user{session["id"]}-{os.urandom(4).hex()}'})
    except Exception:app.logger.exception('Razorpay order creation failed');flash('Could not start payment. Please try again.','err');return redirect(url_for('checkout'))
    ok,order=UserDBQueries.createOrder(session['id'],address,'RAZORPAY',rp['id'])
    if not ok:flash(str(order),'err');return redirect(url_for('checkout'))
    session['pending_order_id']=order['order_id']
    _,user=UserDBQueries.getUser(session['id'])
    return render_template('user/payment.html',amount=order['amount'],razorpay_key_id=os.getenv('RAZORPAY_KEY_ID'),razorpay_order=rp,user=user or {})

@app.route('/verify-payment',methods=['POST'])
@user_required
def verify_payment():
    payment_id=request.form.get('razorpay_payment_id','');rp_order_id=request.form.get('razorpay_order_id','');signature=request.form.get('razorpay_signature','');oid=session.get('pending_order_id')
    client=razorpay_client()
    if not client or not all([payment_id,rp_order_id,signature,oid]):flash('Payment verification details are missing.','err');return redirect(url_for('payment_failed'))
    try:client.utility.verify_payment_signature({'razorpay_order_id':rp_order_id,'razorpay_payment_id':payment_id,'razorpay_signature':signature})
    except Exception:app.logger.warning('Razorpay signature verification failed');flash('Payment could not be verified.','err');return redirect(url_for('payment_failed'))
    ok,msg=UserDBQueries.markPaid(session['id'],oid,rp_order_id,payment_id)
    if not ok:flash(msg,'err');return redirect(url_for('payment_failed'))
    return redirect(url_for('payment_success'))
@app.route('/payment/success')
@user_required
def payment_success():
    oid=session.get('pending_order_id'); ok,order=UserDBQueries.getOrderDetails(oid,session['id']) if oid else (False,None)
    session.pop('pending_order_id',None)
    return render_template('user/payment_success.html',order=order if ok else None)
@app.route('/payment/failed',methods=['GET','POST'])
@user_required
def payment_failed():
    if request.method == 'POST':
        oid=request.form.get('order_id') or session.get('pending_order_id')
        reason=request.form.get('reason','Payment failed')
        if oid:
            ok,msg=UserDBQueries.failPayment(session['id'],int(oid),reason)
            flash(msg,'msg' if ok else 'err')
        session.pop('pending_order_id',None)
        return redirect(url_for('payment_failed'))
    return render_template('user/payment_failed.html',message=request.args.get('message'))

@app.route('/payment/cancel',methods=['POST'])
@user_required
def payment_cancel():
    oid=session.get('pending_order_id')
    if oid:
        ok,msg=UserDBQueries.cancelPendingOrder(session['id'],oid)
        flash(msg,'msg' if ok else 'err')
        session.pop('pending_order_id',None)
    return redirect(url_for('viewcart'))

@app.route('/orders')
@user_required
def orders():
    _,rows=UserDBQueries.getOrders(session['id']);return render_template('user/orders.html',orders=rows or [])
@app.route('/orders/<int:order_id>')
@user_required
def order_details(order_id):
    ok,order=UserDBQueries.getOrderDetails(order_id,session['id'])
    if not ok:abort(404)
    return render_template('user/order_details.html',order=order)
@app.route('/orders/<int:order_id>/invoice')
@user_required
def invoice(order_id):
    ok,order=UserDBQueries.getOrderDetails(order_id,session['id'])
    if not ok:abort(404)
    return render_template('user/invoice.html',order=order)
@app.route('/orders/<int:order_id>/invoice/download')
@user_required
def download_invoice(order_id):return redirect(url_for('invoice',order_id=order_id))
@app.route('/profile')
@user_required
def profile():
    _,user=UserDBQueries.getUser(session['id']);return render_template('user/profile.html',user=user or {})
@app.route('/profile/edit',methods=['GET','POST'])
@user_required
def edit_profile():
    from database.connection import DatabaseConnction
    if request.method=='GET':_,user=UserDBQueries.getUser(session['id']);return render_template('user/edit_profile.html',user=user or {})
    name=request.form.get('username','').strip();phone=request.form.get('phone','').strip();db=DatabaseConnction();cur=db.cursor()
    try:cur.execute('UPDATE users SET username=%s,phone=%s WHERE userid=%s',(name,phone,session['id']));db.commit();session['username']=name;flash('Profile updated.','msg')
    except Exception:db.rollback();flash('Could not update profile.','err')
    finally:cur.close();db.close()
    return redirect(url_for('profile'))

@app.route('/change-password',methods=['GET','POST'])
@user_required
def change_password():
    if request.method=='GET':
        return render_template('user/change_password.html')
    from database.connection import DatabaseConnction
    old=request.form.get('current_password','');
    new=request.form.get('new_password','')
    ok,user=getUserByEmail(session['email'])
    if not ok or not check_password_hash(user['hashpassword'],old) or len(new)<8:
        flash('Current password is incorrect or new password is too short.','err')
        return redirect(url_for('change_password'))
    db=DatabaseConnction()
    cur=db.cursor()
    try:
        cur.execute('UPDATE users SET hashpassword=%s WHERE userid=%s',(generate_password_hash(new),session['id']))
        db.commit()
        flash('Password changed.','msg')
    finally:
        cur.close()
        db.close()
    return redirect(url_for('profile'))

@app.errorhandler(403)
def forbidden(e):
    return render_template('base.html'),403

if __name__=='__main__':
    try: print(createTables())
    except Exception as e: print(f'Database setup failed: {e}')
    app.run(debug=True)
