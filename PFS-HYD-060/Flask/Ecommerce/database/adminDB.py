
from database.connection import DatabaseConnection

class AdminQueries:
    @staticmethod
    def insertProductRecord(product_data:tuple[str|int]):
        cursor = db_config = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()

            query = """insert into products(productname, description, category,
                             saleprice, quantity,imgname, storedpath)
                             values(%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, product_data)
            db_config.commit()
            return True, "Product Added"
        except Exception as e:
            return False, f"Something wrong in \
                        database/adminDB.AdminQueries.insertProductRecord():{e}"
        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()



# get all products baseed on category, productname, is_active,
    @staticmethod
    def getAllProducts(product_name:str=None, product_id:int = None,
                        category:str=None,page_no:int=1, per_page:int=7):
        cursor = db_config = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)

            query = """select * from products where 1=1"""
            values = []
            if product_name:
                query += " and productname like %s"
                values.append(f"%{product_name}%")
            if category:
                query += " and category = %s"
                values.append(category)
            if product_id:
                query += " and productid = %s"
                values.append(product_id)

            query += f" order by updated_at desc limit {per_page} offset {(page_no-1) * 7}"

        
            cursor.execute(query, values)
            data = cursor.fetchone() if product_id else cursor.fetchall()
            return True, data
        except Exception as e:
            return False, f"Something wrong in \
                        database/adminDB.AdminQueries.getAllProducts():{e}"
        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    # get all categoriges
    @staticmethod
    def getAllCategories():
        cursor = db_config = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()

            query = """select distinct category from products;"""
            cursor.execute(query)
            data = cursor.fetchall()
            
            return True, data
        except Exception as e:
            return False, f"Something wrong in \
                        database/adminDB.AdminQueries.getAllCategories():{e}"
        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    # update product record
    @staticmethod
    def updateProductRecord(product_data:tuple[str|int]):
        cursor = db_config = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()

            query = """update products set productname = %s , description = %s, category = %s,
                             saleprice=%s, quantity=%s, imgname = %s , storedpath = %s
                             where productid = %s"""
            cursor.execute(query, product_data)
            db_config.commit()
            return True, "Product Updated"
        except Exception as e:
            return False, f"Something wrong in \
                        database/adminDB.AdminQueries.updateProductRecord():{e}"
        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()


    # get all users
    @staticmethod
    def getAllUsers():
        cursor = db_config = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)

            query = """select * from users;"""
            cursor.execute(query)
            data = cursor.fetchall()
            
            return True, data
        except Exception as e:
            return False, f"Something wrong in \
                        database/adminDB.AdminQueries.getAllUsers():{e}"
        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

