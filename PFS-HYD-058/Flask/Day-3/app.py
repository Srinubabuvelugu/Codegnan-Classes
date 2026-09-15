# Topic: Templates and jinja Templates



from flask import Flask, render_template

# flask instance
app = Flask(__name__)



data = {
    "1":{'name':"srinu", "age":12, "class":7},
    "2":{'name':"babu", "age":11, "class":6},
    "3":{'name':"bhanu", "age":12, "class":7},
    "4":{'name':"sam", "age":13, "class":8},
    "5":{'name':"geethu", "age":10, "class":10}
}


# routing
@app.route("/")
def home():
    return render_template("home.html", module = "Flask", timings="9-11 am")

@app.route('/students')
def concat():
    return render_template("students.html", data = data)

# # return student 1 info
# @app.route('/students/1')
# def get_data():
#     return data['1']


# # return student 1 info
# @app.route('/students/2')
# def get_data2():
#     return data['2']

# @app.route('/students/3')
# def get_data3():
#     return data['3']

# dynamic routing
@app.route("/students/id=<string:id>")
def get_student_data(id):
    if id in data:
        return data[id]
    else:
        return "Student id not found"
@app.route("/students/class=<int:class_no>")
def get_class_data(class_no):

    return render_template('class.html', data= data, class_no = class_no)

# dynamic routing
@app.route("/students/<id>/name")
def get_student_name(id):
    if id in data:
        return data[id]['name']
    else:
        return "Student id not found"
# main
if __name__ == "__main__":
    app.run(debug=True)


