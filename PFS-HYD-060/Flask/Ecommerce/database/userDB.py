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


    # create order
    @staticmethod
    def createOrder(userid:int, address:str, payment_method:str,
                     razorapy_id:str=None, razorapy_order_id:str=None):
        cursor = db_config = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)
            # get cart items
            query = """select * from cart where userid = %s"""
            cursor.execute(query, (userid, ))
            items = cursor.fetchall()
            if not items:
                return False, "Cart is Empty"

            # check weather the stock is available for every cart item
            query = """select c.cartid, c.userid, c.productid, c.quantity,
                                    p.productname, p.category, p.saleprice,
                                    p.quantity as stock,
                                    c.quantity * p.saleprice as subtotal
                                    from cart c
                                    inner join products p
                                    on c.productid = p.productid
                                    where c.userid = %s For update;"""
            cursor.execute(query, (userid, ))
            items = cursor.fetchall()
            for item in items:
                if item['quantity'] > item['stock']:
                    return False, f"{item['productname']} product currently not have required stock"

            # update each product stock
            sub_total = 0
            query = "update products set quantity = quantity - %s where productid = %s"
            for item in items:
                cursor.execute(query, (item['quantity'], item['productid']))
                sub_total += item['sub_total']

            total = sub_total + sub_total * 0.01

            # insert into orders table
            query = """insert into orders(userid, address, status, total) values(%s, %s, %s, %s)"""
            cursor.execute(query, (userid, address, "pending",total))
            orderid =cursor.lastrowid


            # insert into order details
            query = """insert into order_details(orderid, productid, quantity, price) 
                        values(%s, %s, %s, %s)"""
            for item in items:
                cursor.execute(query, (orderid, item['productid'], 
                                       item['quantity'], item['saleprice']))

            # insert into payments
            query = """insert into payments(orderid, userid, status, method, amount,
                                razorpay_id, razorpay_order_id) 
                                values(%s, %s, %s, %s, %s, %s, %s)"""
            method = payment_method.lower()
            cursor.execute(query, (orderid, userid,'pending',method, total,
                                   razorapy_id, razorapy_order_id ))

            # clear the cart
            query = "delete from cart where userid = %s"
            cursor.execute(query, (userid, ))
            db_config.commit()

            return True, {'order_id':orderid, 'Total':total}

        
        except Exception as e:
            db_config.rollback()
            return False, f"Something wrong in \
                        database/userDB.UserQueries.createOrder():{e}"
        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    