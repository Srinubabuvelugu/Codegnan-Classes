from database.connection import DatabaseConnction


class UserDBQueries:
    @staticmethod
    def getAllProducts(id=None, category=None, search=None):
        db = DatabaseConnction(); cur = db.cursor(dictionary=True)
        try:
            sql = 'SELECT * FROM products WHERE is_active=1'; vals = []
            if id is not None:
                sql += ' AND productid=%s'; vals.append(id)
            if category:
                sql += ' AND category=%s'; vals.append(category)
            if search:
                sql += ' AND productname LIKE %s'; vals.append('%' + search + '%')
            cur.execute(sql + ' ORDER BY created_at DESC', tuple(vals))
            rows = cur.fetchone() if id is not None else cur.fetchall()
            return (True, rows) if rows else (False, 'No products found')
        except Exception as e:
            return False, str(e)
        finally:
            cur.close(); db.close()

    @staticmethod
    def addToCart(userid, productid, quantity):
        try: quantity = int(quantity)
        except (TypeError, ValueError): return False, 'Invalid quantity'
        if quantity < 1: return False, 'Quantity must be at least 1'
        db = DatabaseConnction(); cur = db.cursor(dictionary=True)
        try:
            cur.execute('SELECT quantity FROM products WHERE productid=%s AND is_active=1', (productid,)); p = cur.fetchone()
            if not p: return False, 'Product not found'
            cur.execute('SELECT cartid,quantity FROM cart WHERE userid=%s AND productid=%s', (userid, productid)); row = cur.fetchone()
            newqty = quantity + (int(row['quantity']) if row else 0)
            if newqty > int(p['quantity']): return False, 'Requested quantity exceeds available stock'
            if row: cur.execute('UPDATE cart SET quantity=%s WHERE cartid=%s', (newqty, row['cartid']))
            else: cur.execute('INSERT INTO cart(userid,productid,quantity) VALUES(%s,%s,%s)', (userid, productid, quantity))
            db.commit(); return True, 'Product added to cart'
        except Exception as e:
            db.rollback(); return False, str(e)
        finally:
            cur.close(); db.close()

    @staticmethod
    def getCartItems(userid):
        db = DatabaseConnction(); cur = db.cursor(dictionary=True)
        try:
            cur.execute('''SELECT c.cartid,c.userid,c.productid,c.quantity,p.productname,p.category,
                           p.saleprice,p.storedpath,p.quantity AS stock,
                           (c.quantity*p.saleprice) AS subtotal
                           FROM cart c JOIN products p ON p.productid=c.productid
                           WHERE c.userid=%s AND p.is_active=1 ORDER BY c.cartid DESC''', (userid,))
            return True, cur.fetchall()
        except Exception as e:
            return False, str(e)
        finally:
            cur.close(); db.close()

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
            db.commit(); return True, 'Quantity updated'
        except Exception as e:
            db.rollback(); return False, str(e)
        finally:
            cur.close(); db.close()

    @staticmethod
    def removeCartItem(cartid, userid):
        db = DatabaseConnction(); cur = db.cursor()
        try:
            cur.execute('DELETE FROM cart WHERE cartid=%s AND userid=%s', (cartid, userid))
            deleted = cur.rowcount
            db.commit(); return deleted > 0, ('Item removed' if deleted else 'Item not found')
        except Exception as e:
            db.rollback(); return False, str(e)
        finally:
            cur.close(); db.close()

    @staticmethod
    def getUser(userid):
        db = DatabaseConnction(); cur = db.cursor(dictionary=True)
        try:
            cur.execute('''SELECT userid,username,email,phone,gender,dateofbirth,
                           profilename,profilepath,is_active,created_at
                           FROM users WHERE userid=%s''', (userid,))
            return True, cur.fetchone()
        finally:
            cur.close(); db.close()

    @staticmethod
    def getOrders(userid):
        db = DatabaseConnction(); cur = db.cursor(dictionary=True)
        try:
            cur.execute('''SELECT o.orderid AS id,o.status,o.total_amount,o.payment_method,
                           o.payment_status,o.razorpay_payment_id AS payment_id,o.created_at,
                           COUNT(od.orderdetailid) AS item_count
                           FROM orders o LEFT JOIN order_details od ON od.orderid=o.orderid
                           WHERE o.userid=%s GROUP BY o.orderid ORDER BY o.created_at DESC''', (userid,))
            return True, cur.fetchall()
        finally:
            cur.close(); db.close()

    @staticmethod
    def getOrderDetails(orderid, userid):
        db = DatabaseConnction(); cur = db.cursor(dictionary=True)
        try:
            cur.execute('''SELECT o.*,o.orderid AS id,o.razorpay_payment_id AS payment_id,
                           u.username AS customer_name,u.phone AS customer_phone
                           FROM orders o JOIN users u ON u.userid=o.userid
                           WHERE o.orderid=%s AND o.userid=%s''', (orderid, userid))
            order = cur.fetchone()
            if not order: return False, 'Order not found'
            cur.execute('''SELECT od.*,p.productname AS product_name,p.storedpath AS image,p.category
                           FROM order_details od JOIN products p ON p.productid=od.productid
                           WHERE od.orderid=%s''', (orderid,))
            order['items'] = cur.fetchall()
            order['subtotal'] = sum((float(i['subtotal']) for i in order['items']), 0.0)
            order['shipping_charge'] = round(float(order['total_amount']) - order['subtotal'], 2)
            order['shipping'] = order['shipping_charge']
            order['delivery_address'] = order.get('address')
            return True, order
        finally:
            cur.close(); db.close()

    @staticmethod
    def createOrder(userid, address, method, razorpay_order_id=None):
        """Create order + order lines + transaction + legacy payment atomically.

        Stock is reserved/decremented in this same transaction. If an online payment
        later fails, failPayment() releases that reserved stock.
        """
        db = DatabaseConnction(); cur = db.cursor(dictionary=True)
        try:
            cur.execute('''SELECT c.productid,c.quantity,p.saleprice,p.quantity AS stock,p.productname
                           FROM cart c JOIN products p ON p.productid=c.productid
                           WHERE c.userid=%s AND p.is_active=1 FOR UPDATE''', (userid,))
            items = cur.fetchall()
            if not items: return False, 'Your cart is empty'

            subtotal = 0.0
            for item in items:
                if int(item['quantity']) > int(item['stock']):
                    return False, f"Insufficient stock for {item['productname']}"
                subtotal += float(item['saleprice']) * int(item['quantity'])

            shipping = round(subtotal * 0.01, 2)
            total = round(subtotal + shipping, 2)
            payment_status = 'pending'
            order_status = 'processing' if method == 'COD' else 'pending'

            cur.execute('''INSERT INTO orders
                           (userid,status,address,total_amount,payment_method,payment_status,razorpay_order_id)
                           VALUES(%s,%s,%s,%s,%s,%s,%s)''',
                        (userid, order_status, address, total, method, payment_status, razorpay_order_id))
            order_id = cur.lastrowid

            for item in items:
                cur.execute('''INSERT INTO order_details(orderid,productid,quantity,price)
                               VALUES(%s,%s,%s,%s)''',
                            (order_id, item['productid'], item['quantity'], item['saleprice']))
                # Reserve stock immediately so two users cannot order the same units.
                cur.execute('''UPDATE products SET quantity=quantity-%s
                               WHERE productid=%s AND quantity >= %s''',
                            (item['quantity'], item['productid'], item['quantity']))
                if cur.rowcount != 1:
                    raise RuntimeError(f"Stock changed for {item['productname']}; please try again")

            cur.execute('''INSERT INTO transactions
                           (userid,orderid,transaction_type,method,amount,status,gateway_order_id)
                           VALUES(%s,%s,'payment',%s,%s,%s,%s)''',
                        (userid, order_id, method, total, payment_status, razorpay_order_id))

            # Existing project table kept synchronized for backward compatibility.
            cur.execute('''INSERT INTO payments
                           (userid,orderid,method,amount,status,razorpay_order_id)
                           VALUES(%s,%s,%s,%s,%s,%s)''',
                        (userid, order_id, method, total, payment_status, razorpay_order_id))

            # COD is complete from the checkout perspective; Razorpay remains pending.
            if method == 'COD':
                cur.execute("UPDATE orders SET payment_status='pending' WHERE orderid=%s", (order_id,))

            db.commit()
            return True, {'order_id': order_id, 'amount': total, 'items': items}
        except Exception as e:
            db.rollback(); return False, str(e)
        finally:
            cur.close(); db.close()

    @staticmethod
    def markPaid(userid, orderid, razorpay_order_id, payment_id):
        db = DatabaseConnction(); cur = db.cursor(dictionary=True)
        try:
            cur.execute('''SELECT * FROM orders WHERE orderid=%s AND userid=%s
                           AND payment_method='RAZORPAY' FOR UPDATE''', (orderid, userid))
            order = cur.fetchone()
            if not order: return False, 'Order not found'
            if order['payment_status'] == 'paid': return True, 'Payment already verified'
            if order['razorpay_order_id'] != razorpay_order_id: return False, 'Payment order mismatch'

            cur.execute('''UPDATE orders SET payment_status='paid',status='processing',
                           razorpay_payment_id=%s WHERE orderid=%s''', (payment_id, orderid))
            if cur.rowcount != 1: return False, 'Could not update order payment status'

            cur.execute('''UPDATE transactions SET status='paid',gateway_payment_id=%s,
                           failure_reason=NULL WHERE orderid=%s AND gateway_order_id=%s''',
                        (payment_id, orderid, razorpay_order_id))
            if cur.rowcount != 1: return False, 'Transaction record not found'

            cur.execute('''UPDATE payments SET status='paid',razorpay_payment_id=%s
                           WHERE orderid=%s AND razorpay_order_id=%s''',
                        (payment_id, orderid, razorpay_order_id))
            if cur.rowcount != 1: return False, 'Payment record not found'

            cur.execute('DELETE FROM cart WHERE userid=%s', (userid,))
            db.commit(); return True, 'Payment verified and order placed successfully'
        except Exception as e:
            db.rollback(); return False, str(e)
        finally:
            cur.close(); db.close()

    @staticmethod
    def failPayment(userid, orderid, reason='Payment failed'):
        """Mark online payment failed and release the stock reserved for that order."""
        db = DatabaseConnction(); cur = db.cursor(dictionary=True)
        try:
            cur.execute('''SELECT orderid,payment_status,status FROM orders
                           WHERE orderid=%s AND userid=%s AND payment_method='RAZORPAY' FOR UPDATE''',
                        (orderid, userid))
            order = cur.fetchone()
            if not order: return False, 'Order not found'
            if order['payment_status'] == 'paid': return False, 'This order is already paid'
            if order['status'] == 'cancelled': return True, 'Payment already marked as failed'

            cur.execute('SELECT productid,quantity FROM order_details WHERE orderid=%s', (orderid,))
            lines = cur.fetchall()
            for line in lines:
                cur.execute('UPDATE products SET quantity=quantity+%s WHERE productid=%s',
                            (line['quantity'], line['productid']))

            cur.execute('''UPDATE orders SET status='cancelled',payment_status='failed'
                           WHERE orderid=%s AND userid=%s''', (orderid, userid))
            cur.execute('''UPDATE transactions SET status='failed',failure_reason=%s
                           WHERE orderid=%s AND status='pending' ''', (reason[:255], orderid))
            cur.execute('''UPDATE payments SET status='failed' WHERE orderid=%s AND status='pending' ''', (orderid,))
            db.commit(); return True, 'Payment failed and order was cancelled'
        except Exception as e:
            db.rollback(); return False, str(e)
        finally:
            cur.close(); db.close()

    @staticmethod
    def cancelPendingOrder(userid, orderid):
        return UserDBQueries.failPayment(userid, orderid, 'Customer cancelled payment')

    @staticmethod
    def completeCOD(userid, orderid):
        db = DatabaseConnction(); cur = db.cursor(dictionary=True)
        try:
            cur.execute('''SELECT orderid,status,payment_status FROM orders
                           WHERE orderid=%s AND userid=%s AND payment_method='COD' FOR UPDATE''', (orderid, userid))
            order = cur.fetchone()
            if not order: return False, 'Order not found'
            if order['status'] == 'cancelled': return False, 'Order is cancelled'

            # Stock was already reserved by createOrder().
            cur.execute("UPDATE orders SET status='processing',payment_status='pending' WHERE orderid=%s", (orderid,))
            cur.execute("UPDATE transactions SET status='pending' WHERE orderid=%s", (orderid,))
            cur.execute("UPDATE payments SET status='pending' WHERE orderid=%s", (orderid,))
            cur.execute('DELETE FROM cart WHERE userid=%s', (userid,))
            db.commit(); return True, 'Order placed successfully'
        except Exception as e:
            db.rollback(); return False, str(e)
        finally:
            cur.close(); db.close()
