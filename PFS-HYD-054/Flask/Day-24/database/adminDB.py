from database.connection import DatabaseConnction
from functools import wraps


# class AdminDB:
#     def __init__(self, userid, name):
#         self.userid = userid
#         self.name = name




# def getDBconnection(fun):
#     @wraps
#     def wrapper(*args, **kwargs):
#         try:
#             db_config = DatabaseConnction()
#             cursor = db_config.cursor()
#             return fun(cursor,db_config, *args, **kwargs)
#         except Exception as e:
#             return False, f"Something wrong in {fun}:{e}"



# insert product record  

class AdminDBQueries:
    def insertProductRecord(product_data:tuple[str|int]):
        try: 
            db_config = DatabaseConnction()
            cursor = db_config.cursor()

            query = """insert into products(productname, description, category, quantity, buyprice, saleprice,imgname,storedpath)
                        values(%s, %s, %s, %s, %s, %s,%s, %s);
            """
            cursor.execute(query, product_data)
            db_config.commit()
            return True, "Product Added"
        except Exception as e:
            return False, f"Something wrong in database/adminDB.py-iinsertProductRecord:{e}"
    # get products
    def getAllProducts():
        try: 
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)

            query = """select * from products order by updated_at desc;
            """
            cursor.execute(query)
            products = cursor.fetchall()

            db_config.commit()
            return True, products
        except Exception as e:
            return False, f"Something wrong in database/adminDB.py-iinsertProductRecord:{e}"


    
