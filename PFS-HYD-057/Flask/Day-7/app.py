from flask import Flask, request, redirect, render_template
from database import CreateTables


# Flask instance
app = Flask(__name__)


# ======================================================
#                     Auth routes
# =====================================================
# home route
@app.route("/")
def home():
    return render_template('home.html')


# register route
@app.route('/register',methods = ['GET','POST'])
def register():
    pass


# login route
@app.route('/login', methods = ['GET', 'POST'])
def login():
    pass


# main
if __name__ == "__main__":
    print(CreateTables())
    app.run(debug=True, port = 8000)