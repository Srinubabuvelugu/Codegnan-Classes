
from database.connection import DatabaseConnection
from psycopg2.extras import RealDictCursor


class AdminQueries:

    # INSERT PRODUCT
    @staticmethod
    def insertProductRecord(product_data: tuple[str | int]):
        db_config = cursor = None
        try:
            db_config = DatabaseConnection()
            if db_config is None:
                return False, "Database connection failed"

            cursor = db_config.cursor()

            query = """
                INSERT INTO products(
                    productname, description, category,
                    saleprice, quantity, imgname, storedpath
                )
                VALUES(%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, product_data)
            db_config.commit()

            return True, "Product Added"

        except Exception as e:
            if db_config:
                db_config.rollback()
            return False, f"Something wrong in database/adminDB.AdminQueries.insertProductRecord(): {e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    # GET ALL PRODUCTS BASED ON CATEGORY, PRODUCT NAME, PRODUCT ID
    @staticmethod
    def getAllProducts(product_name: str = None, product_id: int = None,
                       category: str = None, page_no: int = 1, per_page: int = 7):
        db_config = cursor = None
        try:
            db_config = DatabaseConnection()
            if db_config is None:
                return False, "Database connection failed"

            cursor = db_config.cursor(cursor_factory=RealDictCursor)

            query = "SELECT * FROM products WHERE 1=1"
            values = []

            if product_name:
                query += " AND productname LIKE %s"
                values.append(f"%{product_name}%")

            if category:
                query += " AND category = %s"
                values.append(category)

            if product_id:
                query += " AND productid = %s"
                values.append(product_id)

            offset = (page_no - 1) * per_page

            query += " ORDER BY updated_at DESC LIMIT %s OFFSET %s"
            values.extend([per_page, offset])

            cursor.execute(query, values)

            data = cursor.fetchone() if product_id else cursor.fetchall()

            return True, data

        except Exception as e:
            return False, f"Something wrong in database/adminDB.AdminQueries.getAllProducts(): {e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    # GET ALL CATEGORIES
    @staticmethod
    def getAllCategories():
        db_config = cursor = None
        try:
            db_config = DatabaseConnection()
            if db_config is None:
                return False, "Database connection failed"

            cursor = db_config.cursor()

            query = "SELECT DISTINCT category FROM products"
            cursor.execute(query)

            data = cursor.fetchall()

            return True, data

        except Exception as e:
            return False, f"Something wrong in database/adminDB.AdminQueries.getAllCategories(): {e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    # UPDATE PRODUCT RECORD
    @staticmethod
    def updateProductRecord(product_data: tuple[str | int]):
        db_config = cursor = None
        try:
            db_config = DatabaseConnection()
            if db_config is None:
                return False, "Database connection failed"

            cursor = db_config.cursor()

            query = """
                UPDATE products
                SET productname = %s,
                    description = %s,
                    category = %s,
                    saleprice = %s,
                    quantity = %s,
                    imgname = %s,
                    storedpath = %s
                WHERE productid = %s
            """

            cursor.execute(query, product_data)
            db_config.commit()

            return True, "Product Updated"

        except Exception as e:
            if db_config:
                db_config.rollback()
            return False, f"Something wrong in database/adminDB.AdminQueries.updateProductRecord(): {e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    # GET ALL USERS
    @staticmethod
    def getAllUsers():
        db_config = cursor = None
        try:
            db_config = DatabaseConnection()
            if db_config is None:
                return False, "Database connection failed"

            cursor = db_config.cursor(cursor_factory=RealDictCursor)

            cursor.execute("SELECT * FROM users")
            data = cursor.fetchall()

            return True, data

        except Exception as e:
            return False, f"Something wrong in database/adminDB.AdminQueries.getAllUsers(): {e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    # UPDATE PRODUCT DATA
    @staticmethod
    def updateProductData(product_data, img=False):
        db = cursor = None
        try:
            db = DatabaseConnection()
            if db is None:
                return False, "Database connection failed"

            cursor = db.cursor()

            if img:
                query = """
                    UPDATE products
                    SET productname=%s,
                        description=%s,
                        category=%s,
                        quantity=%s,
                        saleprice=%s,
                        imgname=%s,
                        storedpath=%s
                    WHERE productid=%s
                """
            else:
                query = """
                    UPDATE products
                    SET productname=%s,
                        description=%s,
                        category=%s,
                        quantity=%s,
                        saleprice=%s
                    WHERE productid=%s
                """

            cursor.execute(query, product_data)
            db.commit()

            return True, "Product Updated"

        except Exception as e:
            if db:
                db.rollback()
            return False, f"Unable to update product: {e}"

        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    # DELETE PRODUCT (SOFT DELETE)
    @staticmethod
    def deleteProduct(productid):
        db = cursor = None
        try:
            db = DatabaseConnection()
            if db is None:
                return False, "Database connection failed"

            cursor = db.cursor()

            cursor.execute(
                "UPDATE products SET is_active=FALSE WHERE productid=%s",
                (productid,)
            )
            db.commit()

            if cursor.rowcount == 0:
                return False, "Product not found"

            return True, "Product deactivated"

        except Exception as e:
            if db:
                db.rollback()
            return False, f"Unable to deactivate product: {e}"

        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    # DEACTIVATE PRODUCT
    @staticmethod
    def deactivateProduct(product_id):
        db = cursor = None
        try:
            db = DatabaseConnection()
            if db is None:
                return False

            cursor = db.cursor()

            cursor.execute(
                "UPDATE products SET is_active=FALSE WHERE productid=%s",
                (product_id,)
            )
            db.commit()

            return cursor.rowcount > 0

        except Exception as e:
            if db:
                db.rollback()
            print("DEACTIVATE PRODUCT ERROR:", e)
            return False

        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    # ACTIVATE PRODUCT
    @staticmethod
    def activateProduct(product_id):
        db = cursor = None
        try:
            db = DatabaseConnection()
            if db is None:
                return False

            cursor = db.cursor()

            cursor.execute(
                "UPDATE products SET is_active=TRUE WHERE productid=%s",
                (product_id,)
            )
            db.commit()

            return cursor.rowcount > 0

        except Exception as e:
            if db:
                db.rollback()
            print("ACTIVATE PRODUCT ERROR:", e)
            return False

        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    # CHANGE PRODUCT ACTIVATE STATUS
    @staticmethod
    def chengeProductActivateStatus(product_id, active=False):
        if active:
            success = AdminQueries.activateProduct(product_id)
            return success, "Product activated" if success else "Unable to activate product"

        success = AdminQueries.deactivateProduct(product_id)
        return success, "Product deactivated" if success else "Unable to deactivate product"

    # GET PRODUCTS WITH FILTERS AND PAGINATION
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
        db = cursor = None
        try:
            db = DatabaseConnection()
            if db is None:
                return {
                    'products': [],
                    'total': 0,
                    'categories': []
                }

            cursor = db.cursor(cursor_factory=RealDictCursor)

            query = "SELECT * FROM products WHERE 1=1"
            params = []

            if search:
                query += " AND (productname LIKE %s OR description LIKE %s)"
                search_value = f"%{search}%"
                params.extend([search_value, search_value])

            if category:
                query += " AND category=%s"
                params.append(category)

            if status == 'active':
                query += " AND is_active=TRUE"
            elif status == 'inactive':
                query += " AND is_active=FALSE"

            if stock == 'available':
                query += " AND quantity > 0"
            elif stock == 'out':
                query += " AND quantity = 0"
            elif stock == 'low':
                query += " AND quantity > 0 AND quantity <= 5"

            if min_price:
                query += " AND saleprice >= %s"
                params.append(min_price)

            if max_price:
                query += " AND saleprice <= %s"
                params.append(max_price)

            count_query = f"""
                SELECT COUNT(*) AS total
                FROM ({query}) AS filtered_products
            """

            cursor.execute(count_query, tuple(params))
            total = cursor.fetchone()['total']

            if page < 1:
                page = 1

            offset = (page - 1) * per_page

            query += " ORDER BY productid DESC LIMIT %s OFFSET %s"
            params.extend([per_page, offset])

            cursor.execute(query, tuple(params))
            products = cursor.fetchall()

            cursor.execute("""
                SELECT DISTINCT category
                FROM products
                WHERE category IS NOT NULL AND category != ''
                ORDER BY category
            """)

            categories = [row['category'] for row in cursor.fetchall()]

            return {
                'products': products,
                'total': total,
                'categories': categories
            }

        except Exception as e:
            print("GET PRODUCTS ERROR:", e)
            return {
                'products': [],
                'total': 0,
                'categories': []
            }

        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    # ---------------------------------------------------------
    # USERS
    # ---------------------------------------------------------

    # GET USERS
    @staticmethod
    def getUsers():
        db = cursor = None
        try:
            db = DatabaseConnection()
            if db is None:
                return False, "Database connection failed"

            cursor = db.cursor(cursor_factory=RealDictCursor)

            cursor.execute("""
                SELECT
                    userid,
                    username AS name,
                    email,
                    role,
                    phone,
                    is_active,
                    created_at
                FROM users
                ORDER BY created_at DESC
            """)

            return True, cursor.fetchall()

        except Exception as e:
            return False, f"Unable to get users: {e}"

        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    # GET USER BY ID
    @staticmethod
    def getUserById(user_id):
        db = cursor = None
        try:
            db = DatabaseConnection()
            if db is None:
                return False, "Database connection failed"

            cursor = db.cursor(cursor_factory=RealDictCursor)

            cursor.execute("""
                SELECT
                    userid AS id,
                    username,
                    email,
                    phone,
                    role,
                    is_active,
                    created_at
                FROM users
                WHERE userid=%s
            """, (user_id,))

            user = cursor.fetchone()

            return (True, user) if user else (False, "User not found")

        except Exception as e:
            return False, str(e)

        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    # GET USER DETAILS
    @staticmethod
    def getUserDetails(user_id):
        return AdminQueries.getUserById(user_id)

    # UPDATE USER
    @staticmethod
    def updateUser(user_id, data):
        if data.get('role') not in {'user', 'admin'}:
            return False, 'Invalid role'

        if not data.get('username') or not data.get('email'):
            return False, 'Name and email are required'

        db = cursor = None
        try:
            db = DatabaseConnection()
            if db is None:
                return False, "Database connection failed"

            cursor = db.cursor()

            cursor.execute("""
                UPDATE users
                SET username=%s,
                    email=%s,
                    phone=%s,
                    role=%s
                WHERE userid=%s
            """, (
                data['username'],
                data['email'],
                data.get('phone') or None,
                data['role'],
                user_id
            ))

            if cursor.rowcount != 1:
                db.rollback()
                return False, 'User not found'

            db.commit()
            return True, 'User updated successfully'

        except Exception as e:
            if db:
                db.rollback()
            return False, str(e)

        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    # ---------------------------------------------------------
    # ORDERS
    # ---------------------------------------------------------

    # GET ALL ORDERS
    @staticmethod
    def getOrders(search=None, status=None):
        db = cursor = None
        try:
            db = DatabaseConnection()
            if db is None:
                return False, "Database connection failed"

            cursor = db.cursor(cursor_factory=RealDictCursor)

            query = """
                SELECT
                    o.orderid AS id,
                    o.userid,
                    u.username AS customer_name,
                    u.email AS customer_email,
                    o.total,
                    o.status,
                    o.address,
                    o.created_at,
                    p.method AS payment_method,
                    p.status AS payment_status,
                    p.amount AS payment_amount,
                    p.razorpay_order_id,
                    p.razorpay_id AS razorpay_payment_id,
                    COALESCE(od.item_count, 0) AS item_count

                FROM orders o
                JOIN users u ON u.userid = o.userid
                LEFT JOIN payments p ON p.orderid = o.orderid
                LEFT JOIN (
                    SELECT orderid, COUNT(*) AS item_count
                    FROM order_details
                    GROUP BY orderid
                ) od ON od.orderid = o.orderid
                WHERE 1=1
            """

            values = []

            if search:
                query += """
                    AND (
                        CAST(o.orderid AS TEXT) LIKE %s
                        OR u.username LIKE %s
                        OR u.email LIKE %s
                    )
                """
                values.extend([f"%{search}%"] * 3)

            if status:
                query += " AND o.status=%s"
                values.append(status.lower())

            query += " ORDER BY o.created_at DESC"

            cursor.execute(query, tuple(values))

            return True, cursor.fetchall()

        except Exception as e:
            print("GET ORDERS ERROR:", e)
            return False, str(e)

        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    # GET ORDER BY ID
    @staticmethod
    def getOrderById(order_id):
        db = cursor = None
        try:
            db = DatabaseConnection()
            if db is None:
                return None

            cursor = db.cursor(cursor_factory=RealDictCursor)

            query = """
                SELECT
                    o.orderid,
                    o.userid,
                    o.status,
                    o.address,
                    o.total,
                    o.created_at,
                    u.username AS customer_name,
                    u.email AS customer_email,
                    u.phone,
                    u.gender,
                    u.dateofbirth,
                    p.method AS payment_method,
                    p.status AS payment_status,
                    p.amount AS payment_amount,
                    p.razorpay_order_id,
                    p.razorpay_id AS razorpay_payment_id
                FROM orders o
                LEFT JOIN users u ON u.userid = o.userid
                LEFT JOIN payments p ON p.orderid = o.orderid
                WHERE o.orderid=%s
            """

            cursor.execute(query, (order_id,))

            return cursor.fetchone()

        except Exception as e:
            print("GET ORDER ERROR:", e)
            return None

        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    # GET ORDER ITEMS
    @staticmethod
    def getOrderItems(order_id):
        db = cursor = None
        try:
            db = DatabaseConnection()
            if db is None:
                return []

            cursor = db.cursor(cursor_factory=RealDictCursor)

            query = """
                SELECT
                    od.orderid,
                    od.productid,
                    od.quantity,
                    od.price,
                    od.subtotal,
                    p.productname,
                    p.category,
                    p.imgname,
                    p.storedpath
                FROM order_details od
                LEFT JOIN products p ON p.productid = od.productid
                WHERE od.orderid=%s
            """

            cursor.execute(query, (order_id,))

            return cursor.fetchall()

        except Exception as e:
            print("GET ORDER ITEMS ERROR:", e)
            return []

        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    # GET COMPLETE ORDER DETAILS
    @staticmethod
    def getOrderDetails(order_id):
        order = AdminQueries.getOrderById(order_id)

        if not order:
            return False, 'Order not found'

        items = AdminQueries.getOrderItems(order_id)

        order['items'] = items
        order['subtotal'] = sum(float(item['subtotal']) for item in items)
        order['shipping'] = round(float(order['total']) - order['subtotal'], 2)

        return True, order

    # UPDATE ORDER STATUS
    @staticmethod
    def updateOrderStatus(order_id, status):
        status = status.lower()

        allowed_statuses = {
            'pending',
            'shipped',
            'delivered',
            'cancelled'
        }

        if status not in allowed_statuses:
            return False

        db = cursor = None
        try:
            db = DatabaseConnection()
            if db is None:
                return False

            cursor = db.cursor(cursor_factory=RealDictCursor)

            # PostgreSQL starts a transaction automatically.
            # Lock the order row before changing stock or status.
            cursor.execute(
                "SELECT status FROM orders WHERE orderid=%s FOR UPDATE",
                (order_id,)
            )

            order = cursor.fetchone()

            if not order:
                db.rollback()
                return False

            if order['status'] == 'cancelled':
                db.rollback()
                return False

            if status == 'cancelled':

                # Restore stock once while the order row is locked.
                cursor.execute("""
                    SELECT productid, quantity
                    FROM order_details
                    WHERE orderid=%s
                """, (order_id,))

                for item in cursor.fetchall():
                    cursor.execute("""
                        UPDATE products
                        SET quantity = quantity + %s
                        WHERE productid = %s
                    """, (item['quantity'], item['productid']))

                # Only pending payments are marked failed.
                cursor.execute("""
                    UPDATE payments
                    SET status='failed'
                    WHERE orderid=%s AND status='pending'
                """, (order_id,))

            cursor.execute(
                "UPDATE orders SET status=%s WHERE orderid=%s",
                (status, order_id)
            )

            db.commit()
            return True

        except Exception as e:
            if db:
                db.rollback()
            print("UPDATE ORDER STATUS ERROR:", e)
            return False

        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()
