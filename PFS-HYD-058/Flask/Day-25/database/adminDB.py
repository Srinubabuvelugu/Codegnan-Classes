
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


    @staticmethod
    def updateProductRecord(product_data:tuple[str|int]):
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor()

            query = """update products set productname =%s, description=%s,
                         category = %s, quantity=%s, 
                        saleprice=%s, imgname=%s, storedpath=%s
                        where productid = %s"""
            cursor.execute(query,product_data)
            db_config.commit()
            cursor.close()
            db_config.close()
            return True, "Product Updated"
        except Exception as e:
            return False, f"Something wrong in database/adminDB.AdminQueries.updateProductRecord:{e}"


    # get all categories 
    @staticmethod
    def getAllCategories():
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor()

            query = """select distinct category from products"""
            cursor.execute(query)
            categories = cursor.fetchall()
            cursor.close()
            db_config.close()
            return True, categories
        except Exception as e:
            return False, f"Something wrong in database/adminDB.AdminQueries.getAllCategories:{e}"
    # get users data
    @staticmethod
    def getAllUsers():
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)

            query = """select * from users"""
            cursor.execute(query)
            users = cursor.fetchall()
            cursor.close()
            db_config.close()
            return True, users
        except Exception as e:
            return False, f"Something wrong in database/adminDB.AdminQueries.getAllUsers:{e}"

