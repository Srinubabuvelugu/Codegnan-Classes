from flask import Flask


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
    return "This is home page"


@app.route('/students')
def students():
    return data



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
    
# static route
@app.route('/students/1')
def students1():
    return f"This student 1 data: {data['1']}"

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
