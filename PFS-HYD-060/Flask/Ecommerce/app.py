from flask import Flask, redirect, render_template, url_for, session, request

from database import createTables


app = Flask(__name__)




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




# login
@app.route("/login")
def login():
    return render_template('login.html')


# main
if __name__ == "__main__":
    print(createTables())
    app.run(debug=True)

