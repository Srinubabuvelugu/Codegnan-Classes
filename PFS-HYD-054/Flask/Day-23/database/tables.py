from database.connection import DatabaseConnction



def createTables():
    try:
        db_config = DatabaseConnction()
        cursor = db_config.cursor()

        users_table_query = """CREATE TABLE IF NOT EXISTS USERS(
            USERID BIGINT AUTO_INCREMENT PRIMARY KEY,
            USERNAME VARCHAR(50) NOT NULL,
            EMAIL VARCHAR(50) NOT NULL UNIQUE,
            HASHPASSWORD VARCHAR(255) NOT NULL,
            ROLE ENUM('ADMIN','USER') DEFAULT 'ADMIN',
            GENDER ENUM('MALE', 'FEMALE'),
            PHONE VARCHAR(15),
            DATEOFBIRTH DATE,
            PROFILENAME VARCHAR(255), 
            PROFILEPATH VARCHAR(255), 
            IS_ACTIVE BOOLEAN DEFAULT TRUE,
            CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );"""

        products_table_query = """CREATE TABLE IF NOT EXISTS PRODUCTS(
            PRODUCTID BIGINT AUTO_INCREMENT PRIMARY KEY,
            PRODUCTNAME VARCHAR(100) NOT NULL,
            DESCRIPTION TEXT,
            CATEGORY VARCHAR(50),
            QUANTITY INT UNSIGNED DEFAULT 0,
            BUYPRICE FLOAT(15,2) DEFAULT 0.0,
            SALEPRICE FLOAT(15,2) DEFAULT 0.0,
            IMGNAME VARCHAR(100),
            STOREDPATH VARCHAR(255),
            IS_ACTIVE BOOLEAN DEFAULT TRUE,
            CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );"""

        orders_table_query = """CREATE TABLE IF NOT EXISTS ORDERS(
            ORDERID BIGINT AUTO_INCREMENT PRIMARY KEY,
            USERID BIGINT,
            STATUS ENUM('SHIPPED', 'DELIVERED', 'CANCELLED', 'PENDING') DEFAULT 'PENDING',
            ADDRESS VARCHAR(255),
            CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (USERID) REFERENCES USERS(USERID)
        );"""

        orderdetails_table_query = """CREATE TABLE IF NOT EXISTS ORDER_DETAILS(
            ORDERID BIGINT, 
            PRODUCTID BIGINT,
            QUANTITY INT UNSIGNED DEFAULT 1,
            PRICE FLOAT(15,2) DEFAULT 0.0,
            SUBTOTAL FLOAT(20,2) GENERATED ALWAYS AS (QUANTITY * PRICE),
            FOREIGN KEY(ORDERID) REFERENCES ORDERS(ORDERID),
            FOREIGN KEY(PRODUCTID) REFERENCES PRODUCTS(PRODUCTID)
        );"""

        payments_table_query = """CREATE TABLE IF NOT EXISTS PAYMENTS(
            PAYMENTID BIGINT AUTO_INCREMENT PRIMARY KEY,
            USERID BIGINT,
            ORDERID BIGINT,
            METHOD ENUM('CASH', 'UPI', 'NETBANKING'),
            AMOUNT FLOAT(20,2) DEFAULT 0.0,
            CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(USERID) REFERENCES USERS(USERID),
            FOREIGN KEY(ORDERID) REFERENCES ORDERS(ORDERID)
        );"""

        cart_table_query = """CREATE TABLE IF NOT EXISTS CART(
            CARTID BIGINT AUTO_INCREMENT PRIMARY KEY,
            USERID BIGINT,
            PRODUCTID BIGINT,
            QUANTITY INT DEFAULT 1,
            FOREIGN KEY(USERID) REFERENCES USERS(USERID),
            FOREIGN KEY(PRODUCTID) REFERENCES PRODUCTS(PRODUCTID)
        );"""

        tables = [users_table_query,
                  products_table_query,
                  orders_table_query,
                  orderdetails_table_query,
                  payments_table_query,
                  cart_table_query
                  ]
        for table_query in tables:
            cursor.execute(table_query)

        return "Tables Created"


    except Exception as e:
        return f"Somthing wrong in database/tables.py:{e}"