import mysql.connector as SQLC

# database connection
db_config = SQLC.connect(host='localhost',
                         user = 'root',
                         password = 'root',
                         database = 'fruit_market_db')

# cursor object creation
cursor = db_config.cursor()

fruits_table_query = """create table if not exists fruits(
                        id int auto_increment primary key,
                        name varchar(50) not null,
                        price float default 0.0,
                        stock float default 0.0
                        )"""

cursor.execute(fruits_table_query)

# data insertion

insertion_query = """insert into fruits(name, price, stock) values(%s, %s, %s)"""


cursor.execute(insertion_query, ('apple', 100, 25))

data = [('banan', 50, 20), ('orange', 70, 15), ('water melon', 30, 30)]
cursor.executemany(insertion_query, data)

db_config.commit()


