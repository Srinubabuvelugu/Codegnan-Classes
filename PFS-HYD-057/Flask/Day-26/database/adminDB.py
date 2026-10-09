from database.connection import DatabaseConnction

class AdminQueries:
    @staticmethod
    def insertProductRecord(product_data:tuple[str|int]):
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor()

            query = """insert into products(productname, 
                                            description,
                                            category, 
                                            quantity, 
                                            saleprice,
                                            imgname,
                                            storedpath) values(%s,%s,%s,%s,%s,%s,%s)"""
            cursor.execute(query, product_data)
            db_config.commit()
            cursor.close()
            db_config.close()
            return True, "Product Added"
        except Exception as e:
            return False, f"Something wrong in database/adminDB.AdminQueries-insertProductRecord():{e}"


    @staticmethod
    def getAllProducts(productid:int=None):
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)
            query = """ select * from products where 1=1"""
            values= []
            if productid:
                query += " and productid = %s"
                values.append(productid)
                cursor.execute(query, tuple(values))
                products = cursor.fetchone()
            else:
                cursor.execute(query)
                products = cursor.fetchall()
            cursor.close()
            db_config.close()
            return True, products
        except Exception as e:
            return False, f"Something wrong in database/adminDB.AdminQueries-getAllProducts():{e}"
    
    @staticmethod
    def getCategories():
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor()
            query = "select distinct category from products"
            cursor.execute(query)
            categories = cursor.fetchall()
            cursor.close()
            db_config.close()
            return True, categories
        except Exception as e:
            return False, f"Something wrong in database/adminDB.AdminQueries-getCategories():{e}"


    @staticmethod
    def updateProductData(product_data:tuple[str|int], img:bool=False):
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor()

            query = """update products set productname = %s, 
                                            description = %s,
                                            category = %s, 
                                            quantity = %s, 
                                            saleprice = %s
                                            """
            if img:
                query += """,imgname = %s,
                            storedpath = %s
                            where productid = %s
                            """
                cursor.execute(query, product_data)
            else:
                query +=" where productid = %s"
                cursor.execute(query, product_data)
            db_config.commit()
            cursor.close()
            db_config.close()
            return True, "Product Updated"
        except Exception as e:
            return False, f"Something wrong in database/adminDB.AdminQueries-updateProductData():{e}"
