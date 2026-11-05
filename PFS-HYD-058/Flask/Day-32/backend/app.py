from flask import Flask, jsonify, request
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


@app.route("/api/students", methods=["POST"])
def register_student():

    data = request.get_json()

    new_student = {
        "id": len(students) + 1,
        "name": data["name"],
        "course": data["course"]
    }

    students.append(new_student)

    return jsonify({
        "message": "Student registered successfully",
        "student": new_student
    }), 201



if __name__ == "__main__":
    app.run(debug=True, port=5000)