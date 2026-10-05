from flask import Flask, render_template, url_for, session, redirect, request, flash, send_file
from werkzeug.utils import secure_filename
import os
import sys

from database import createTables
from database import AdminDBQueries, UserDBQueries



app = Flask(__name__)
app.secret_key = "Srinubabu@1234"



@app.route("/")
def home():
    session['id'] = 2
    return render_template('home.html')

@app.route("/register")
def register():
    return render_template('register.html')

@app.route("/login")
def login():
    return render_template("login.html")



# ====================================================================
#                   ADMIN ROUTES
# ====================================================================
@app.route("/admin/dashboard")
def admin_dashboard():
    return render_template('admin/dashboard.html')

@app.route("/admin")
def admin():
    return render_template('admin/base.html')

@app.route("/admin/products")
def admin_products():

    # get products
    if request.method == 'GET':
        # get all products
        status, products = AdminDBQueries.getAllProducts()
        if status == True:
            print(products)
            return render_template('admin/products.html', products=products)
        else:
            flash(products, 'err')
            return render_template('admin/products.html')


    return render_template('admin/products.html')

@app.route("/admin/products/add", methods=["GET", "POST"])
def admin_add_product():
    if request.method == 'GET':
        return render_template('admin/add_product.html')
    elif request.method == 'POST':
        # Handle form submission
        productname = request.form.get('name')
        category = request.form.get('category')
        if not category:
            category = request.form.get('new_category')
        buyprice = request.form.get('buyprice', 0)
        saleprice = request.form.get('price')
        quantity = request.form.get('stock')
        description = request.form.get('description')
        image = request.files.get('image')

        imgname = secure_filename(image.filename)
        print(imgname)
        storedpath = os.path.join('./static/images/products', imgname).replace('\\', '/')

        # Here you can add code to save the product details to the database
        data = (productname, description, category, quantity, buyprice, saleprice,imgname,storedpath)
        print(data)
        status, msg = AdminDBQueries.insertProductRecord(product_data=data)
        if status ==True:
            image.save(storedpath)

            # flash(msg, 'msg')
            return redirect(url_for('admin_products'))
        else:        
            flash(msg, 'err')
            return redirect(url_for('admin_products'))
        

@app.route('/admin/products/delete/<product_id>')
def admin_delete_product(product_id):
    pass

@app.route('/admin/produts/edit/<product_id>')
def admin_edit_product(product_id):
    if request.method =='GET':
        product = AdminDBQueries.getAllProducts(id=product_id)
        print(product)
        return render_template('admin/edit_product.html', product = product)
# ===============================================================
#                           Category
# =============================================================

# category
@app.route('/admin/category')
def admin_category():
    if request.method == 'GET':
        return render_template('admin/category.html')

@app.route('/admin/category/add-category')
def admin_add_category():
    pass



# =============================================================
#                       admin Orders
# =============================================================
@app.route('/admin/orders')
def admin_orders():
    if request.method == 'GET':
        return render_template('admin/orders.html')



# =============================================================
#                       admin users
# =============================================================
@app.route('/admin/users')
def admin_users():
    if request.method == 'GET':
        return render_template('admin/users.html')



# =============================================================
#                       admin Settings
# =============================================================
# @app.route('/admin/settings')
# def admin_settings():
#     if request.method == 'GET':
#         return render_template('admin/settings.html')

# =============================================================
# =============================================================
#                       User Routes
# =============================================================
# =============================================================
        
@app.route('/products', methods = ['GET','POST'])
def products():
    if request.method == 'GET':
        # get all products
        _, products = UserDBQueries.getAllProducts()
        print(products)
        return render_template('user/products.html', products=products)

@app.route('/products/<int:product_id>')
def product_details(product_id):
    if request.method == 'GET':
        status, product = UserDBQueries.getAllProducts(id=product_id)
        if status == False:
            flash(product, 'err')
            return redirect(url_for('products'))
        print(product)
        
        return render_template('user/product_details.html', product=product)



@app.route('/products/cart')
def cart():
    if request.method == 'GET':
        # get all cart itemsby userid
        return render_template('user/cart.html')


# add to cart
@app.route("/products/cart/add-to-cart/<int:product_id>", methods = ['POST'])
def add_to_cart(product_id):
    # get quantity and add item to cart
    if request.method == 'POST':
        quantity = int(request.form.get('quantity'))
        userid = session.get('id',2)
        # add to cart table
        status, msg = UserDBQueries.addToCart(userid=userid, productid=product_id,
                                              quantity= quantity)
        if status == False:
            flash(msg, 'err')
            return redirect(url_for('product_details', product_id=product_id))
        flash(msg, "msg")
        return redirect(url_for('product_details', product_id=product_id))

#  add view cart
@app.route('/cart')
def viewcart():
    if request.method == 'GET':
        # get all cart items from datatabase using user id
        userid = session.get('id',2)
        status, items = UserDBQueries.getCartItems(userid=userid)
        print(items)
        subtotal = sum([item['subtotal'] for item in items])
        shipping =subtotal * 0.01
        total = subtotal + shipping
        return render_template('user/cart.html',
                                cart_items= items, 
                                subtotal=subtotal, 
                                shipping =shipping,
                                total=total )
# update item quantity in cart
@app.route('/cart/update-quantity/<cartid>', methods=['POST'])
def update_cart_quantity(cartid):
    if request.method == 'POST':
        quantity = request.form.get('quantity')
        # update quantity through cartid
        userid = session.get('id',2)
        status, msg = UserDBQueries.updateCartQuantity(cartid=cartid, quantity=quantity, userid = userid)
        return redirect(url_for('viewcart'))



# check out
@app.route('/checkout', methods=['GET','POST'])
def checkout():
    if request.method == 'GET':
        userid = session.get('id',2)
        status, items = UserDBQueries.getCartItems(userid=userid)
        # print(items)
        subtotal = sum([item['subtotal'] for item in items])
        shipping =subtotal * 0.01
        total = subtotal + shipping
        return render_template('user/checkout.html',
                                cart_items= items, 
                                subtotal=subtotal, 
                                shipping =shipping,
                                total=total )




@app.route("/logout")
def logout():
    pass

# main
if __name__ == "__main__":
    print(createTables())
    app.run(debug=True, port=5001)