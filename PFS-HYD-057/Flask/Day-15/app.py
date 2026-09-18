from flask import Flask, request, redirect, render_template, url_for,session, flash
from database import CreateTables, getUserByEmail, insertUserRecord, insertNotesRecord, getNotesByUserid, getNotesByNotesid, updateNotesByNotesid, deleteNotesByNotesid
from database import checkFileDuplicate
import random

from utils import sendEmail
from email_templates import EmailTemplates
from werkzeug.utils import secure_filename
import mimetypes

from utils import generateHashPassword, verifyHashPassword
import os
import sys

# Flask instance
app = Flask(__name__)
app.secret_key = "Srinubabu@123"

# create upload folder if not exist
if not os.path.exists('uploads'):
    os.mkdir('uploads')





# ======================================================
#                     Auth routes
# =====================================================
# home route
@app.route("/")
def home():
    return render_template('home.html')


# register route
@app.route('/register',methods = ['GET','POST'])
def register():
    if request.method =='GET':
        return render_template('register.html')
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        conform_password = request.form.get('conformpassword')
        # check password match
        # print(password, type(password))
        # print(conform_password, type(conform_password))
        if password != conform_password:
            # password miss match
            flash("Password miss match", "err")
            return redirect('/register')

        # check user already exists or not
        if getUserByEmail(email=email):
            # if user not exists
            # verify otp
            OTP = random.randint(1000,9999)
            # store OTP in session
            session['otp'] = OTP
            session['username'] = username
            session['email'] = email
            session['password'] = password
            # send otp email
            status, msg = sendEmail(to_email=email,
                                    subject="SNS- OTP Verification for Register",
                                    body=EmailTemplates.OTPEmailTemplate(
                                        username=username,
                                        otp=OTP
                                    ))
            
            if status == True:
                # reidect to verify otp page
                # flash msg Email email send
                flash("Email send to registed mail","msg")
                return redirect(url_for('verifyOTP'))
            else:
                flash(msg, "err")
                return redirect(url_for('register'))
        else:
            flash("Email Already Exists","err")
            return redirect(url_for('register'))


        # redirect to login page



# verify OTP
@app.route("/verify-otp",methods = ['GET', 'POST'])
def verifyOTP():
    if 'otp' not in session:
        return redirect(url_for('register'))
    if request.method == 'GET':
        return render_template('verifyotp.html')
    if request.method == 'POST':
        otp = int(request.form.get('otp'))
        if otp == session['otp']:
            #store user data in users table
            hash_password = generateHashPassword(password=session['password'])
            status, msg = insertUserRecord(name=session['username'],
                                           email=session['email'],
                                           hash_pasword=hash_password)

            if status == True:# reditect to login 
                flash("Registred successfully", "msg")
                return redirect(url_for('login'))
            else:
                return msg
        flash("Enter Valid OTP","err")
        return redirect(url_for('verifyOTP'))
    


# login route
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        # check user user already exist or not
        status, data = getUserByEmail(email=email, data=True)
        if status == False: #if user not exists
            flash(data, "err")
            return redirect(url_for("login"))
        #if user exists
        print(data)
        hash_password = data['HASHPASSWORD']
        # verify password
        if verifyHashPassword(password, hash_password):
            # store user data in session
            session.clear()
            session['USERID'] = data['USERID']
            session['USERNAME'] = data['USERNAME']
            session['EMAIL'] = data['EMAIL']
            # redirect to dashboard
            flash(f"Hello {data['USERNAME']}, Welcome to SNS management", "msg")
            return redirect(url_for('dashboard'))
        flash("Check your password","err")
        return redirect(url_for('login'))
            
@app.route("/dashboard")
def dashboard():
    if "USERID" not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')#, username=session['USERNAME'])

#==================================================================
#                            Notes Management
# =====================================================================
@app.route("/notes")
def mynotes():
    if request.method == 'GET':
        # get notes by userid
        _, notes = getNotesByUserid(userid = session['USERID'])
        print(notes)
        

        return render_template('notes.html', notes= notes)
@app.route("/notes/addnotes", methods=['GET', 'POST'])
def add_notes():
    if request.method == 'GET':
        return render_template('addnotes.html')
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        # store notes in table
        status, msg = insertNotesRecord(userid=session['USERID'], title=title, content=content)
        # redirect to notes dashboard
        if status == True:
            flash(msg, "msg")
            return redirect(url_for('mynotes'))
        else:
            flash(msg, "err")
            return redirect(url_for('mynotes'))


# view notes route
@app.route('/notes/view/<notesid>')
def viewnotes(notesid):
    if request.method == 'GET':
    # get the notes from database by using noteid
        status, notes = getNotesByNotesid(notesid=notesid, userid =session['USERID'])
        if status == True:
            print(notes)
            return render_template('viewnotes.html', title= notes['TITLE'], content =notes['CONTENT'])
        else:
            flash(notes, "err")
            return redirect(url_for('mynotes'))

# edit notes
@app.route('/notes/edit/<notesid>', methods = ['GET', 'POST'])
def editnotes(notesid):
    if request.method == 'GET':
        # get title, content from database using notesid
        status, notes = getNotesByNotesid(notesid=notesid, userid = session['USERID'])
        print(notes)
        if status == True:
            return render_template('editnotes.html', 
                               title=notes['TITLE'], 
                               content=notes['CONTENT'],
                               notesid = notesid)
        else:
            flash(notes, "err")
            return redirect(url_for('mynotes'))


    # POST
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        # update notes in database by using notesid
        status, msg = updateNotesByNotesid(notesid=notesid,
                                           userid=session['USERID'],
                                           title=title,
                                           content=content)
        if status == True:
            flash(msg, 'msg')
            return redirect(url_for('mynotes'))
        else:
            flash(msg, 'err')
            return redirect(url_for('mynotes'))


# delete notes by notes id
@app.route('/notes/delete/<notesid>')
def deletenotes(notesid):
    if request.method == 'GET':
        # delete notes from database using notes id 
        status, msg = deleteNotesByNotesid(notesid=notesid, userid=session['USERID'])
        if status == True:
            flash(msg, 'msg')
            return redirect(url_for('mynotes'))
        else:
            flash(msg, 'err')
            return redirect(url_for('mynotes'))
            



        
# ======================================================================================
#                               File management
# ======================================================================================

@app.route("/files")
def myfiles():
    if request.method == 'GET':
        return render_template('files.html')


@app.route('/files/uploadfile', methods = ['GET', 'POST'])
def uploadfile():
    if 'USERID' not in session:
        return redirect(url_for('login'))
    
    userid = session['USERID']

    if request.method == 'GET':
        return render_template('uploadfile.html')
    if request.method =='POST':
        file = request.files.get('file')
        # get file meta data
        original_filename = file.filename
        #generate secure file name 
        filename_secure = secure_filename(filename=original_filename)
        # check file in allowed exstation
        file_type = filename_secure.split(".")[-1].strip()
        allowed_types = ['png','jpg', 'jpeg','pdf','csv','doc']
        if file_type not in allowed_types:
            flash("File type not allowed", "err")
            return redirect(url_for('uploadfile'))
        #check duplicate file exists or not
        status, msg = checkFileDuplicate(filename=filename_secure, userid=userid)
        if status == False:
            flash(msg, 'err')
            return redirect(url_for('myfiles'))
        
        # file path
        file_path = os.path.join('uploads', filename_secure)
        file.save(file_path) # saves the file in sepecified path
        file_size = os.path.getsize(file_path)

        file_mime_type,_ = mimetypes.guess_type(file_path)
        print("--------------------------------File Meta Data------------------")
        print("Orignal name:",original_filename)
        print("Filename Secure:", filename_secure)
        print("File type:", file_type)
        print("File path:", file_path)
        print("file mime type:",file_mime_type)
        print("File size:", file_size)










@app.route("/profile")
def profile():
    pass

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))


# main
if __name__ == "__main__":
    print(CreateTables())
    app.run(debug=True, port = 8000)