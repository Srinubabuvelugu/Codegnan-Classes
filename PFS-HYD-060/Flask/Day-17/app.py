from flask import Flask, render_template, request, redirect, session, url_for, send_file, flash


from database import createTables, AuthQueries, NotesQueries, FilesQueries
import random
from utils import EmailTemaples, sendEmail
from utils import generateHashPassword,validateHashPassword
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature # it used to create token and validate token


import os
from werkzeug.utils import secure_filename
import uuid
from mimetypes import guess_type


app = Flask(__name__)
app.secret_key = "Srinubabu@1123"
serializer = URLSafeTimedSerializer(app.secret_key)

if not os.path.exists('uploads'):
    os.mkdir('uploads')





# generate token
def generateToken(email:str):
    token = serializer.dumps(obj=email, salt="reset-password")
    return token

# validate token
def validateToken(token):
    try:
        data = serializer.loads(token, 
                                salt="reset-password",
                                max_age=600) # 10 mins
        return data
    except BadTimeSignature:
        print("URL Time Expired")
        return redirect('/login')
    except SignatureExpired:
        print("Invalid url ")
        return redirect('/login')






# home route
@app.route('/')
def home():
    return render_template('home.html')

# login 
@app.route("/login", methods = ['GET','POST'])
def login():
    # get request
    if request.method == 'GET':
        return render_template('login.html')
    # Post request
    if request.method =='POST':
        email = request.form.get('email')
        password = request.form.get('password')
        status, user = AuthQueries.checkEmailExists(email=email, data=True)
        # print(user)
        if status == False:
            flash(user, 'msg' if status else 'err')
            return redirect('/login')
        # match password
        status = validateHashPassword(password=password,
                                    hash_password=user['hashpassword'])
        if status == False:
            flash("Password incorrect", 'msg' if status else 'err')
            return redirect('/login')
        # redicte to dash board page
        session.clear()
        session['id'] = user['userid']
        session['username'] = user['username']
        return redirect('/dashboard')






# register 
@app.route('/register', methods =['GET','POST'])
def register():
    # get request
    if request.method == 'GET':
        return render_template('register.html')
    # Post request
    if request.method == 'POST':
        name = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        print(name, email, password, confirm_password)
        # check password and confirm_password both are same or not
        # check email already exist or not
        # generate otp
        # send otp via email
        # redirect ti verify otp page
        if password != confirm_password:
            print("Password miss match")
            return redirect('/register')

        status, msg = AuthQueries.checkEmailExists(email=email)
        if status == True:
            print(msg)
            return redirect('/login')
        print(msg)

        otp = random.randint(1000,9999) # it generate 4 digit random number
        body = EmailTemaples.registerEmailTemplate(otp=otp, username=name)
        status, msg = sendEmail(to_email=email,
                                subject="SNS managment Register!!!",
                                body = body)
        if status == False:
            print(msg)
            return redirect('/register')
        session.clear()
        session['otp'] = otp
        session['username'] = name
        session['email'] = email
        session['password'] = password
        # redirect to verify otp page
        return redirect('/verify-otp')

@app.route('/verify-otp', methods=['GET','POST'])
def verifyotp():
    if request.method =='GET':
        return render_template('verifyotp.html')
    if request.method == "POST":
        otp = int(request.form.get('otp'))
        # match otp
        if otp!= session['otp']:
            print("OTP Incorrect")
            return redirect('/vefiry-otp')
        hash_password = generateHashPassword(password=session['password'])
        status, msg = AuthQueries.insertUserRecord(username=session['username'],
                                                   email=session['email'],
                                                   hash_password= hash_password)
        if status == False:
            print(msg)
            return redirect('/')
        print(msg)
        return redirect('/login')

        #store user data in database

    
# forgot - password
@app.route('/forgot-password', methods = ['GET','POST'])
def forgot_password():
    if request.method =='GET':
        return render_template('forgot_password.html')
    if request.method == 'POST':
        email = request.form.get('email')
        # check email exists
        status, msg = AuthQueries.checkEmailExists(email=email)
        if status == False:
            print(msg)
            return redirect(url_for('login'))
        # generate email token
        token = generateToken(email=email)
        # generate reset password link
        reset_link = url_for('reset_password', token=token, _external = True)
        # send link via email
        body = EmailTemaples.forgotPasswordTemplate(url=reset_link)
        status, msg = sendEmail(to_email=email, 
                                subject="Reset Password - SNS",
                                body = body)
        if status == False:
            print(msg)
            return redirect(url_for('forgot_password'))
        print(msg)
        # redirect to login page
        return redirect(url_for('login'))



# reset password 
@app.route('/reset-password/<token>', methods = ['GET','POST'])
def reset_password(token):
    # validate token
    email = validateToken(token=token)
    if request.method =='GET':
        return render_template('reset_password.html', token_val = token)
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        # match NP and CP
        if new_password != confirm_password:
            print("Password miss match")
            return redirect(url_for('reset_password', token = token))
        # generate hash password
        hash_password = generateHashPassword(password=new_password)
        # update hash password in database by using email
        status, msg = AuthQueries.updatePassword(email=email,
                                                 hash_password=hash_password)
        print(msg)
        return f"<h2>{msg}</h2>"
        # return msg like "Password Updates successfully"
        








# dashboard 
@app.route("/dashboard")
def dashboard():
    if 'id' not in session:
        return redirect('/login')

    return render_template('dashboard.html', 
                           username = session.get('username'))

# =============================================================================
#                               Notes Routes
# =============================================================================
@app.route('/dashboard/notes')
def mynotes():
    if 'id' not in session:
        return redirect('/login')
    userid = session['id']
    status, all_notes = NotesQueries.getAllNotes(userid=userid)
    return render_template('notes.html', notes = all_notes)

# new notes
@app.route('/dashboard/notes/new-notes', methods=['GET','POST'])
def new_notes():
    if 'id' not in session:
        return redirect('/login')
    if request.method == 'GET':
        return render_template('new_notes.html')
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        userid = session['id']
        # stored notes in  database
        status, msg = NotesQueries.insertNotesRecord(userid=userid,
                                                    title=title, 
                                                    content=content)
        print(msg)
        return redirect(url_for('mynotes'))

# view notes
@app.route('/dashboard/notes/view/<int:id>')
def view_notes(id):
    if 'id' not in session:
        return redirect('/login')
    # get notes by notes id
    status, note = NotesQueries.getAllNotes(userid=session['id'], 
                                            notesid=id)
    return render_template('view_notes.html', 
                           title=note['title'], 
                           content = note['content'])


# update notes
@app.route("/dashboard/notes/update/<int:notesid>", methods = ['GET','POST'])
def update_notes(notesid):
    if 'id' not in session:
        return redirect('/login')
    if request.method == 'GET':
        # get notes by notes id
        status, note = NotesQueries.getAllNotes(userid=session['id'],
                                                 notesid=notesid)
        return render_template('edit_notes.html',
                               title = note['title'],
                               content = note['content'],
                               id = notesid)
    if request.method =='POST':
        title = request.form.get('title')
        content = request.form.get('content')
        # update notes in database
        status, msg = NotesQueries.updateNotes(notesid=notesid, 
                                               title=title,
                                               content=content)
        print(msg)
        return redirect(url_for('mynotes'))

@app.route("/dashboard/notes/delete/<int:notesid>")
def delete_notes(notesid):
    if 'id' not in session:
        return redirect('/login')
    if request.method == 'GET':
        status, msg = NotesQueries.deleteNotes(notesid=notesid)
        print(msg)
        return redirect(url_for('mynotes'))






# =============================================================================
#                               Files Routes
# =============================================================================

@app.route("/dashboard/files")
def myfiles():
    if 'id' not in session:
        return redirect('/login')

    # get all files based on userid
    status, all_files = FilesQueries.getAllFiles(userid=session['id'])
    return render_template('files.html', files= all_files)


@app.route('/dashboard/files/upload-file', methods = ['GET','POST'])
def upload_file():
    if 'id' not in session:
        return redirect('/login')
    if request.method == 'GET':
        return render_template('upload_file.html')

    if request.method == 'POST':
        file = request.files.get('file')
        # file meta data
        original_name = file.filename
        file_name = secure_filename(original_name)
        file_type = original_name.split(".")[-1]
        if file_type not in {'pdf','jpg','jpeg','docx','png','csv'}:
            print("File type not allowed")
            return redirect(url_for('upload_file'))
        
        unique_name = str(uuid.uuid1()) + "_" + file_name
        file_path = os.path.join('uploads',unique_name)
        # save file 
        file.save(file_path)
        file_size = os.path.getsize(file_path) # it returns file size in terms of bytes
        mime_type = guess_type(file_path)[0]
        data = (session['id'],original_name, unique_name, mime_type, file_size, file_path)
        status, msg = FilesQueries.insertFileRecord(file_data=data)
        # store file meta data in table
        print(msg)
        return redirect(url_for('myfiles'))



@app.route("/dashboard/files/view/<int:file_id>")
def view_file(file_id):
    if 'id' not in session:
        return redirect('/login')
    # get file meta data by using file_id
    status, file = FilesQueries.getAllFiles(userid=session['id'], fileid = file_id)

    return send_file(
        path_or_file=file['filepath'],
        mimetype=file['mimetype'],
        as_attachment=False
                     )

@app.route("/dashboard/files/download/<int:file_id>")
def download_file(file_id):
    if 'id' not in session:
        return redirect('/login')
    status, file = FilesQueries.getAllFiles(userid=session['id'], fileid = file_id)

    return send_file(
        path_or_file=file['filepath'],
        mimetype=file['mimetype'],
        as_attachment=True)


@app.route("/dashboard/files/delete/<int:file_id>")
def delete_file(file_id):
    if 'id' not in session:
        return redirect('/login')
    # delete in database
    # redirect to files
    status, msg = FilesQueries.deleteFile(fileid=file_id)
    print(msg)
    return redirect(url_for('myfiles'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')



#main
if __name__ == "__main__":
    print(createTables())
    app.run(debug=True)
