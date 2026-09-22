from flask import Flask, render_template, url_for, session, redirect, request, flash, send_file
from werkzeug.utils import secure_filename
import os
import sys

from database import createTables
from database import AdminDBQueries


app = Flask(__name__)
app.secret_key = "Srinubabu@1234"


@app.route("/")
def home():
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
            return render_template('admin/products.html', products=products)
        else:
            flash(products, 'err')
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
        storedpath = os.path.join('static','images','products',imgname)

        # Here you can add code to save the product details to the database
        data = (productname, description, category, quantity, buyprice, saleprice,imgname,storedpath)
        print(data)
        status, msg = AdminDBQueries.insertProductRecord(product_data=data)
        if status ==True:
            image.save(storedpath)

            flash(msg, 'msg')
            return redirect(url_for('admin_products'))
        else:        
            flash(msg, 'err')
            return redirect(url_for('admin_products'))
        



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




@app.route("/logout")
def logout():
    pass

# main
if __name__ == "__main__":
    print(createTables())
    app.run(debug=True, port=5001)