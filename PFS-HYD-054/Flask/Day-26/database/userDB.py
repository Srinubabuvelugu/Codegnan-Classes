from database.connection import DatabaseConnction
from functools import wraps




# insert product record  

class UserDBQueries:
    
    def getAllProducts(id:int=None):
        try: 
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)

            query = "select * from products where is_active = %s"
            values = [True]
            if id:
                query += " and productid = %s"
                values.append(id)
            # query += " order by updated_At desc"
            if id:
                cursor.execute(query, tuple(values))
                products = cursor.fetchone()
            else:
                cursor.execute(query, tuple(values))
                products = cursor.fetchall()

            db_config.commit()
            if products:
                return True, products
            else:
                return False, "Product Not exists"
        except Exception as e:
            return False, f"Something wrong in database/userDB.py-getAllProducts:{e}"


    
