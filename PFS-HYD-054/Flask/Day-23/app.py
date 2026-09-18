from flask import Flask, render_template, url_for, session, redirect, request


from database import createTables


app = Flask(__name__)


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
    return render_template('admin/products.html')

@app.route("/admin/products/add", methods=["GET", "POST"])
def admin_add_product():
    if request.method == 'GET':
        return render_template('admin/add_product.html')
    elif request.method == 'POST':
        # Handle form submission
        product_name = request.form.get('product_name')
        category = request.form.get('category')
        if not category:
            category = request.form.get('new_category')
        price = request.form.get('price')
        stock = request.form.get('stock')
        description = request.form.get('description')
        image = request.files.get('image')
        # Here you can add code to save the product details to the database
        

        pass

@app.route("/logout")
def logout():
    pass

# main
if __name__ == "__main__":
    print(createTables())
    app.run(debug=True, port=5001)