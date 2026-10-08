
from flask import Flask

import logging

logging.basicConfig(
    filename="app.log",
    level="INFO",
    format="%(asctime)s- %(levelname)s-%(message)s"
)

app = Flask(__name__)
data = {
    1:{'name':"srinu", "class":5},
    2:{'name':"mahi", "class":6},
    3:{'name':"prajwal", "class":5},
    4:{'name':"geethu", "class":7},
    5:{'name':"prerana", "class":8}
}

@app.route("/")
def home():
    logging.info("User in home page")
    return "This students application"

@app.route("/students")
def students():
    logging.info("this is students page")
    logging.info(f"studnets data:{data}")
    return data

@app.route('/contact')
def contact():
    logging.warning("User in contact page")
    return "This is contact page"


if __name__ == "__main__":
    app.run(debug=True)