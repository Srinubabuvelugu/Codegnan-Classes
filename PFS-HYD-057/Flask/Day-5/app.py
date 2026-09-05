# Render Template, redirect, forms, request, HTTP Request methods
from flask import Flask, render_template, redirect, request                              # pyright: ignore[reportMissingImports]


app = Flask(__name__)

# students data
students = {
    "1":{"name":"Ravi", "class":6, "age":11, 'marks':45},
    "2":{"name":"geethu", "class":8, "age":13, 'marks':30},
    "3":{"name":"prerana", "class":7, "age":12, 'marks':75},
    "4":{"name":"srinu", "class":6, "age":11, 'marks':85},
    "5":{"name":"divya", "class":6, "age":11, 'marks':28},
    "6":{"name":"pranathi", "class":7, "age":13, 'marks':58},
    "7":{"name":"parvathi", "class":8, "age":14, 'marks':45}
}

# Routes
#Home route
@app.route("/")
def home():
    return render_template("home.html", username = "Ravi")

# studnets route
@app.route('/students')
def Allstudent():
    return render_template('students.html', students=students)


# get student 1 data
@app.route('/students/1')
def get_student_data1():
    return students['1']

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


## register student
@app.route('/students/register', methods = ['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    if request.method == 'POST':
        # get data from form
        name = request.form.get('name')
        age = request.form.get('age')
        class_no = request.form.get('class')
        id = str(len(students)+1)
        students[id] = {'name':name,'age':age,'class':class_no}
        return redirect('/students')



# search student by is
@app.route('/students/search', methods = ['GET','POST'])
def seach_student():
    if request.method == 'GET':
        return render_template('search.html')
    if request.method =='POST':
        id = request.form.get('id')
        data = students[id]
        return render_template('search.html', data = data)





# main
if __name__ == "__main__":
    app.run(debug=True)