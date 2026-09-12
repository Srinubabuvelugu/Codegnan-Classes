from flask import Flask, render_template, url_for, session, redirect


from database import createTables


app = Flask(__name__)


@app.route("/")
def home():
    return render_template('home.html')

@app.route("/register")
def register():
    return render_template('register.html')

@app.route("/login")
def login():
    return render_template("login.html")

# main
if __name__ == "__main__":
    # print(createTables())
    app.run(debug=True, port=5001)