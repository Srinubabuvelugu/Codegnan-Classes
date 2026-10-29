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
    class_no = int(request.args.get('class'))
    # print(class_no)
    res = {}
    if class_no:
        for id in data:
            if data[id]['class'] == class_no:
                res[id] = data[id]

    return jsonify(res if res else data)


# get students data as per id-(dynamic path parameter)
@app.route('/students/<int:id>', methods = ['GET'])
def get_student_data_by_id(id):
    if id in data:
        return jsonify({"status":"success", "data": data[id]})
    
    return jsonify({'status':"error", "msg":"Student id not found"}), 404




# register a student
@app.route('/students', methods=['POST'])
def register():
    new_student = request.get_json()
    if 'name' not in new_student or 'class' not in new_student:
        return jsonify({"status":"error", "msg":f"Request data format incorrect"}), 400

    id = len(data) + 1
    data[id] = new_student
    return jsonify({"status":"Success", "msg":f"Registred successfully and your id is {id}"}), 201



# update students data as per id-(dynamic path parameter)
@app.route('/students/<int:id>', methods = ['PUT'])
def update_student_data_by_id(id):
    if id in data:
        new_data = request.get_json()
        if 'name' not in new_data or 'class' not in new_data:
            return jsonify({"status":"error", "msg":f"Request data format incorrect"}), 400

        data[id] = new_data
        return jsonify({"status":"success", "msg": "student data updated"}),200
    
    return jsonify({'status':"error", "msg":"Student id not found"}), 404

# main
if __name__ == "__main__":
    app.run(debug=True)
