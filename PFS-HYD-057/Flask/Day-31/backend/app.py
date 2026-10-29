from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS for the React frontend
CORS(app, origins=["http://localhost:5173"])

students = [
    {"id": 1, "name": "Ravi", "course": "Python"},
    {"id": 2, "name": "Sita", "course": "Java"},
    {"id": 3, "name": "Rahul", "course": "SQL"}
]

@app.route("/")
def home():
    return "Flask Backend Running"

@app.route("/api/students", methods=["GET"])
def get_students():
    return students

if __name__ == "__main__":
    app.run(debug=True, port=5000)