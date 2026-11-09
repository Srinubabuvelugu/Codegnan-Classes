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
                        database/userDB.UserQueries.addCartItem():{e}"
        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    # get all cart items
    @staticmethod
    def getCartItems(userid:int):
        cursor = db_config = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)
            # get cart item products info
            query = """select c.cartid, c.userid, c.productid, c.quantity,
                        p.productname, p.category, p.saleprice, p.storedpath,
                        c.quantity * p.saleprice as subtotal
                        from cart c
                        inner join products p
                        on c.productid = p.productid
                        where c.userid = %s;"""
            
            cursor.execute(query, (userid, ))
            items = cursor.fetchall()
            return True, items
        
        except Exception as e:
            return False, f"Something wrong in \
                        database/userDB.UserQueries.getCartItems():{e}"
        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    # update cart item quantity
    @staticmethod
    def updateCartItemQuantity(cartid:int, quantity:int):
        cursor = db_config = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)
            # get cart item products info
            query = """update cart set quantity = %s where cartid = %s"""
            
            cursor.execute(query, (quantity, cartid ))
            db_config.commit()
            return True, "quantity Updated"
        
        except Exception as e:
            return False, f"Something wrong in \
                        database/userDB.UserQueries.updateCartItemQuantity():{e}"
        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()



    # delete cart item 
    @staticmethod
    def deleteCartItem(cartid:int):
        cursor = db_config = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)
            # get cart item products info
            query = """delete from cart where cartid = %s"""
            
            cursor.execute(query, (cartid, ))
            db_config.commit()
            return True, "Item deleted"
        
        except Exception as e:
            return False, f"Something wrong in \
                        database/userDB.UserQueries.deleteCartItem():{e}"
        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    