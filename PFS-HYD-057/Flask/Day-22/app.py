
from flask import Flask, render_template, url_for, session, request, flash

from database import createTables


# Flask class instance
app = Flask(__name__)


# home route
@app.route('/')
def home():
    return "This is home page"



# main
if __name__ == "__main__":
    print(createTables())
    app.run(debug=True)
