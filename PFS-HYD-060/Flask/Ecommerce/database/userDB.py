
from database.connection import DatabaseConnection
from psycopg2.extras import RealDictCursor
from decimal import Decimal


class UserQueries:

    @staticmethod
    def addCartItem(product_id: int, userid: int, quantity: int):
        cursor = db_config = None

        try:
            db_config = DatabaseConnection()
            if db_config is None:
                return False, "Database connection failed"

            cursor = db_config.cursor()

            query = """UPDATE cart
                       SET quantity = quantity + %s
                       WHERE productid = %s AND userid = %s"""

            cursor.execute(query, (quantity, product_id, userid))

            if cursor.rowcount:
                db_config.commit()
                return True, "Cart Item Quantity Updated"

            query = """INSERT INTO cart(userid, productid, quantity)
                       VALUES(%s, %s, %s)"""

            cursor.execute(query, (userid, product_id, quantity))
            db_config.commit()

            return True, "Item added to cart"

        except Exception as e:
            if db_config:
                db_config.rollback()
            return False, f"Something wrong in database/userDB.UserQueries.addCartItem(): {e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    # get all cart items
    @staticmethod
    def getCartItems(userid: int):
        cursor = db_config = None

        try:
            db_config = DatabaseConnection()
            if db_config is None:
                return False, "Database connection failed"

            cursor = db_config.cursor(cursor_factory=RealDictCursor)

            query = """SELECT c.cartid, c.userid, c.productid, c.quantity,
                              p.productname, p.category, p.saleprice, p.storedpath,
                              c.quantity * p.saleprice AS subtotal
                       FROM cart c
                       INNER JOIN products p
                       ON c.productid = p.productid
                       WHERE c.userid = %s"""

            cursor.execute(query, (userid,))
            items = cursor.fetchall()

            return True, items

        except Exception as e:
            return False, f"Something wrong in database/userDB.UserQueries.getCartItems(): {e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    # update cart item quantity
    @staticmethod
    def updateCartItemQuantity(cartid: int, quantity: int):
        cursor = db_config = None

        try:
            db_config = DatabaseConnection()
            if db_config is None:
                return False, "Database connection failed"

            cursor = db_config.cursor()

            query = """UPDATE cart SET quantity = %s WHERE cartid = %s"""

            cursor.execute(query, (quantity, cartid))
            db_config.commit()

            return True, "quantity Updated"

        except Exception as e:
            if db_config:
                db_config.rollback()
            return False, f"Something wrong in database/userDB.UserQueries.updateCartItemQuantity(): {e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    # delete cart item
    @staticmethod
    def deleteCartItem(cartid: int):
        cursor = db_config = None

        try:
            db_config = DatabaseConnection()
            if db_config is None:
                return False, "Database connection failed"

            cursor = db_config.cursor()

            query = """DELETE FROM cart WHERE cartid = %s"""

            cursor.execute(query, (cartid,))
            db_config.commit()

            return True, "Item deleted"

        except Exception as e:
            if db_config:
                db_config.rollback()
            return False, f"Something wrong in database/userDB.UserQueries.deleteCartItem(): {e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    # create order
    @staticmethod
    def createOrder(
        userid: int,
        address: str,
        payment_method: str,
        razorpay_order_id: str = None,
        razorpay_payment_id: str = None
    ):
        db_config = cursor = None

        try:
            db_config = DatabaseConnection()
            if db_config is None:
                return False, "Database connection failed"

            cursor = db_config.cursor(cursor_factory=RealDictCursor)

            query = """SELECT c.cartid, c.userid, c.quantity,
                              p.productname, p.productid,
                              p.quantity AS stock, p.saleprice
                       FROM cart c
                       JOIN products p ON c.productid = p.productid
                       WHERE c.userid = %s
                       FOR UPDATE"""

            cursor.execute(query, (userid,))
            items = cursor.fetchall()

            if not items:
                return False, "Cart is empty"

            # check each product stock
            sub_total = 0

            for item in items:
                if item['quantity'] > item['stock']:
                    return False, f"{item['productname']} current stock is not available"

                sub_total += item['quantity'] * item['saleprice']

            # reduce product stocks
            for item in items:
                query = """UPDATE products
                           SET quantity = quantity - %s
                           WHERE productid = %s"""

                cursor.execute(query, (item['quantity'], item['productid']))

            # calculate shipping
            shipping = sub_total * Decimal('0.01')
            total = sub_total + shipping

            # add order record
            query = """INSERT INTO orders(userid, status, address, total)
                       VALUES(%s, %s, %s, %s)
                       RETURNING orderid"""

            cursor.execute(query, (userid, "pending", address, total))
            orderid = cursor.fetchone()['orderid']

            # add items to order details
            for item in items:
                query = """INSERT INTO order_details
                           (orderid, productid, quantity, price)
                           VALUES(%s, %s, %s, %s)"""

                cursor.execute(
                    query,
                    (
                        orderid,
                        item['productid'],
                        item['quantity'],
                        item['saleprice']
                    )
                )

            # insert payment record
            status = "pending"
            method = payment_method.lower()

            query = """INSERT INTO payments
                       (userid, orderid, status, method, amount,
                        razorpay_order_id, razorpay_id)
                       VALUES(%s, %s, %s, %s, %s, %s, %s)"""

            cursor.execute(
                query,
                (
                    userid,
                    orderid,
                    status,
                    'cash' if method == 'cod' else method,
                    total,
                    razorpay_order_id,
                    razorpay_payment_id
                )
            )

            # clear cart
            cursor.execute(
                "DELETE FROM cart WHERE userid = %s",
                (userid,)
            )

            db_config.commit()

            return True, {
                "order_id": orderid,
                "amount": total
            }

        except Exception as e:
            if db_config:
                db_config.rollback()

            return False, f"Something wrong in database/userDB.py/UserQueries.createOrder(): {e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    @staticmethod
    def getUser(userid):
        db = cur = None

        try:
            db = DatabaseConnection()
            if db is None:
                return False, "Database connection failed"

            cur = db.cursor(cursor_factory=RealDictCursor)

            query = """SELECT userid, username, email, phone, gender,
                              dateofbirth, profilename, profilepath,
                              is_active, created_at
                       FROM users WHERE userid = %s"""

            cur.execute(query, (userid,))
            return True, cur.fetchone()

        except Exception as e:
            return False, str(e)

        finally:
            if cur:
                cur.close()
            if db:
                db.close()

    @staticmethod
    def getOrders(userid):
        db = cur = None

        try:
            db = DatabaseConnection()
            if db is None:
                return False, "Database connection failed"

            cur = db.cursor(cursor_factory=RealDictCursor)

            query = """SELECT
                           o.orderid AS id,
                           o.status,
                           o.total AS total_amount,
                           o.address,
                           o.created_at,
                           p.method AS payment_method,
                           p.status AS payment_status,
                           p.razorpay_id AS payment_id
                       FROM orders o
                       LEFT JOIN payments p ON o.orderid = p.orderid
                       WHERE o.userid = %s
                       ORDER BY o.created_at DESC"""

            cur.execute(query, (userid,))
            return True, cur.fetchall()

        except Exception as e:
            return False, str(e)

        finally:
            if cur:
                cur.close()
            if db:
                db.close()

    @staticmethod
    def getOrderDetails(orderid, userid):
        db = cur = None

        try:
            db = DatabaseConnection()
            if db is None:
                return False, "Database connection failed"

            cur = db.cursor(cursor_factory=RealDictCursor)

            query = """SELECT
                           o.*,
                           o.orderid AS id,
                           p.method AS payment_method,
                           p.status AS payment_status,
                           p.razorpay_id AS payment_id,
                           p.razorpay_order_id,
                           p.amount AS total_amount,
                           u.username AS customer_name,
                           u.phone AS customer_phone
                       FROM orders o
                       JOIN users u ON u.userid = o.userid
                       LEFT JOIN payments p ON p.orderid = o.orderid
                       WHERE o.orderid = %s AND o.userid = %s"""

            cur.execute(query, (orderid, userid))
            order = cur.fetchone()

            if not order:
                return False, "Order not found"

            query = """SELECT
                           od.*,
                           p.productname AS product_name,
                           p.storedpath AS image,
                           p.category
                       FROM order_details od
                       JOIN products p ON p.productid = od.productid
                       WHERE od.orderid = %s"""

            cur.execute(query, (orderid,))
            order['items'] = cur.fetchall()

            # calculate subtotal
            order['subtotal'] = sum(
                float(item['subtotal']) for item in order['items']
            )

            # calculate shipping
            order['shipping'] = (
                float(order['total']) - order['subtotal']
            )

            order['delivery_address'] = order.get('address')

            return True, order

        except Exception as e:
            return False, str(e)

        finally:
            if cur:
                cur.close()
            if db:
                db.close()

    @staticmethod
    def markPaid(userid, orderid, razorpay_order_id, payment_id):
        db = cur = None

        try:
            db = DatabaseConnection()
            if db is None:
                return False, "Database connection failed"

            cur = db.cursor(cursor_factory=RealDictCursor)

            query = """SELECT *
                       FROM payments
                       WHERE orderid = %s
                       AND userid = %s
                       AND LOWER(method) = 'razorpay'
                       FOR UPDATE"""

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

            query = """UPDATE payments
                       SET status = 'paid',
                           razorpay_id = %s
                       WHERE orderid = %s
                       AND userid = %s"""

            cur.execute(query, (payment_id, orderid, userid))

            if cur.rowcount != 1:
                db.rollback()
                return False, "Could not update payment status"

            # remove cart items after successful verification
            cur.execute(
                "DELETE FROM cart WHERE userid = %s",
                (userid,)
            )

            db.commit()

            return True, "Payment verified successfully"

        except Exception as e:
            if db:
                db.rollback()
            return False, str(e)

        finally:
            if cur:
                cur.close()
            if db:
                db.close()

    @staticmethod
    def failPayment(userid, orderid, reason='Payment failed'):
        db = cur = None

        try:
            db = DatabaseConnection()
            if db is None:
                return False, "Database connection failed"

            cur = db.cursor(cursor_factory=RealDictCursor)

            # get payment details
            query = """SELECT *
                       FROM payments
                       WHERE orderid = %s
                       AND userid = %s
                       AND LOWER(method) = 'razorpay'
                       FOR UPDATE"""

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

            # restore product stock
            query = """SELECT productid, quantity
                       FROM order_details
                       WHERE orderid = %s"""

            cur.execute(query, (orderid,))
            items = cur.fetchall()

            for item in items:
                query = """UPDATE products
                           SET quantity = quantity + %s
                           WHERE productid = %s"""

                cur.execute(
                    query,
                    (item['quantity'], item['productid'])
                )

            # update payment status
            query = """UPDATE payments
                       SET status = 'failed'
                       WHERE orderid = %s AND userid = %s"""

            cur.execute(query, (orderid, userid))

            # cancel order
            query = """UPDATE orders
                       SET status = 'cancelled'
                       WHERE orderid = %s AND userid = %s"""

            cur.execute(query, (orderid, userid))

            db.commit()

            return True, "Payment failed and order cancelled"

        except Exception as e:
            if db:
                db.rollback()
            return False, str(e)

        finally:
            if cur:
                cur.close()
            if db:
                db.close()

    @staticmethod
    def cancelPendingOrder(userid, orderid):
        return UserQueries.failPayment(
            userid,
            orderid,
            "Customer cancelled payment"
        )
