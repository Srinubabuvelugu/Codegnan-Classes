
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
            


    # create order
    @staticmethod
    def createOrder(userid:int, address:str,payment_method:str, razorpay_order_id:str=None, razorpay_payment_id:str=None):
        try:
            db_config = DatabaseConnction()
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
            method = payment_method.upper()
            
            query = """insert into payments(userid, orderid, status, method, amount, razorpay_order_id, razorpay_payment_id)
                    values(%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (userid, orderid,status, method, sub_total +shipping,razorpay_order_id, razorpay_payment_id ))

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
    def updateCartQuantity(cartid, quantity, userid):
        try: quantity = int(quantity)
        except (ValueError, TypeError): return False, 'Invalid quantity'
        if quantity < 1: return False, 'Quantity must be at least 1'
        db = DatabaseConnction(); cur = db.cursor(dictionary=True)
        try:
            cur.execute('''SELECT p.quantity AS stock FROM cart c
                           JOIN products p ON p.productid=c.productid
                           WHERE c.cartid=%s AND c.userid=%s''', (cartid, userid))
            row = cur.fetchone()
            if not row: return False, 'Cart item not found'
            if quantity > int(row['stock']): return False, 'Quantity exceeds available stock'
            cur.execute('UPDATE cart SET quantity=%s WHERE cartid=%s AND userid=%s', (quantity, cartid, userid))
            db.commit()
            return True, 'Quantity updated'
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            cur.close()
            db.close()

    @staticmethod
    def removeCartItem(cartid, userid):
        db = DatabaseConnction(); cur = db.cursor()
        try:
            cur.execute('DELETE FROM cart WHERE cartid=%s AND userid=%s', (cartid, userid))
            deleted = cur.rowcount
            db.commit(); return deleted > 0, ('Item removed' if deleted else 'Item not found')
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            cur.close()
            db.close()

    @staticmethod
    def getUser(userid):
        db = DatabaseConnction()
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
        db = DatabaseConnction()
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
        db = DatabaseConnction()
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

        db = DatabaseConnction()
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

        db = DatabaseConnction()
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
    #     db = DatabaseConnction()
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
    #     db = DatabaseConnction(); 
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