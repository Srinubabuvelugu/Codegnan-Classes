from flask import Flask, request

app = Flask(__name__)

products = {1:{'name':"laptop", 'price':50000, 'quantity':50},
            2:{'name':"phone", 'price':30000, 'quantity':15},
            3:{'name':"mouse", 'price':500, 'quantity':100},
            4:{'name':"book", 'price':100, 'quantity':20},
            5:{'name':"tab", 'price':20000, 'quantity':40},
            6:{'name':"keyboard", 'price':2000, 'quantity':30}
            }

@app.route('/products', methods=['GET'])
def home():
    min = int(request.args.get('min', 0))
    max = int(request.args.get('max', 100000))
    print(min,max)
    if min and max:
        res = []
        for id in products:
            if min <= products[id]['price'] <= max:
                res.append(products[id])
        return res if res else "Not products found"
    return products

# get product details
@app.route('/products/<int:id>', methods=["GET"])
def productDetails(id):
    if id in products:
        return products[id]
    else:
        return "Product id not avaliable"

# add product
@app.route("/products", methods=['POST'])
def addProduct():
    
    new_product = request.get_json()
    id = len(products) + 1
    products[id] = new_product
    return f"Product Added and product id is {id}"


# update product quantity
@app.route('/products/<int:id>', methods=['PUT'])
def update_quantity(id):
    update_product = request.get_json()
    if id in products:
        products[id] = update_product
        return "Product Updated"
    else:
        return "Product Id not found"


# main
if __name__ == "__main__":
    app.run(debug=True)
