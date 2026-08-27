from flask import Flask,render_template,request

app=Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/postData',methods=['POST'])
def postData():
    name=request.form['name']
    email=request.form['email']
    password=request.form['password']
    if name is None or len(name)<2:
        return render_template('index.html',err="invalid name")
    if email is None:
        return render_template('index.html',err="invalid email")
    if password is None or len(password)<4:
        return render_template('index.html',err="invalid password")
    return render_template('index.html',msg="submitted successfully")

# madhu, madhu@codegnan.com, 12345
# PUT - GET + MODIFY THE NEW DATA
# GET - fetch data from db
# POST - store data in db, forms
# PUT - update entire row
# DELETE - delete a row
# PATCH - update a column in a row

@app.route('/updateData/<email>',methods=['PUT'])
def updateData(email):
    data=request.get_json()
    email1=data['email']
    print(email1)
    # DATABASE LOGIC TO PUT 
    return f'Data updated successfully for {email}'

@app.route('/deleteData/<email>',methods=['DELETE'])
def deleteData(email):
    # DATABASE LOGIC TO DELETE
    return f'Data Deleted Successfully for {email}'

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='GET':
        name=request.args.get('name')
    if request.method=='POST':
        data=request.get_json()
        name=data['name']
    return f'The name is {name}'

if (__name__=="__main__"):
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True)