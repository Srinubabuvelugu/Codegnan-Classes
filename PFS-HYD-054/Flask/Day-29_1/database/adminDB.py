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
