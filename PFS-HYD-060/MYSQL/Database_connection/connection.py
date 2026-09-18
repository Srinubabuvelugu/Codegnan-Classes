import mysql.connector as SQLC

#step 1: Database connection
db_config = SQLC.connect(
    host = "localhost",
    user = "root",
    password = "root", # Your mysql workbench password
    database = 'cricket'
)
# Step2: creating cursor object
cursor = db_config.cursor(dictionary=True)
# print(db_config)
# print(cursor)
# # create  cricket database
# create_database_query ="""create database if not exists cricket;"""
# # execute the query
# cursor.execute(create_database_query)
# print(cursor)
# print("Database created")

# # table creation query
# table_creation_query = """create table if not exists players(
#     id int auto_increment primary key,
#     name varchar(30),
#     age tinyint unsigned,
#     gender enum('male', 'female'),
#     role varchar(40),
#     created_at timestamp default current_timestamp
# );"""
# cursor.execute(table_creation_query)
# print("Table created")

# Step3 : inserting data
# # inserting data into table
# record_insert_query = """insert into players(name, age, gender, role)
#                         values(%s, %s, %s, %s);"""
# cursor.execute(record_insert_query, ("Rohit", 38,'male','Batting'))
# cursor.execute(record_insert_query, ("Virat", 35,'male','Batting'))
# db_config.commit()
# print("records inserted")

# Step4: get data
## get the table data
cursor.execute("update players set age = %s where id = %s", (39, 3))
db_config.commit()

cursor.execute("select * from players where id = %s;", (3,))
data = cursor.fetchone()
print(data)