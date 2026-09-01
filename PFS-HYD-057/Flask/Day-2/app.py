from flask import Flask

# creating flask instance
app = Flask(__name__)



# contact route
@app.route("/")
def contact():
    return "This contact Page"

# contact route
@app.route("/babu")
def contact1():
    return "This home 1 Page"



# home
@app.route("/babu")
def home():
    return "This home page"
# main
if __name__ == "__main__":
    app.run(debug=True)
