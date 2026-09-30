from database.connection import DatabaseConnction
from functools import wraps




# insert product record  

class UserDBQueries:
    
    def getAllProducts(id:int=None):
        try: 
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)

            query = "select * from products where is_active = %s"
            values = [True]
            if id:
                query += " and productid = %s"
                values.append(id)
            # query += " order by updated_At desc"
            if id:
                cursor.execute(query, tuple(values))
                products = cursor.fetchone()
            else:
                cursor.execute(query, tuple(values))
                products = cursor.fetchall()

            db_config.commit()
            if products:
                return True, products
            else:
                return False, "Product Not exists"
        except Exception as e:
            return False, f"Something wrong in database/userDB.py-getAllProducts:{e}"


    def addToCart(userid:int,productid:int, quantity:int):
        try: 
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)

            query = "insert into cart(userid, productid, quantity) values(%s, %s, %s)"
            cursor.execute(query,(userid, productid, quantity) )
            db_config.commit()
            return True, "Product added to cart"
        except Exception as e:
            return False, f"Something wrong in database/userDB.py-insertToCart:{e}"

    def getCartItems(userid:int):
        try: 
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)

            query = """select c.cartid, c.userid, c.productid, c.quantity, p.productname, p.category, p.saleprice, p.storedpath, (c.quantity * p.saleprice) as subtotal
                from cart c
                left join products p
                on c.productid = p.productid
                where userid = %s"""
            cursor.execute(query,(userid,))
            items = cursor.fetchall()
            return True, items
        except Exception as e:
            return False, f"Something wrong in database/userDB.py-getCartItems:{e}"

    def updateCartQuantity(cartid:int, quantity:int, userid:int):
        try: 
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)

            query = """update cart set quantity = %s where cartid = %s and userid = %s"""
            cursor.execute(query,(quantity,cartid, userid))
            db_config.commit()
            return True, "Qauntity Updated"
        except Exception as e:
            return False, f"Something wrong in database/userDB.py-updateCartQuantity:{e}"

