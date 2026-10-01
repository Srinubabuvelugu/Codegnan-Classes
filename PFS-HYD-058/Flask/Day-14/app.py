from flask import Flask, render_template, request, redirect, flash, session, url_for

from database import createTables

from database import getUserDataByEmail, insertUserRecord, updatePassword, insertNotesRecord, getNotesByUserid, updateNotes, deleteNotes
from utils import SendEmail, EmailTemapltes, generate_otp, generateHashPassword, verifyHashPassword

from itsdangerous import URLSafeTimedSerializer,BadSignature,SignatureExpired
app = Flask(__name__)
app.secret_key="Srinubabu@123"
serializer = URLSafeTimedSerializer(app.secret_key)

# generate token
def generateToken(email:str):
    token = serializer.dumps(
        obj=email,
        salt = "reset-password"
    )
    return token


# validate token
def validateToken(token):
    try:
        data = serializer.loads(token,
                                max_age=600,
                                salt= "reset-password")
        return data
    except BadSignature:
        flash('Invalid URl', 'err')
        return redirect(url_for('forgot_password'))
    except SignatureExpired:
        flash('URL Time expired', 'err')
        return redirect(url_for('forgot_password'))




# home route
@app.route("/")
def home():
    return render_template('home.html')


# Register route
@app.route('/register', methods = ['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        print(email, name, password, confirm_password)

        # check password and confirm_password both are same or not
        if password != confirm_password:
            flash("Password doesn't match", "err")
            return redirect('/register')
        #check user email already exists or not
        status, msg = getUserDataByEmail(email=email)
        if status == True:
            flash("User Email Already Exists", "err")
            return redirect('/register')
        # send OTP via Email
        otp = generate_otp()
        status, msg = SendEmail(to_email=email,
                                subject="SNS Registation OTP",
                                body=EmailTemapltes.OTPEmailTempalte(otp=otp,username=name))
        if status == False:
            flash(msg)
            return redirect('/register')
        flash(msg)
        # redirect tot Verifyotp page
        # store user data in session
        session.clear()
        session['name'] = name
        session['email'] = email
        session['password'] = password
        session['otp'] = otp
        return redirect('/verifyotp')







#verify otp route
@app.route('/verifyotp', methods = ['GET','POST'])
def verifyotp():
    if request.method == 'GET':
        return render_template('verifyotp.html')
    if request.method == 'POST':
        otp = request.form.get('otp')
        # match otp
        if int(otp) == session['otp']:
            #store user data in table
            # generate hash password
            hash_password = generateHashPassword(password=session['password'])
            status, msg = insertUserRecord(email=session['email'],
                                           username=session['name'],
                                           hash_password=hash_password)
            if status == False:
                flash(msg,"err")
                print(msg)
                return redirect('/register')
            else:
                flash(msg, "msg")
                print(msg)
                return redirect('/login')
        else:
            flash("Invalid OTP", "err")
            return redirect('/verifyotp')



# Login Route
@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        print(email, password)
        # check email exists in table or not
        status, user = getUserDataByEmail(email=email)
        if status == False:
            flash(user, "err")
            print(user)
            return redirect('/login')
        # if user exist verify password
        print(user)
        status = verifyHashPassword(hash_password=user['hashpassword'],
                                    password=password)
        if status == False:
            flash("Check login credentials", 'err')
            print("Check login credentials")
            return redirect('/login')
        # redirect to dashboard 
        session.clear()
        session['id'] = user['userid']
        session['email'] = email
        session['name'] = user['username']
        return redirect('/dashboard')


#forgot password
@app.route('/forgot-password', methods = ['GET','POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('forgot_password.html')
    # post request
    if request.method == 'POST':
        email = request.form.get('email')
        #check email exists or not
        status, user = getUserDataByEmail(email=email)
        if status == False:
            flash(user, 'err')
            return redirect(url_for('forgot_password'))
        # if email  exist generate token 
        token = generateToken(email=email)
        reset_link = url_for('reset_password', token=token, _external = True)
        # send reset link via email
        status, msg = SendEmail(to_email=email,
                                subject="Reset password SNS app",
                                body =EmailTemapltes.resetPasswordEmailTemplate(username=user['username'],
                                                                                url=reset_link))
        if status == False:
            flash(msg, 'err')
            return redirect(url_for('forgot_password'))
        flash(msg, 'msg')
        # redirect to login page
        return redirect(url_for('login'))

#reset password route
@app.route('/reset-password/<token>', methods = ['GET','POST'])
def reset_password(token):
    #validate token
    email = validateToken(token=token)

    if request.method == 'GET':
        return render_template('reset_password.html', token = token)
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        # match passwords
        # generate hashpassword
        # update hashpassword in database using email
        # redirect to login page
        if new_password != confirm_password:
            flash('Password miss match',"err")
            # return redirect(f'/reset-password/{token}')
            return redirect(url_for('reset_password',token=token))
        hash_password = generateHashPassword(password=new_password)
        status, msg = updatePassword(email=email,hash_password=hash_password)
        if status == False:
            flash(msg, "err")
            return redirect(url_for('login'))
        flash(msg, "msg")
        return redirect(url_for('login'))







# dashboard route
@app.route('/dashboard')
def dashboard():
    if "id" not in session:
        return redirect('/login')
    if request.method == 'GET':
        return render_template('dashboard.html', name = session['name'])


# ===========================================================
#                         Notes Routes
# ===========================================================
#notesh dachboard
@app.route('/notes')
def mynotes():
    if "id" not in session:
        return redirect(url_for('login'))
    if request.method == "GET":
        status, notes = getNotesByUserid(userid=session['id'])
        print(notes)
        return render_template("notes.html", notes=notes)

@app.route('/notes/addnotes', methods=['GET', 'POST'])
def addnotes():
    if "id" not in session:
        return redirect('/login')
    if request.method == "GET":
        return render_template("addnotes.html")
    if request.method == 'POST':
        pass
        # get data from form 
        # store notes in database
        # redirect to notes dashboard
        title = request.form.get('title')
        content = request.form.get('content')
        status, msg = insertNotesRecord(title=title, content=content, userid=session['id'])
        if status == False:
            flash(msg, 'err')
            return redirect(url_for('mynotes'))
        flash(msg, 'msg')
        return redirect(url_for('mynotes'))

@app.route('/notes/view/<notesid>')
def viewnotes(notesid):
    if "id" not in session:
        return redirect('/login')
    if request.method == 'GET':
        # get notes by userid and notesid
        status, notes  = getNotesByUserid(userid=session['id'], notesid=notesid)
        if status == False:
            flash(notes, 'err')
            return redirect(url_for('mynotes'))
        return render_template('viewnotes.html', title = notes['title'], 
                               content = notes['content'])
# edit notes
@app.route('/notes/edit/<notesid>', methods = ['GET','POST'])
def editnotes(notesid):
    if "id" not in session:
            return redirect('/login')
    if request.method == 'GET':
        status, notes  = getNotesByUserid(userid=session['id'], notesid=notesid)
        return render_template('editnotes.html', 
                               title = notes['title'], 
                               content = notes['content'], 
                               notesid = notesid)
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        # update title and content in database
        status, msg = updateNotes(title=title,
                                  content=content,
                                  notesid= notesid,
                                  userid = session['id'])
        if status == False:
            flash(msg, 'err')
        else:
            flash(msg, 'msg')
        return redirect(url_for('mynotes'))

# delete notes
@app.route('/notes/delete/<notesid>')
def deletenotes(notesid):
    if "id" not in session:
        return redirect('/login')
    if request.method == 'GET':
        # delete notes by notesid and userid
        # redirect to mynotes page
        status, msg = deleteNotes(userid=session['id'], notesid=notesid)
        if status == False:
            flash(msg, 'err')
        else:
            flash(msg, 'msg')
        return redirect(url_for('mynotes'))


# =========================================================================
#                             Files Routes
# =========================================================================
@app.route('/files')
def myfiles():
    if "id" not in session:
        return redirect('/login')
    if request.method == 'GET':
        return render_template('files.html')










#logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect('/login')


# main
if __name__ == "__main__":
    print(createTables())
    app.run(debug=True)
