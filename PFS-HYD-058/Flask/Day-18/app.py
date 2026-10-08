from flask import Flask, jsonify


app = Flask(__name__)

data = {
    1:{'name':'appple', 'price':100, 'stock':20},
    2:{'name':'banana', 'price':50, 'stock':0},
    3:{'name':'cherry', 'price':80, 'stock':40},
    4:{'name':'pappaya', 'price':30, 'stock':30},
    5:{'name':'orange', 'price':70, 'stock':60},
        
}

@app.route('/')
def home():
    return {"status":"success", "msg":"This is fruit managment application"}

@app.route('/fruits')
def all_fruits():
    return {"status":"success", "data":data}

# get fruit data by id
@app.route('/fruits/<int:id>')
def get_fruit_data(id):
    if id in data:
        return {"status":"success", "data":data[id]}
    else:
        return jsonify({"status":"error", "msg":"Fruit id not found"}), 404


#main
if __name__ =="__main__":
    app.run(debug=True)