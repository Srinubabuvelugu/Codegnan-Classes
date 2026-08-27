# from library (flask) importing class (Flask)
from flask import Flask

# object to connect with members
app=Flask(__name__)
#__name__ is saying that app is Flask object

@app.route('/')
def home():
    return 'PFS-HYD-054 was cool'

@app.route('/madhu')
def madhu():
    return 'Madhu is a Good Boy'

@app.route('/codegnan')
def codegnan():
    return 'Codegnan Rocks'

if(__name__=="__main__"):
    app.run(host='0.0.0.0',port=5000,debug=True) 
