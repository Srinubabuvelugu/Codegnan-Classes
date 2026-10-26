from database.connection import DatabaseConnction



class UserQueries:
    # get products
    @staticmethod
    def getAllProducts(category:str=None, product_id:int=None):
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)
            query = """ select * from products where is_active = %s"""
            values= [1]
            if category:
                query += " and category = %s"
                values.append(category)
            if product_id:
                query += " and productid = %s"
                values.append(product_id)
                cursor.execute(query, tuple(values))
                products = cursor.fetchone()
            else:
                cursor.execute(query, tuple(values))
                products = cursor.fetchall()
            cursor.close()
            db_config.close()
            return True, products
        except Exception as e:
            return False, f"Something wrong in database/adminDB.UserQueries-getAllProducts():{e}"

    # add item to cart
    @staticmethod
    def addItemToCart(userid:int, productid:int, quantity:int):
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)
            
            query = """select * from cart where userid = %s"""
            cursor.execute(query, (userid,))
            cart_items = cursor.fetchall()
            # if product already exists
            for item in cart_items:
                if item['productid'] == productid:
                    query = "update cart set quantity = quantity + %s where cartid = %s"
                    cursor.execute(query,(quantity, item['cartid']))
                    db_config.commit()
                    break
            else:
                query = "insert into cart(productid, userid, quantity) values(%s, %s, %s)"
                cursor.execute(query, (productid, userid, quantity))
                db_config.commit()

            cursor.close()
            db_config.close()
            return True, "Product Added"
        except Exception as e:
            return False, f"Something wrong in database/adminDB.UserQueries-addItemToCart():{e}"
    # get cart items
    @staticmethod
    def getCartItems(userid:int):
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)
            query = """select c.*, p.* from cart c inner join products p
            on c.productid = p.productid
            where userid = %s"""
            
            cursor.execute(query, (userid, ))
            items = cursor.fetchall()
            return True, items
        except Exception as e:
            return False, f"Something wrong in database/adminDB.UserQueries-getCartItems():{e}"
