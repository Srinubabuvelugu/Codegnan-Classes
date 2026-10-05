from flask import Flask, render_template, request

from database import createTables


app = Flask(__name__)

# home route
@app.route('/')
def home():
    return render_template('home.html')

# login 
@app.route("/login", methods = ['GET','POST'])
def login():
    # get request
    if request.method == 'GET':
        return render_template('login.html')
    # Post request

# register 
@app.route('/register', methods =['GET','POST'])
def register():
    # get request
    if request.method == 'GET':
        return render_template('register.html')
    # Post request

#main
if __name__ == "__main__":
    print(createTables())
    app.run(debug=True)
