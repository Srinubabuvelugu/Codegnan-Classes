from flask import Flask


# flask instance 
app = Flask(__name__)


data = {
    "1":{'aname':'srinu','class':5},
    "2":{'name':'babu','class':6},
    "3":{'name':'bhanu','class':7},
    "4":{'name':'mahi','class':5},
    "5":{'name':'geethu','class':6}      
}



# # syntax for routing
# @app.route('/path')
# def func():
#     # black statements
#     # Return statement



# home route
@app.route('/')
def home1():
    return "This is home page 1"
# home route
@app.route('/')
def home():
    return "This is student management application"



@app.route('/students')
def students():
    return data

@app.route('/students/1')
def student1():
    return data['1']



# contact route
@app.route('/contact')
def contact():
    return "This contact page"


# main
if __name__ == "__main__":
    app.run(debug = True)