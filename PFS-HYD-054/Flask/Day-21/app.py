from flask import Flask


from database import createTables


app = Flask(__name__)


@app.route("/")
def home():
    return "This is home page"


# main
if __name__ == "__main__":
    print(createTables())
    app.run(debug=True)