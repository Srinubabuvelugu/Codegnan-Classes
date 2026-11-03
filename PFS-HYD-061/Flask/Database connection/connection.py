import mysql.connector as SQLC


# step 1: Database configuration
db_config = SQLC.connect(host="localhost",
                         user="root",
                         password = "root", # yur mysql password
                         database = "codegnan"
                         )
# step 2: create cursor object
cursor = db_config.cursor(dictionary=True)

# print(db_config)
# print(cursor)
# # Step 3: execute a query 
# query = "create database if not exists Codegnan;"
# cursor.execute(query)
# print("dactabase created")
# print(cursor)

# query = """create table if not exists students(
#             id int,
#             name varchar(30),
#             batch varchar(30)
#         );"""
# cursor.execute(query)

# query = "insert into students(id, name, batch) values(%s, %s,%s)"
# cursor.execute(query, (101, 'srinu', 'PFS-61'))
# db_config.commit()

# step 4: select data from tables
# query = "select * from students"
# cursor.execute(query)
# data = cursor.fetchall()
# print(data)
query = "select * from students where id = %s"
cursor.execute(query, (101, ))
data = cursor.fetchone()
print(data)