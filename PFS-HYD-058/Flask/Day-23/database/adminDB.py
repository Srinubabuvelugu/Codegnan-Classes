
from database.connection import DatabaseConnction


class AdminQueries:
    @staticmethod
    def insertProductRecord(product_data:tuple[str|int]):
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor()

            query = """insert into products(productname, description, category, quantity, 
                        saleprice, imgname, storedpath)
                        values(%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query,product_data)
            db_config.commit()
            cursor.close()
            db_config.close()
            return True, "Product Added"
        except Exception as e:
            return False, f"Something wrong in database/adminDB.AdminQueries.insertProductRecord:{e}"


    # get all products
    @staticmethod
    def getAllProducts(productname:str=None, category:str=None, product_id:int=None):
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)

            query = """select * from products where 1=1"""
            values = []
            if productname:
                query += " and productname like %s"
                values.append(f"%{productname}%")
            if category:
                query += " and category = %s"
                values.append(category)
            if product_id:
                query += " and productid = %s"
                cursor.execute(query, (product_id, ))
                product = cursor.fetchone()
                return True, product

            cursor.execute(query,values)
            products = cursor.fetchall()
            cursor.close()
            db_config.close()
            return True, products
        except Exception as e:
            return False, f"Something wrong in database/adminDB.AdminQueries.getAllProducts:{e}"


