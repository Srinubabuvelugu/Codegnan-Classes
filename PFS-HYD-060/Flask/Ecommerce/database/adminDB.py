
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
