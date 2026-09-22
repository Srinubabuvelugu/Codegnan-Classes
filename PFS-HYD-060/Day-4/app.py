# Topic: Dynamic routing 

from flask import Flask


# flask instance 
app = Flask(__name__)


data = {
    "1":{'name':'srinu','class':5},
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
def home():
    return "This is student management application"



@app.route('/students')
def students():
    return data

# @app.route('/students/1')
# def student1():
#     return data['1']


# @app.route('/students/2')
# def student2():
#     return data['2']




# Dynamic path parameters
@app.route("/students/<id>")
def get_student_data(id):
    print(type(id))
    if id in data:
        return data[id]
    return "Student id not found"



# dynamic path parameter validation

@app.route('/class/<int:class_no>')
def get_class_data(class_no):
    print(type(class_no))
    res = []
    for id in data:
        if data[id]['class'] == class_no:
            res.append(data[id])
    return res if res else "Student data not found"


# get student by search student name
@app.route('/students/name=<string:std_name>')
def get_data(std_name):
    res = []
    for id in data:
        if std_name in data[id]['name']:
            res.append(data[id])
    return res if res else "Student data not found"





# contact route
@app.route('/contact')
def contact():
    return "This contact page"


# main
if __name__ == "__main__":
    app.run(debug = True, )