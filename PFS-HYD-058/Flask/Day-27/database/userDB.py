
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
    def createOrder(userid:int, address:str, razorpay_order_id:str=None, razorpay_payment_id:str=None):
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)

            query = """select c.cartid, c.userid, c.quantity, p.productname, 
                        p.productid, p.quantity as stock p.saleprice from cart c
                        join products p on c.productid = p.productid
                        where c.userid = %s FOR UPDATE"""
            items = cursor.execute(query, (userid, ))
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
            query = """insert into orders(userid, status, address, total)
                        values(%s, %s, %s, %s)"""
            cursor.execute(query, (userid,"pending", address, sub_total))
            cursor.execute("select orderid from orders where userid = %s order by orderid desc", (userid,))
            # add payment record
            orderid = cursor.fetchone()[0]

            #add items to order details
            for item in items:
                query = """insert into order_details(orderid,productid, quantity, price, subtotal)
                values(%s, %s, %s, %s)"""
                item_sub_total = item['quantity'] * item['saleprice']
                cursor.execute(query, (orderid,item['productid'], item['quantity'], item['saleprice'], item_sub_total))

            # insert payment in payments table
            status = "pending"
            method = "COD"
            shipping = sub_total * 0.01
            query = """insert into payments(userid, orderid, status, method, amount, razorpay_order_id, razorpay_payment_id)
                    values(%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (userid, orderid,status, method, sub_total +shipping,razorpay_order_id, razorpay_payment_id ))

            db_config.commit()
            cursor.close()
            db_config.close()
            return True, {"Orderid":orderid, "amount":sub_total+ shipping}
        except Exception as e:
            db_config.rollback()
            return False, f"Something wrong in database/userDB.py/UserQueries.createOrder():{e}"
            



