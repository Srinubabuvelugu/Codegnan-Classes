from flask import Flask, render_template, request, redirect

from database import createTables


app = Flask(__name__)


# home route
@app.route("/")
def home():
    return render_template('home.html')


# Register route
@app.route('/register', methods = ['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        print(email, name, password, confirm_password)

        # check password and confirm_password both are same or not
        #check user email already exists or not
        # redirect tot Verifyotp page






#verify otp route
@app.route('/verifyotp', methods = ['GET','POST'])
def verifyotp():
    if request.method == 'GET':
        return render_template('verifyotp.html')

# Login Route
@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')



# main
if __name__ == "__main__":
    print(createTables())
    app.run(debug=True)
