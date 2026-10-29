
from database.connection import DatabaseConnction


class UserQueries:
    @staticmethod
    def addToCart(product_id, user_id, quantity):
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor()
            query = """update cart set quantity = quantity + %s 
                        where productid = %s and userid = %s"""
            cursor.execute(query, (quantity, product_id, user_id))
            if cursor.rowcount:
                db_config.commit()
                cursor.close()
                db_config.close()
                return True, "Item Added to Cart"
            query = """insert into cart(productid, userid, quantity) values(%s, %s, %s)"""
            cursor.execute(query, (product_id, user_id, quantity))
            db_config.commit()
            cursor.close()
            db_config.close()
            return True, "Item Added to Cart"
        except Exception as e:
            return False, f"Something wrong in database/userDB.UserQueries.addToCart():{e}"
            

    # get cart items
    @staticmethod
    def cartItems(user_id):
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)
            query = """select c.cartid, p.productid, p.productname, p.category, p.saleprice,
                                c.quantity, p.storedpath,p.quantity as stock, 
                                (c.quantity * p.saleprice) as subtotal
                                from products p
                                inner join cart c
                                on c.productid = p.productid
                                where c.userid = %s"""
            cursor.execute(query, (user_id, ))
            
            items = cursor.fetchall()
            cursor.close()
            db_config.close()
            return True, items
        except Exception as e:
            return False, f"Something wrong in database/userDB.UserQueries.cartItems():{e}"
            


