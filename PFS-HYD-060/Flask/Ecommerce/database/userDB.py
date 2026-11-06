from database.connection import DatabaseConnection

class UserQueries:
    @staticmethod
    def addCartItem(product_id:int, userid:int, quantity:int):
        cursor = db_config = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()
            # update cart item quantity if item already exists
            query = """update cart set quantity = quantity + %s 
                        where productid = %s and userid = %s"""
            cursor.execute(query, (quantity, product_id, userid))
            if cursor.rowcount:
                db_config.commit()
                return True, "Cart Item Quantity Updated"

            # insert item to cart
            query = """insert into cart(userid, productid, quantity) values(%s, %s, %s)"""
            cursor.execute(query, (userid, product_id, quantity))
            db_config.commit()
            return True, "Item added to cart"
        
        except Exception as e:
            return False, f"Something wrong in \
                        database/adminDB.AdminQueries.assCartItem():{e}"
        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()