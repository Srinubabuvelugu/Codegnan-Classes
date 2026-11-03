from database.connection import DatabaseConnction


class AdminQueries:

    # ---------------------------------------------------------
    # PRODUCTS
    # ---------------------------------------------------------

    @staticmethod
    def insertProductRecord(product_data):
        db = DatabaseConnction()
        cur = db.cursor()

        try:
            query = """
                INSERT INTO products(
                    productname,
                    description,
                    category,
                    quantity,
                    buyprice,
                    saleprice,
                    imgname,
                    storedpath
                )
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(query, product_data)
            db.commit()
            return True, "Product Added"

        except Exception as e:
            db.rollback()
            return False, f"Unable to add product: {e}"

        finally:
            cur.close()
            db.close()

    @staticmethod
    def getAllProducts(product_id=None):
        db = DatabaseConnction()
        cur = db.cursor(dictionary=True)

        try:
            if product_id:
                cur.execute(
                    "SELECT * FROM products WHERE productid=%s",
                    (product_id,)
                )
                product = cur.fetchone()
                return (True, product) if product else (False, "Product not found")

            cur.execute("SELECT * FROM products ORDER BY productid DESC")
            return True, cur.fetchall()

        except Exception as e:
            return False, f"Unable to get products: {e}"

        finally:
            cur.close()
            db.close()

    @staticmethod
    def getCategories():
        db = DatabaseConnction()
        cur = db.cursor()

        try:
            cur.execute("""
                SELECT DISTINCT category
                FROM products
                WHERE category IS NOT NULL AND category != ''
                ORDER BY category
            """)
            return True, cur.fetchall()

        except Exception as e:
            return False, f"Unable to get categories: {e}"

        finally:
            cur.close()
            db.close()

    @staticmethod
    def updateProduct(product_id, product_data):
        db = DatabaseConnction()
        cur = db.cursor()

        try:
            query = """
                UPDATE products
                SET productname=%s,
                    description=%s,
                    category=%s,
                    quantity=%s,
                    buyprice=%s,
                    saleprice=%s
                WHERE productid=%s
            """
            cur.execute(query, (*product_data, product_id))
            db.commit()

            if cur.rowcount == 0:
                return False, "Product not found or no changes made"

            return True, "Product Updated"

        except Exception as e:
            db.rollback()
            return False, f"Unable to update product: {e}"

        finally:
            cur.close()
            db.close()

    @staticmethod
    def updateProductData(product_data, img=False):
        """Compatibility method for code that uses the older tuple format."""
        db = DatabaseConnction()
        cur = db.cursor()

        try:
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

            cur.execute(query, product_data)
            db.commit()
            return True, "Product Updated"

        except Exception as e:
            db.rollback()
            return False, f"Unable to update product: {e}"

        finally:
            cur.close()
            db.close()

    @staticmethod
    def deleteProduct(productid):
        # Soft delete: order_details may still refer to this product.
        db = DatabaseConnction()
        cur = db.cursor()

        try:
            cur.execute(
                "UPDATE products SET is_active=FALSE WHERE productid=%s",
                (productid,)
            )
            db.commit()

            if cur.rowcount == 0:
                return False, "Product not found"

            return True, "Product deactivated"

        except Exception as e:
            db.rollback()
            return False, f"Unable to deactivate product: {e}"

        finally:
            cur.close()
            db.close()

    @staticmethod
    def deactivateProduct(product_id):
        db = DatabaseConnction()
        cur = db.cursor()

        try:
            cur.execute(
                "UPDATE products SET is_active=FALSE WHERE productid=%s",
                (product_id,)
            )
            db.commit()
            return cur.rowcount > 0

        except Exception as e:
            db.rollback()
            print("DEACTIVATE PRODUCT ERROR:", e)
            return False

        finally:
            cur.close()
            db.close()

    @staticmethod
    def activateProduct(product_id):
        db = DatabaseConnction()
        cur = db.cursor()

        try:
            cur.execute(
                "UPDATE products SET is_active=TRUE WHERE productid=%s",
                (product_id,)
            )
            db.commit()
            return cur.rowcount > 0

        except Exception as e:
            db.rollback()
            print("ACTIVATE PRODUCT ERROR:", e)
            return False

        finally:
            cur.close()
            db.close()

    @staticmethod
    def chengeProductActivateStatus(product_id, active=False):
        if active:
            success = AdminQueries.activateProduct(product_id)
            return success, "Product activated" if success else "Unable to activate product"

        success = AdminQueries.deactivateProduct(product_id)
        return success, "Product deactivated" if success else "Unable to deactivate product"

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

            count_query = f"SELECT COUNT(*) AS total FROM ({query}) AS filtered_products"
            cur.execute(count_query, tuple(params))
            total = cur.fetchone()['total']

            if page < 1:
                page = 1

            offset = (page - 1) * per_page
            query += " ORDER BY productid DESC LIMIT %s OFFSET %s"
            params.extend([per_page, offset])

            cur.execute(query, tuple(params))
            products = cur.fetchall()

            cur.execute("""
                SELECT DISTINCT category
                FROM products
                WHERE category IS NOT NULL AND category != ''
                ORDER BY category
            """)
            categories = [row['category'] for row in cur.fetchall()]

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
            cur.close()
            db.close()

    # ---------------------------------------------------------
    # USERS
    # ---------------------------------------------------------

    @staticmethod
    def getUsers():
        db = DatabaseConnction()
        cur = db.cursor(dictionary=True)

        try:
            cur.execute("""
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
            return True, cur.fetchall()

        except Exception as e:
            return False, f"Unable to get users: {e}"

        finally:
            cur.close()
            db.close()

    @staticmethod
    def getUserById(user_id):
        db = DatabaseConnction()
        cur = db.cursor(dictionary=True)

        try:
            cur.execute("""
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
            user = cur.fetchone()
            return (True, user) if user else (False, "User not found")

        except Exception as e:
            return False, str(e)

        finally:
            cur.close()
            db.close()

    @staticmethod
    def getUserDetails(user_id):
        return AdminQueries.getUserById(user_id)

    @staticmethod
    def updateUser(user_id, data):
        if data.get('role') not in {'user', 'admin'}:
            return False, 'Invalid role'

        if not data.get('username') or not data.get('email'):
            return False, 'Name and email are required'

        db = DatabaseConnction()
        cur = db.cursor()

        try:
            cur.execute("""
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

            if cur.rowcount != 1:
                db.rollback()
                return False, 'User not found'

            db.commit()
            return True, 'User updated successfully'

        except Exception as e:
            db.rollback()
            return False, str(e)

        finally:
            cur.close()
            db.close()

    # ---------------------------------------------------------
    # ORDERS
    # ---------------------------------------------------------

    @staticmethod
    def getOrders(search=None, status=None):
        """Returns (success, list_of_orders), matching the existing routes."""
        db = DatabaseConnction()
        cur = db.cursor(dictionary=True)

        try:
            query = """
                SELECT
                    o.orderid ,
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
                    p.razorpay_payment_id,
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
                        CAST(o.orderid AS CHAR) LIKE %s
                        OR u.username LIKE %s
                        OR u.email LIKE %s
                    )
                """
                values.extend([f"%{search}%"] * 3)

            if status:
                query += " AND o.status=%s"
                values.append(status.lower())

            query += " ORDER BY o.created_at DESC"

            cur.execute(query, tuple(values))
            return True, cur.fetchall()

        except Exception as e:
            print("GET ORDERS ERROR:", e)
            return False, str(e)

        finally:
            cur.close()
            db.close()

    @staticmethod
    def getOrderById(order_id):
        db = DatabaseConnction()
        cur = db.cursor(dictionary=True)

        try:
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
                    p.razorpay_payment_id
                FROM orders o
                LEFT JOIN users u ON u.userid = o.userid
                LEFT JOIN payments p ON p.orderid = o.orderid
                WHERE o.orderid=%s
            """
            cur.execute(query, (order_id,))
            return cur.fetchone()

        except Exception as e:
            print("GET ORDER ERROR:", e)
            return None

        finally:
            cur.close()
            db.close()

    @staticmethod
    def getOrderItems(order_id):
        db = DatabaseConnction()
        cur = db.cursor(dictionary=True)

        try:
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
            cur.execute(query, (order_id,))
            return cur.fetchall()

        except Exception as e:
            print("GET ORDER ITEMS ERROR:", e)
            return []

        finally:
            cur.close()
            db.close()

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

        db = DatabaseConnction()
        cur = db.cursor(dictionary=True)

        try:
            db.start_transaction()

            cur.execute(
                "SELECT status FROM orders WHERE orderid=%s FOR UPDATE",
                (order_id,)
            )
            order = cur.fetchone()

            if not order:
                db.rollback()
                return False

            if order['status'] == 'cancelled':
                db.rollback()
                return False

            if status == 'cancelled':
                # Restore stock once, while the order row is locked.
                cur.execute("""
                    SELECT productid, quantity
                    FROM order_details
                    WHERE orderid=%s
                """, (order_id,))

                for item in cur.fetchall():
                    cur.execute("""
                        UPDATE products
                        SET quantity = quantity + %s
                        WHERE productid = %s
                    """, (item['quantity'], item['productid']))

                # Only pending payments are marked failed.
                # Paid Razorpay payments require a separate refund process.
                cur.execute("""
                    UPDATE payments
                    SET status='failed'
                    WHERE orderid=%s AND status='pending'
                """, (order_id,))

            cur.execute(
                "UPDATE orders SET status=%s WHERE orderid=%s",
                (status, order_id)
            )

            db.commit()
            return True

        except Exception as e:
            db.rollback()
            print("UPDATE ORDER STATUS ERROR:", e)
            return False

        finally:
            cur.close()
            db.close()
