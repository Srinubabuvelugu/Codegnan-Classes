# API Testing

# Postman 

from flask import Flask, request


app = Flask(__name__)

fruits = {
    1:{"name":"Apple", 'price':150, 'stock':15},
    2:{"name":"Banana", 'price':50, 'stock':5},
    3:{"name":"Cherry", 'price':120, 'stock':0},
    4:{"name":"Water melon", 'price':80, 'stock':56},
    5:{"name":"grapes", 'price':90, 'stock':25},
    6:{"name":"pappaya", 'price':30, 'stock':30}
}

# Home route
@app.route('/')
def home():
    return {"Msg": "This is fruit market application"}

# return all fruits
@app.route("/fruits")
def all_fruits():
    return fruits

# return the fruit  based on id
@app.route("/fruits/<int:id>")
def get_fruit_by_id(id):
    if id in fruits:
        return fruits[id]
    return {'error':f"Fruit id {id} not found"}


# add new fruit
@app.route('/fruits', methods=['POST'])
def add_fruit():
    data = request.get_json()
    name = data['name']
    price = data['price']
    stock = data.get('stock', 0)
    new_fruit = {"name":name, 'price':price, 'stock':stock}
    if stock == 0:
        new_fruit['is_avilable'] = "out of stock"
    else:
        new_fruit['is_avilable'] = "stock avialable"
    id = len(fruits) + 1
    fruits[id] = new_fruit
    return {"msg":"Fruit added successfully","fruit id":id}    


# main
if __name__ == "__main__":
    app.run(debug=True)