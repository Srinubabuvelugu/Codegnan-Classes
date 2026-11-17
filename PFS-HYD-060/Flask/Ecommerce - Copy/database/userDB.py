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


    # # create order
    # @staticmethod
    # def createOrder(userid:int, address:str, payment_method:str,
    #                  razorapy_id:str=None, razorapy_order_id:str=None):
    #     cursor = db_config = None

    #     try:
    #         db_config = DatabaseConnection()
    #         cursor = db_config.cursor(dictionary=True)
    #         # get cart items
    #         query = """select * from cart where userid = %s"""
    #         cursor.execute(query, (userid, ))
    #         items = cursor.fetchall()
    #         if not items:
    #             return False, "Cart is Empty"

    #         # check weather the stock is available for every cart item
    #         query = """select c.cartid, c.userid, c.productid, c.quantity,
    #                                 p.productname, p.category, p.saleprice,
    #                                 p.quantity as stock,
    #                                 c.quantity * p.saleprice as subtotal
    #                                 from cart c
    #                                 inner join products p
    #                                 on c.productid = p.productid
    #                                 where c.userid = %s For update;"""
    #         cursor.execute(query, (userid, ))
    #         items = cursor.fetchall()
    #         for item in items:
    #             if item['quantity'] > item['stock']:
    #                 return False, f"{item['productname']} product currently not have required stock"

    #         # update each product stock
    #         sub_total = 0
    #         query = "update products set quantity = quantity - %s where productid = %s"
    #         for item in items:
    #             cursor.execute(query, (item['quantity'], item['productid']))
    #             sub_total += item['sub_total']

    #         total = sub_total + sub_total * 0.01

    #         # insert into orders table
    #         query = """insert into orders(userid, address, status, total) values(%s, %s, %s, %s)"""
    #         cursor.execute(query, (userid, address, "pending",total))
    #         orderid =cursor.lastrowid


    #         # insert into order details
    #         query = """insert into order_details(orderid, productid, quantity, price) 
    #                     values(%s, %s, %s, %s)"""
    #         for item in items:
    #             cursor.execute(query, (orderid, item['productid'], 
    #                                    item['quantity'], item['saleprice']))

    #         # insert into payments
    #         query = """insert into payments(orderid, userid, status, method, amount,
    #                             razorpay_id, razorpay_order_id) 
    #                             values(%s, %s, %s, %s, %s, %s, %s)"""
    #         method = payment_method.lower()
    #         cursor.execute(query, (orderid, userid,'pending',method, total,
    #                                razorapy_id, razorapy_order_id ))

    #         # clear the cart
    #         query = "delete from cart where userid = %s"
    #         cursor.execute(query, (userid, ))
    #         db_config.commit()

    #         return True, {'order_id':orderid, 'Total':total}

        
    #     except Exception as e:
    #         db_config.rollback()
    #         return False, f"Something wrong in \
    #                     database/userDB.UserQueries.createOrder():{e}"
    #     finally:
    #         if cursor:
    #             cursor.close()
    #         if db_config:
    #             db_config.close()


    # create order
    @staticmethod
    def createOrder(userid:int, address:str,payment_method:str, razorpay_order_id:str=None, razorpay_payment_id:str=None):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)

            query = """select c.cartid, c.userid, c.quantity, p.productname, 
                        p.productid, p.quantity as stock, p.saleprice from cart c
                        join products p on c.productid = p.productid
                        where c.userid = %s FOR UPDATE"""
            cursor.execute(query, (userid, ))
            items = cursor.fetchall()
            print("cart items:",items)
            if not items:
                return False, "Cart is empty"
            # check each product stock is avilable as per the quantity
            sub_total = 0
            for item in items:
                if item['quantity'] > item['stock']:
                    return False, f"{item['productname']} current {item['quantity']}  not avilable"
                sub_total += item['quantity'] * item['saleprice']

            # Reduce the each product stocks
            for item in items:
                query = "update products set quantity = quantity - %s where productid = %s"
                cursor.execute(query, (item['quantity'], item['productid']))
            
            # add order record
            shipping = sub_total * 0.01
            query = """insert into orders(userid, status, address, total)
                        values(%s, %s, %s, %s)"""
            cursor.execute(query, (userid,"pending", address, sub_total+shipping))
            # cursor.execute("select orderid from orders where userid = %s order by orderid desc", (userid,))
            # # add payment record
            # orderid = cursor.fetchone()[0]
            orderid = cursor.lastrowid

            #add items to order details
            for item in items:
                query = """insert into order_details(orderid,productid, quantity, price)
                values(%s, %s, %s, %s)"""
                # item_sub_total = item['quantity'] * item['saleprice']
                cursor.execute(query, (orderid,item['productid'], item['quantity'], item['saleprice']))

            # insert payment in payments table
            status = "pending"
            method = payment_method.lower()
            
            
            query = """insert into payments(userid, orderid, status, method, amount, razorpay_order_id, razorpay_payment_id)
                    values(%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (userid, orderid,status, 'cash' if method=='cod' else method, sub_total +shipping,razorpay_order_id, razorpay_payment_id ))

             # Clear cart
            cursor.execute(
                "DELETE FROM cart WHERE userid = %s",
                (userid,)
            )

            db_config.commit()
            cursor.close()
            db_config.close()
            return True, {"order_id":orderid, "amount":sub_total+ shipping}
        except Exception as e:
            db_config.rollback()
            return False, f"Something wrong in database/userDB.py/UserQueries.createOrder():{e}"
            


    

    @staticmethod
    def getUser(userid):
        db = DatabaseConnection()
        cur = db.cursor(dictionary=True)
        try:
            cur.execute('''SELECT userid,username,email,phone,gender,dateofbirth,
                           profilename,profilepath,is_active,created_at
                           FROM users WHERE userid=%s''', (userid,))
            return True, cur.fetchone()
        finally:
            cur.close()
            db.close()

    @staticmethod
    def getOrders(userid):
        db = DatabaseConnection()
        cur = db.cursor(dictionary=True)

        try:
            query = '''SELECT
                        o.orderid AS id,
                        o.status,
                        o.total AS total_amount,
                        o.address,
                        o.created_at,
                        p.method AS payment_method,
                        p.status AS payment_status,
                        p.razorpay_payment_id AS payment_id
                    FROM orders o
                    LEFT JOIN payments p ON o.orderid = p.orderid
                    WHERE o.userid = %s
                    ORDER BY o.created_at DESC'''

            cur.execute(query, (userid,))
            return True, cur.fetchall()

        except Exception as e:
            return False, str(e)

        finally:
            cur.close()
            db.close()

    @staticmethod
    def getOrderDetails(orderid, userid):
        db = DatabaseConnection()
        cur = db.cursor(dictionary=True)

        try:
            query = '''SELECT
                        o.*,
                        o.orderid AS id,
                        p.method AS payment_method,
                        p.status AS payment_status,
                        p.razorpay_payment_id AS payment_id,
                        p.razorpay_order_id,
                        p.amount AS total_amount,
                        u.username AS customer_name,
                        u.phone AS customer_phone
                    FROM orders o
                    JOIN users u ON u.userid = o.userid
                    LEFT JOIN payments p ON p.orderid = o.orderid
                    WHERE o.orderid = %s AND o.userid = %s'''

            cur.execute(query, (orderid, userid))
            order = cur.fetchone()

            if not order:
                return False, "Order not found"

            query = '''SELECT
                        od.*,
                        p.productname AS product_name,
                        p.storedpath AS image,
                        p.category
                    FROM order_details od
                    JOIN products p ON p.productid = od.productid
                    WHERE od.orderid = %s'''

            cur.execute(query, (orderid,))
            order['items'] = cur.fetchall()

            # Calculate subtotal
            order['subtotal'] = sum(
                float(item['subtotal']) for item in order['items']
            )

            # Calculate actual shipping charge
            order['shipping'] = (
                float(order['total']) - order['subtotal']
            )

            order['delivery_address'] = order.get('address')

            return True, order

        except Exception as e:
            return False, str(e)

        finally:
            cur.close()
            db.close()
    @staticmethod
    def markPaid(userid, orderid, razorpay_order_id, payment_id):

        db = DatabaseConnection()
        cur = db.cursor(dictionary=True)

        try:
            db.start_transaction()

            query = '''SELECT *
                    FROM payments
                    WHERE orderid = %s
                    AND userid = %s
                    AND method = 'RAZORPAY'
                    FOR UPDATE'''

            cur.execute(query, (orderid, userid))
            payment = cur.fetchone()

            if not payment:
                db.rollback()
                return False, "Payment record not found"

            if payment['status'] == 'paid':
                db.rollback()
                return False, "Payment already verified"

            if payment['razorpay_order_id'] != razorpay_order_id:
                db.rollback()
                return False, "Razorpay order ID mismatch"

            query = '''UPDATE payments
                    SET status = 'paid',
                        razorpay_payment_id = %s
                    WHERE orderid = %s
                    AND userid = %s'''

            cur.execute(query, (payment_id, orderid, userid))

            if cur.rowcount != 1:
                db.rollback()
                return False, "Could not update payment status"

            # Remove cart items after successful verification
            cur.execute(
                "DELETE FROM cart WHERE userid = %s",
                (userid,)
            )

            db.commit()

            return True, "Payment verified successfully"

        except Exception as e:
            db.rollback()
            return False, str(e)

        finally:
            cur.close()
            db.close()



    @staticmethod
    def failPayment(userid, orderid, reason='Payment failed'):

        db = DatabaseConnection()
        cur = db.cursor(dictionary=True)

        try:
            db.start_transaction()

            # Get payment details
            query = '''SELECT *
                    FROM payments
                    WHERE orderid = %s
                    AND userid = %s
                    AND method = 'RAZORPAY'
                    FOR UPDATE'''

            cur.execute(query, (orderid, userid))
            payment = cur.fetchone()

            if not payment:
                db.rollback()
                return False, "Payment record not found"

            if payment['status'] == 'paid':
                db.rollback()
                return False, "This order is already paid"

            if payment['status'] == 'failed':
                db.rollback()
                return True, "Payment already marked as failed"

            # Restore product stock
            query = '''SELECT productid, quantity
                    FROM order_details
                    WHERE orderid = %s'''

            cur.execute(query, (orderid,))
            items = cur.fetchall()

            for item in items:
                query = '''UPDATE products
                        SET quantity = quantity + %s
                        WHERE productid = %s'''

                cur.execute(query, (
                    item['quantity'],
                    item['productid']
                ))

            # Update payment status
            query = '''UPDATE payments
                    SET status = 'failed'
                    WHERE orderid = %s AND userid = %s'''

            cur.execute(query, (orderid, userid))

            # Cancel order
            query = '''UPDATE orders
                    SET status = 'cancelled'
                    WHERE orderid = %s AND userid = %s'''

            cur.execute(query, (orderid, userid))

            db.commit()

            return True, "Payment failed and order cancelled"

        except Exception as e:
            db.rollback()
            return False, str(e)

        finally:
            cur.close()
            db.close()


    @staticmethod
    def cancelPendingOrder(userid, orderid):

        return UserQueries.failPayment(
            userid,
            orderid,
            "Customer cancelled payment"
        )
    # @staticmethod
    # def failPayment(userid, orderid, reason='Payment failed'):
    #     """Mark online payment failed and release the stock reserved for that order."""
    #     db = n()
    #     cur = db.cursor(dictionary=True)
    #     try:
    #         cur.execute('''SELECT orderid,payment_status,status FROM orders
    #                        WHERE orderid=%s AND userid=%s AND payment_method='RAZORPAY' FOR UPDATE''',
    #                     (orderid, userid))
    #         order = cur.fetchone()
    #         if not order: 
    #             return False, 'Order not found'
    #         if order['payment_status'] == 'paid': return False, 'This order is already paid'
    #         if order['status'] == 'cancelled': return True, 'Payment already marked as failed'

    #         cur.execute('SELECT productid,quantity FROM order_details WHERE orderid=%s', (orderid,))
    #         lines = cur.fetchall()
    #         for line in lines:
    #             cur.execute('UPDATE products SET quantity=quantity+%s WHERE productid=%s',
    #                         (line['quantity'], line['productid']))

    #         cur.execute('''UPDATE orders SET status='cancelled',payment_status='failed'
    #                        WHERE orderid=%s AND userid=%s''', (orderid, userid))
    #         cur.execute('''UPDATE transactions SET status='failed',failure_reason=%s
    #                        WHERE orderid=%s AND status='pending' ''', (reason[:255], orderid))
    #         cur.execute('''UPDATE payments SET status='failed' WHERE orderid=%s AND status='pending' ''', (orderid,))
    #         db.commit()
    #         return True, 'Payment failed and order was cancelled'
    #     except Exception as e:
    #         db.rollback()
    #         return False, str(e)
    #     finally:
    #         cur.close()
    #         db.close()

    # @staticmethod
    # def cancelPendingOrder(userid, orderid):
    #     return UserQueries.failPayment(userid, orderid, 'Customer cancelled payment')

    # @staticmethod
    # def completeCOD(userid, orderid):
    #     db = n(); 
    #     cur = db.cursor(dictionary=True)
    #     try:
    #         cur.execute('''SELECT orderid,status,payment_status FROM orders
    #                        WHERE orderid=%s AND userid=%s AND payment_method='COD' FOR UPDATE''', (orderid, userid))
    #         order = cur.fetchone()
    #         if not order: 
    #             return False, 'Order not found'
    #         if order['status'] == 'cancelled': 
    #             return False, 'Order is cancelled'

    #         # Stock was already reserved by createOrder().
    #         cur.execute("UPDATE orders SET status='processing',payment_status='pending' WHERE orderid=%s", (orderid,))
    #         cur.execute("UPDATE transactions SET status='pending' WHERE orderid=%s", (orderid,))
    #         cur.execute("UPDATE payments SET status='pending' WHERE orderid=%s", (orderid,))
    #         cur.execute('DELETE FROM cart WHERE userid=%s', (userid,))
    #         db.commit(); return True, 'Order placed successfully'
    #     except Exception as e:
    #         db.rollback(); 
    #         return False, str(e)
    #     finally:
    #         cur.close(); db.close()