# Topic: forms, request, redirect


from flask import Flask, render_template, request, redirect

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
    return render_template("home.html", name = "Srinu",module = "Flask", timings="9-11 am")

@app.route('/students')
def concat():
    class_no = request.args.get('class')
    if class_no:
        res = {}
        for id in data:
            if data[id]['class'] == int(class_no):
                res[id] = data[id]
        return render_template("students.html", data=res)
    return render_template("students.html", data=data)



@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    # POST Request method
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        class_no = request.form.get('class')

        id = str(len(data) + 1)
        data[id] = {"name":name, "class":class_no, "age":age}
        return redirect('/students')
        # return render_template('students.html', data = data)






# dynamic routing
@app.route("/students/id=<string:id>")
def get_student_data(id):
    if id in data:
        return data[id]
    else:
        return "Student id not found"
@app.route("/students/class")
def get_class_data():

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


