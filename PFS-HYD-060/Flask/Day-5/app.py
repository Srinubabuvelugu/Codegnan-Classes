# Topic: Dynamic routing 

from flask import Flask, render_template, request, redirect


# flask instance 
app = Flask(__name__)


data = {
    "1":{'name':'srinu','class':5, 'marks':50},
    "2":{'name':'babu','class':6, 'marks':20},
    "3":{'name':'bhanu','class':7, 'marks':25},
    "4":{'name':'mahi','class':5, 'marks':98},
    "5":{'name':'geethu','class':6, 'marks':75}      
}


# home route
@app.route('/')
def home():
    return render_template('home.html', 
                           name="babu",
                            module = "Flask", 
                            batch = 57, 
                            time = "2-4 PM")



@app.route('/students')
def students():
    return render_template('students.html', students=data)

#register
@app.route('/register', methods = ['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        name = request.form.get('username')
        class_no = int(request.form.get('class'))
        marks = int(request.form.get('marks'))
        print(name,class_no, marks)
        id = len(data) + 1
        student_data = {'name':name, 'class':class_no,'marks':marks}
        data[id] = student_data
        return redirect('/students')





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