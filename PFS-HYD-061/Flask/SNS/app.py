from flask import Flask, render_template, request, redirect


from database import createTables, AuthenticationQuaries


# flask instance
app = Flask(__name__)

# ======================================================================
#                              Authentication Routes
# ======================================================================
@app.route('/')
def home():
    return render_template('home.html')


# login route
@app.route('/login', methods =['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')


# register route
@app.route('/register', methods =['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        print(username, email, password, confirm_password)

        # check password and confirm_password both are same or not
        if password != confirm_password:
            print("Password missmatch")
            return redirect('/register')

        # check user email already exists in database or not
        user = AuthenticationQuaries.getUserData(email= email)
        if isinstance(user, dict) and user.get('userid'):
            print("Email Already Exists")
            return redirect('/register')
        




# main
if __name__ == "__main__":
    print(createTables())
    app.run(debug=True, port = 5001)
