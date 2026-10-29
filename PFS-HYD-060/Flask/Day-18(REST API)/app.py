from flask import Flask, request, jsonify


app = Flask(__name__)


data = {
    1:{'name':"srinu", "class":7},
    2:{'name':"babu", "class":6},
    3:{'name':"mahi", "class":5},
    4:{'name':"geethu", "class":6},
    5:{'name':"prerana", "class":7},
}

@app.route('/')
def home():
    return {"msg":"This is student application"}

@app.route('/students', methods = ['GET'])
def Get_all_students():
    return jsonify(data)


# get students data as per id-(dynamic path parameter)
@app.route('/students/<int:id>', methods = ['GET'])
def get_student_data_by_id(id):
    if id in data:
        return jsonify({"status":"success", "data": data[id]})
    
    return jsonify({'status':"error", "msg":"Student id not found"}), 404

# main
if __name__ == "__main__":
    app.run(debug=True)
