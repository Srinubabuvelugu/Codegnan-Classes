from flask import Flask, jsonify, request, make_response, session


app = Flask(__name__)
app.secret_key="srinubabu@1324"

data = {
    1:{'name':'appple', 'price':100, 'stock':20},
    2:{'name':'banana', 'price':50, 'stock':0},
    3:{'name':'cherry', 'price':80, 'stock':40},
    4:{'name':'pappaya', 'price':30, 'stock':30},
    5:{'name':'orange', 'price':70, 'stock':60},
        
}

@app.route('/')
def home():
    session["id"] = 5
    return {"status":"success", "msg":"This is fruit managment application"}

@app.route('/fruits')
def all_fruits():
    min_price = int(request.args.get('min_price', 0))
    max_price = int(request.args.get('max_price', 100000))
    res ={}
    for id in data:
        if data[id]['price'] in range(min_price, max_price+1):
            res[id] =data[id]
    return {"status":"success", "data":res if res else data}

# get fruit data by id
@app.route('/fruits/<int:id>')
def get_fruit_data(id):
    if id in data:
        return {"status":"success", "data":data[id]}
    else:
        return jsonify({"status":"error", "msg":"Fruit id not found"}), 404


# add fruit
@app.route('/fruits', methods = ['POST'])
def add_fruit():
    fruit_data = request.get_json()
    if "name" not in fruit_data or "price" not in fruit_data or "stock" not in fruit_data:
        return jsonify({"status":"error", "Msg":"Request body should contain name, price and stock"}), 400

    print(fruit_data)
    id = len(data) + 1
    data[id] = fruit_data
    return jsonify({"status":"success","Msg":f"Fruit added and fruit id: {id}"}), 201


# get fruit data by id
@app.route('/fruits/<int:id>', methods=['PUT'])
def update_fruit_data(id):
    fruit_data = request.get_json()
    if "name" not in fruit_data or "price" not in fruit_data or "stock" not in fruit_data:
        return jsonify({"status":"error", "Msg":"Request body should contain name, price and stock"}), 400
    
    if id in data:
        data[id] = fruit_data
        return {"status":"success", "msg":f"{id} fruit data updated"}
    else:
        return jsonify({"status":"error", "msg":"Fruit id not found"}), 404


# set cookie
@app.route('/set-cookie')
def set_cookie():
    response = make_response("Cookie created successfully")
    response.set_cookie("username","Srinubabu")
    return response

# reading cookie data
@app.route('/read-cookie')
def read_cookie():
    
    name = request.cookies.get('username')
    
    return f"Welcome {name}"



#main
if __name__ =="__main__":
    app.run(debug=True)