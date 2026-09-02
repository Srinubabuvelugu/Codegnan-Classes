# Static and Dynamic routing 
from flask import Flask


app = Flask(__name__)

# students data
students = {
    "1":{"name":"Ravi", "class":6, "age":11},
    "2":{"name":"geethu", "class":8, "age":13},
    "3":{"name":"prerana", "class":7, "age":12},
    "4":{"name":"srinu", "class":6, "age":11},
    "5":{"name":"divya", "class":6, "age":11},
    "6":{"name":"pranathi", "class":7, "age":13},
    "6":{"name":"parvathi", "class":8, "age":14}
}

# Routes
#Home route
@app.route("/")
def home():
    return "This is student management applications"

# studnets route
@app.route('/students')
def Allstudent():
    return students


# # get student 1 data
# @app.route('/students/1')
# def get_student_data():
#     return students['1']

# # get student 1 data
# @app.route('/students/2')
# def get_student_data2():
#     return students['2']

# get students day by using dynamic routing
@app.route('/students/id=<id>')
def get_student_data(id):
    if id in students:
        return students[id]
    else:
        return "Student id not Found"

# GET STUDENTS DATA VY CLASS
@app.route('/students/class=<int:class_id>')
def getStudentsByClass(class_id):
    print(type(class_id))
    res = []
    for id in students:
        if students[id]['class'] == class_id:
            res.append(students[id])
    return res if res else "Class Not Found"


@app.route('/students/name=<string:std_name>')
def getStudentsByName(std_name:str):
    
    res = []
    for id in students:
        if students[id]['name'].lower() == std_name.lower():
            res.append(students[id])
    return res if res else "Name Not Found"


# main
if __name__ == "__main__":
    app.run(debug=True)