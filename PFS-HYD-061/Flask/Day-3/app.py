from flask import Flask


app = Flask(__name__)


# routers creation
@app.route('/')
def home():
    return "This is home page"


@app.route('/students')
def students():
    return "This is students page"


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
