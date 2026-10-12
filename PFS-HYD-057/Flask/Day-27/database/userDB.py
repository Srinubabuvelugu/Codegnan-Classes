from database.connection import DatabaseConnction



class UserQueries:
    # get products
    @staticmethod
    def getAllProducts(category:str=None, product_id:int=None):
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)
            query = """ select * from products where is_active = %s"""
            values= [1]
            if category:
                query += " and category = %s"
                values.append(category)
            if product_id:
                query += " and productid = %s"
                values.append(product_id)
                cursor.execute(query, tuple(values))
                products = cursor.fetchone()
            else:
                cursor.execute(query, tuple(values))
                products = cursor.fetchall()
            cursor.close()
            db_config.close()
            return True, products
        except Exception as e:
            return False, f"Something wrong in database/adminDB.UserQueries-getAllProducts():{e}"
    