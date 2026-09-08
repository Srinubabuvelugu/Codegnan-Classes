import mysql.connector as SQLC
# step1: Database conncection
db_config = SQLC.connect(
    host="localhost",
    user="root",
    password="root",
    database="bank1" # your mysql workbench password
)

# step2: create cursor object 
cursor = db_config.cursor()

# print(db_config)
# print(cursor)
# step3: execute the query
# creating one database
# create bank database
# query = """CREATE DATABASE if not exists BANK1;"""
# cursor.execute(query)
# print("Database created")
# print(cursor)

# accounts_table_query = """CREATE TABLE IF NOT EXISTS ACCOUNTS(
#         ACCOUNT_NO INT, 
#         USERNAME VARCHAR(40),
#         AMOUNT INT UNSIGNED,
#         gender enum('f', 'm')
#     );"""
# cursor.execute(accounts_table_query)
# print("Table created")

## insert record into table
# insert_record_query = """INSERT INTO ACCOUNTS(ACCOUNT_NO, USERNAME, AMOUNT)
#                     VALUES(%s, %s,%s);"""
# # cursor.execute(insert_record_query, (1001, "SRINU", 10000))
# cursor.execute(insert_record_query, (1002, "Babu", 10000))
# cursor.execute(insert_record_query, (1003, "Mahi", 7000))
# cursor.execute(insert_record_query, (1004, "Siri", 5000))
# db_config.commit()

# print("record inserted")

# get data from table
get_accounts_query = "SELECT * FROM ACCOUNTS;"
cursor.execute(get_accounts_query)
# setp4 : fetch
data = cursor.fetchall()
print(data)

cursor.execute("select * from accounts where account_no = %s", (1002,))
print(cursor.fetchall())