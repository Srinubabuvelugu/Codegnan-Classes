from flask import Flask, session, redirect
app = Flask(__name__)
from functools import wraps

app.secret_key="srinu@123"

def login_required(fun):
    @wraps(fun)
    def wrapper():
        if "id" not in session:
            return redirect("/")
        return fun()
    return wrapper


@app.route("/")
def home():
    # session['id'] = 2
    return "This is home page"
@app.route('/login')
@login_required
def login():
    return str(session.get("id"))

@app.route("/home")
def home1():
    session['id']=2
    return "This home"

    
if __name__ == "__main__":
    app.run(debug=True)