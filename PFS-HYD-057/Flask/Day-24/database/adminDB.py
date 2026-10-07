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