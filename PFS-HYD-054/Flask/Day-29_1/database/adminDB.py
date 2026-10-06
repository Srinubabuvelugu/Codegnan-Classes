from database.connection import DatabaseConnction

class AdminDBQueries:
    @staticmethod
    def insertProductRecord(product_data):
        db=DatabaseConnction(); cur=db.cursor()
        try: cur.execute('INSERT INTO products(productname,description,category,quantity,buyprice,saleprice,imgname,storedpath) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',product_data); db.commit(); return True,'Product added'
        except Exception as e: db.rollback(); return False,str(e)
        finally: cur.close(); db.close()
    @staticmethod
    def getAllProducts(id=None):
        db=DatabaseConnction(); cur=db.cursor(dictionary=True)
        try:
            if id: cur.execute('SELECT * FROM products WHERE productid=%s',(id,)); rows=cur.fetchone()
            else: cur.execute('SELECT * FROM products ORDER BY created_at DESC'); rows=cur.fetchall()
            return (True,rows) if rows else (False,'No products found')
        except Exception as e:return False,str(e)
        finally:cur.close();db.close()
    @staticmethod
    def updateProduct(productid,data):
        db=DatabaseConnction();cur=db.cursor()
        try:cur.execute('UPDATE products SET productname=%s,description=%s,category=%s,quantity=%s,buyprice=%s,saleprice=%s WHERE productid=%s',(*data,productid));db.commit();return True,'Product updated'
        except Exception as e:db.rollback();return False,str(e)
        finally:cur.close();db.close()
    @staticmethod
    def deleteProduct(productid):
        db=DatabaseConnction();cur=db.cursor()
        try:cur.execute('UPDATE products SET is_active=0 WHERE productid=%s',(productid,));db.commit();return True,'Product deactivated'
        except Exception as e:db.rollback();return False,str(e)
        finally:cur.close();db.close()
    @staticmethod
    def getUsers():
        db=DatabaseConnction();cur=db.cursor(dictionary=True)
        try:cur.execute("SELECT userid AS id,username AS name,email,role,phone,is_active,created_at FROM users ORDER BY created_at DESC");return True,cur.fetchall()
        finally:cur.close();db.close()
    @staticmethod
    def getOrders(search=None,status=None):
        db=DatabaseConnction();cur=db.cursor(dictionary=True)
        try:
            sql='''SELECT o.orderid AS id,u.username customer_name,u.email customer_email,o.total_amount,o.status,o.payment_method,o.payment_status,o.created_at,COUNT(*) item_count FROM orders o JOIN users u ON u.userid=o.userid LEFT JOIN order_details od ON od.orderid=o.orderid WHERE 1=1''';vals=[]
            if search:sql+=' AND (CAST(o.orderid AS CHAR) LIKE %s OR u.username LIKE %s OR u.email LIKE %s)';vals += ['%'+search+'%']*3
            if status:sql+=' AND o.status=%s';vals.append(status.lower())
            sql+=' GROUP BY o.orderid ORDER BY o.created_at DESC';cur.execute(sql,tuple(vals));return True,cur.fetchall()
        finally:cur.close();db.close()
    @staticmethod
    def getOrderDetails(orderid):
        db=DatabaseConnction();cur=db.cursor(dictionary=True)
        try:
            cur.execute('SELECT o.*,o.orderid AS id,o.razorpay_payment_id AS payment_id,u.username customer_name,u.email customer_email,u.phone customer_phone FROM orders o JOIN users u ON u.userid=o.userid WHERE o.orderid=%s',(orderid,));order=cur.fetchone()
            if not order:return False,'Order not found'
            cur.execute('SELECT od.*,p.productname AS product_name,p.storedpath AS image,p.category FROM order_details od JOIN products p ON p.productid=od.productid WHERE od.orderid=%s',(orderid,));order['items']=cur.fetchall();order['subtotal']=sum((float(i['subtotal']) for i in order['items']),0.0);order['shipping']=round(float(order['total_amount'])-order['subtotal'],2);return True,order
        finally:cur.close();db.close()
    @staticmethod
    def updateOrderStatus(orderid,status):
        if status not in {'pending','processing','shipped','delivered','cancelled'}:return False,'Invalid status'
        db=DatabaseConnction();cur=db.cursor(dictionary=True)
        try:
            cur.execute('SELECT status,payment_status FROM orders WHERE orderid=%s FOR UPDATE',(orderid,)); order=cur.fetchone()
            if not order:return False,'Order not found'
            if order['status']=='cancelled' and status!='cancelled':return False,'Cancelled order cannot be reopened'
            if status=='cancelled' and order['status']!='cancelled':
                cur.execute('SELECT productid,quantity FROM order_details WHERE orderid=%s',(orderid,))
                for line in cur.fetchall():
                    cur.execute('UPDATE products SET quantity=quantity+%s WHERE productid=%s',(line['quantity'],line['productid']))
                cur.execute("UPDATE orders SET status='cancelled',payment_status=CASE WHEN payment_status='paid' THEN payment_status ELSE 'failed' END WHERE orderid=%s",(orderid,))
                cur.execute("UPDATE transactions SET status='failed',failure_reason='Order cancelled by admin' WHERE orderid=%s AND status='pending'",(orderid,))
                cur.execute("UPDATE payments SET status='failed' WHERE orderid=%s AND status='pending'",(orderid,))
            else:
                cur.execute('UPDATE orders SET status=%s WHERE orderid=%s',(status,orderid))
            db.commit();return True,'Order status updated'
        except Exception as e:
            db.rollback();return False,str(e)
        finally:cur.close();db.close()
    @staticmethod
    def getProducts(
        search='',
        category='',
        status='',
        stock='',
        min_price=0,
        max_price=0,
        page=1,
        per_page=10
    ):

        db = DatabaseConnction()
        cur = db.cursor(dictionary=True)

        try:

            query = """
                SELECT *
                FROM products
                WHERE 1=1
            """

            params = []

            # Search
            if search:
                query += """
                    AND (
                        productname LIKE %s
                        OR description LIKE %s
                    )
                """

                search_value = f"%{search}%"

                params.extend([
                    search_value,
                    search_value
                ])

            # Category
            if category:
                query += " AND category = %s"
                params.append(category)

            # Status
            if status == 'active':
                query += " AND is_active = TRUE"

            elif status == 'inactive':
                query += " AND is_active = FALSE"

            # Stock
            if stock == 'available':
                query += " AND quantity > 0"

            elif stock == 'out':
                query += " AND quantity = 0"

            elif stock == 'low':
                query += " AND quantity > 0 AND quantity <= 5"

            # Price
            if min_price:
                query += " AND saleprice >= %s"
                params.append(min_price)

            if max_price:
                query += " AND saleprice <= %s"
                params.append(max_price)

            # Total count
            count_query = f"""
                SELECT COUNT(*) as total
                FROM ({query}) AS filtered_products
            """

            cur.execute(count_query, params)
            total = cur.fetchone()['total']

            # Pagination
            offset = (page - 1) * per_page

            query += """
                ORDER BY productid DESC
                LIMIT %s OFFSET %s
            """

            params.extend([
                per_page,
                offset
            ])

            cur.execute(query, params)

            products = cur.fetchall()

            # Categories
            cur.execute("""
                SELECT DISTINCT category
                FROM products
                WHERE category IS NOT NULL
                AND category != ''
                ORDER BY category
            """)

            categories = [row['category'] for row in cur.fetchall()]

            return {
                'products': products,
                'total': total,
                'categories': categories
            }

        except Exception as e:

            import traceback

            print("====================================")
            print("GET PRODUCTS ERROR")
            print("====================================")
            print(e)
            traceback.print_exc()
            print("====================================")

            return {
                'products': [],
                'total': 0,
                'categories': []
            }

        finally:
            cur.close()
            db.close()
    @staticmethod
    def deactivateProduct(product_id):

        db = DatabaseConnction()
        cur = db.cursor()

        try:

            cur.execute("""
                UPDATE products
                SET is_active = FALSE
                WHERE productid = %s
            """, (product_id,))

            db.commit()

            return cur.rowcount > 0

        except Exception as e:

            db.rollback()
            print(e)

            return False

        finally:

            cur.close()
            db.close()

    @staticmethod
    def activateProduct(product_id):

        db = DatabaseConnction()
        cur = db.cursor()

        try:

            cur.execute("""
                UPDATE products
                SET is_active = TRUE
                WHERE productid = %s
            """, (product_id,))

            db.commit()

            return cur.rowcount > 0

        except Exception as e:

            db.rollback()
            print(e)

            return False

        finally:

            cur.close()
            db.close()




    # ---------------------------------------------------------
    # GET ORDERS
    # ---------------------------------------------------------
    @staticmethod
    def getOrders(search='', status='', page=1, per_page=10):

        db = None
        cur = None

        try:
            db = DatabaseConnction()
            cur = db.cursor(dictionary=True)

            query = """
                SELECT
                    o.orderid,
                    o.userid,
                    o.status,
                    o.address,
                    o.total_amount,
                    o.payment_method,
                    o.payment_status,
                    o.razorpay_order_id,
                    o.razorpay_payment_id,
                    o.created_at,
                    o.updated_at,

                    u.username AS customer_name,
                    u.email AS customer_email,

                    COUNT(od.orderdetailid) AS item_count

                FROM orders o

                LEFT JOIN users u
                    ON o.userid = u.userid

                LEFT JOIN order_details od
                    ON o.orderid = od.orderid

                WHERE 1 = 1
            """

            params = []

            # -----------------------------
            # SEARCH
            # -----------------------------
            if search:

                if search.isdigit():

                    query += """
                        AND (
                            o.orderid = %s
                            OR u.username LIKE %s
                            OR u.email LIKE %s
                        )
                    """

                    params.append(int(search))
                    params.append(f"%{search}%")
                    params.append(f"%{search}%")

                else:

                    query += """
                        AND (
                            u.username LIKE %s
                            OR u.email LIKE %s
                        )
                    """

                    params.append(f"%{search}%")
                    params.append(f"%{search}%")

            # -----------------------------
            # STATUS FILTER
            # -----------------------------
            if status:

                query += """
                    AND o.status = %s
                """

                params.append(status)

            # -----------------------------
            # GROUP
            # -----------------------------
            query += """
                GROUP BY
                    o.orderid,
                    o.userid,
                    o.status,
                    o.address,
                    o.total_amount,
                    o.payment_method,
                    o.payment_status,
                    o.razorpay_order_id,
                    o.razorpay_payment_id,
                    o.created_at,
                    o.updated_at,
                    u.username,
                    u.email
            """

            # -----------------------------
            # COUNT
            # -----------------------------
            count_query = f"""
                SELECT COUNT(*) AS total
                FROM (
                    {query}
                ) AS filtered_orders
            """

            cur.execute(count_query, tuple(params))

            count_row = cur.fetchone()
            total = count_row['total']

            # -----------------------------
            # PAGINATION
            # -----------------------------
            offset = (page - 1) * per_page

            query += """
                ORDER BY o.orderid DESC
                LIMIT %s OFFSET %s
            """

            params.append(per_page)
            params.append(offset)

            cur.execute(query, tuple(params))

            orders = cur.fetchall()

            return {
                'orders': orders,
                'total': total
            }

        except Exception as e:

            print("====================================")
            print("GET ORDERS ERROR")
            print("====================================")
            print(e)

            import traceback
            traceback.print_exc()

            return {
                'orders': [],
                'total': 0
            }

        finally:

            if cur:
                cur.close()

            if db:
                db.close()


    # ---------------------------------------------------------
    # GET SINGLE ORDER
    # ---------------------------------------------------------
    @staticmethod
    def getOrderById(order_id):

        db = None
        cur = None

        try:

            db = DatabaseConnction()
            cur = db.cursor(dictionary=True)

            query = """
                SELECT
                    o.orderid,
                    o.userid,
                    o.status,
                    o.address,
                    o.total_amount,
                    o.payment_method,
                    o.payment_status,
                    o.razorpay_order_id,
                    o.razorpay_payment_id,
                    o.created_at,
                    o.updated_at,

                    u.username AS customer_name,
                    u.email AS customer_email,
                    u.phone,
                    u.gender,
                    u.dateofbirth

                FROM orders o

                LEFT JOIN users u
                    ON o.userid = u.userid

                WHERE o.orderid = %s
            """

            cur.execute(query, (order_id,))

            order = cur.fetchone()

            return order

        except Exception as e:

            print("GET ORDER ERROR:", e)

            import traceback
            traceback.print_exc()

            return None

        finally:

            if cur:
                cur.close()

            if db:
                db.close()


    # ---------------------------------------------------------
    # GET ORDER ITEMS
    # ---------------------------------------------------------
    @staticmethod
    def getOrderItems(order_id):

        db = None
        cur = None

        try:

            db = DatabaseConnction()
            cur = db.cursor(dictionary=True)

            query = """
                SELECT
                    od.orderdetailid,
                    od.orderid,
                    od.productid,
                    od.quantity,
                    od.price,
                    od.subtotal,

                    p.productname,
                    p.imgname,
                    p.storedpath

                FROM order_details od

                LEFT JOIN products p
                    ON od.productid = p.productid

                WHERE od.orderid = %s

                ORDER BY od.orderdetailid ASC
            """

            cur.execute(query, (order_id,))

            items = cur.fetchall()

            return items

        except Exception as e:

            print("GET ORDER ITEMS ERROR:", e)

            import traceback
            traceback.print_exc()

            return []

        finally:

            if cur:
                cur.close()

            if db:
                db.close()


    # ---------------------------------------------------------
    # UPDATE ORDER STATUS
    # ---------------------------------------------------------
    @staticmethod
    def updateOrderStatus(order_id, status):

        db = None
        cur = None

        try:

            db = DatabaseConnction()
            cur = db.cursor(dictionary=True)

            allowed_statuses = [
                'PENDING',
                'PROCESSING',
                'SHIPPED',
                'DELIVERED',
                'CANCELLED'
            ]

            if status not in allowed_statuses:
                return False

            query = """
                UPDATE orders
                SET
                    status = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE orderid = %s
            """

            cur.execute(query, (status, order_id))

            db.commit()

            return cur.rowcount > 0

        except Exception as e:

            if db:
                db.rollback()

            print("UPDATE ORDER STATUS ERROR:", e)

            import traceback
            traceback.print_exc()

            return False

        finally:

            if cur:
                cur.close()

            if db:
                db.close()


# User-management queries used by the admin routes.
def _admin_get_user_by_id(user_id):
    db=DatabaseConnction(); cur=db.cursor(dictionary=True)
    try:
        cur.execute('SELECT userid AS id,username AS name,email,phone,role,is_active,created_at FROM users WHERE userid=%s',(user_id,))
        user=cur.fetchone()
        return (True,user) if user else (False,'User not found')
    except Exception as e: return False,str(e)
    finally: cur.close(); db.close()


def _admin_get_user_details(user_id):
    db=DatabaseConnction(); cur=db.cursor(dictionary=True)
    try:
        cur.execute(
            "SELECT userid AS id,username AS name,email,role,phone,is_active,created_at FROM users WHERE userid=%s",
            (user_id,)
        )
        user=cur.fetchone()
        return (True,user) if user else (False,'User not found')
    except Exception as e:
        return False,str(e)
    finally:
        cur.close(); db.close()


def _admin_update_user(user_id,data):
    if data.get('role') not in {'user','admin'}: return False,'Invalid role'
    if not data.get('username') or not data.get('email'): return False,'Name and email are required'
    db=DatabaseConnction(); cur=db.cursor()
    try:
        cur.execute('''UPDATE users SET username=%s,email=%s,phone=%s,role=%s WHERE userid=%s''',
                    (data['username'],data['email'],data.get('phone') or None,data['role'],user_id))
        if cur.rowcount != 1: return False,'User not found'
        db.commit(); return True,'User updated successfully'
    except Exception as e:
        db.rollback(); return False,str(e)
    finally: cur.close(); db.close()

AdminDBQueries.getUserById = staticmethod(_admin_get_user_by_id)
AdminDBQueries.getUserDetails = staticmethod(_admin_get_user_details)
AdminDBQueries.updateUser = staticmethod(_admin_update_user)
