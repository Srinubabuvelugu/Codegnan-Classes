from flask import Flask
import uuid

app=Flask(__name__)

@app.route('/')
def home():
    return 'Flask Server is running'

@app.route('/generate')
def generate():
    id=uuid.uuid4().hex
    print(id)
    return  f"The generated id is {id}"

# /name - Static Routing
# /name/madhu, /name/saisharan - Dynamic Routing
@app.route('/name/<username>')
def name(username):
    return f"The username is {username}"

@app.route('/skills/<s1>/<s2>')
def skills(s1,s2):
    return f"The skills are {s1}, {s2}"

@app.route('/cgpa/<int:cg>')
def cgpa(cg):
    return f"The CGPA is {cg}"

@app.route('/attendance/<float:att>')
def attendance(att):
    return f"The attendance is {att}"

@app.route('/file/<path:fp>')
def file(fp):
    return f"The file path is {fp}"

@app.route('/id/<uuid:uid>')
def id(uid):
    return f"The id is {uid}"

if (__name__=="__main__"):
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )
