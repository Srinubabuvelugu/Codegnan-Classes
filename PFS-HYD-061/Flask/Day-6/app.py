from flask import Flask, render_template, redirect, request


app = Flask(__name__)


data = {
    1:{'name':'Srinu babu', 'class':5, 'marks':45},
    2:{'name':'Babu', 'class':4, 'marks':45},
    3:{'name':'Mahi', 'class':3, 'marks':45},
    4:{'name':'Siva babu', 'class':5, 'marks':45},
    5:{'name':'Geethu', 'class':4, 'marks':45},
    6:{'name':'Prerana', 'class':5, 'marks':45} 
}


# routers creation
@app.route('/')
def home():
    return render_template('home.html',
                           module = "flask",
                           time="4-6pm",
                           triner = 'Babu'
    )   



@app.route('/students')
def students1():
    class_no = request.args.get('class', type=int)
    
    res = {}
    if class_no:
        for id in data:
            if data[id]['class'] == class_no:
                res[id] = data[id]
    
    return render_template('students.html', students = res if res else data)


@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        name = request.form.get('username')
        class_no = request.form.get('class')
        marks = request.form.get('marks')
        print(name, class_no, marks)
        id = len(data) + 1
        std_data = {'name':name, 'class':class_no, 'marks':marks} 
        data[id] = std_data
        return redirect('/students')






# @app.route('/students/2')
# def students2():
#     return data['2']


# Dynamic routing 1
@app.route('/students/<int:id>')
def get_student_data_by_id(id):
    if id in data:
        return data[id]
    return f'Student id {id} not found'

# get the students data based on class
@app.route('/class/<int:class_no>')
def get_students(class_no):
    res = {}
    for id in data:
        if data[id]['class'] == class_no:
            res[id] = data[id]
    return res if res else "student data not found"
    


@app.route('/contact')
def contact1():
    return "This is contact1 page"

@app.route('/contact/2')
def contact2():
    return "This is contact2 page"

@app.route('/contact/3')
def contact3():
    return "This is contact3 page"

# main
if __name__ == "__main__":
    app.run(debug=True)
