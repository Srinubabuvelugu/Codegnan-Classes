from flask import Flask,render_template,redirect,url_for,request

app=Flask(__name__)

@app.route('/')
def home():
    return redirect(url_for('indexPage'))
    #return redirect('/index')
    # return 'Flask Server is running'

@app.route('/index')
def indexPage():
    return render_template('index.html')

@app.route('/about')
def aboutPage():
    return render_template('about.html')

# name = madhu, email=madhu@codegnan.com
@app.route('/getData',methods=['GET'])
def getData():
    name=request.args.get('name')
    email=request.args.get('email')
    return f"The name is {name}, and email is {email}"

# a={'name':'Madhu'}
# print(a['name'])
@app.route('/getDatafromPOST',methods=['POST'])
def getDatafromPOST():
    # name=request.form['name']
    # email=request.form['email']
    # we are reading json data
    # {'name': 'Madhu','email':'madhu@'}
    data=request.get_json()
    name=data['name']
    email=data['email']
    return f"The name is {name},email is {email}"


if(__name__=="__main__"):
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )