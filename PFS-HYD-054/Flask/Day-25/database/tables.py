from database.connection import DatabaseConnction


<<<<<<< HEAD
=======

>>>>>>> b8ff824 (Register Completed)
def createTables():
    try:
        db_config = DatabaseConnction()
        cursor = db_config.cursor()

<<<<<<< HEAD
        users_table_query = """create table if not exists users(
            userid bigint auto_increment primary key,
            username varchar(50) not null,
            email varchar(50) not null unique,
            hashpassword varchar(255) not null,
            role enum('admin','user') default 'admin',
            gender enum('male', 'female'),
            phone varchar(15),
            dateofbirth date,
            profilename varchar(255), 
            profilepath varchar(255), 
            is_active boolean default true,
            created_at timestamp default current_timestamp,
            updated_at timestamp default current_timestamp on update current_timestamp
        );"""

        products_table_query = """create table if not exists products(
            productid bigint auto_increment primary key,
            productname varchar(100) not null,
            description text,
            category varchar(50),
            quantity int unsigned default 0,
            buyprice float(15,2) default 0.0,
            saleprice float(15,2) default 0.0,
            imgname varchar(100),
            storedpath varchar(255),
            is_active boolean default true,
            created_at timestamp default current_timestamp,
            updated_at timestamp default current_timestamp on update current_timestamp
        );"""

        orders_table_query = """create table if not exists orders(
            orderid bigint auto_increment primary key,
            userid bigint,
            status enum('shipped', 'delivered', 'cancelled', 'pending') default 'pending',
            address varchar(255),
            created_at timestamp default current_timestamp,
            foreign key (userid) references users(userid)
        );"""

        orderdetails_table_query = """create table if not exists order_details(
            orderid bigint, 
            productid bigint,
            quantity int unsigned default 1,
            price float(15,2) default 0.0,
            subtotal float(20,2) generated always as (quantity * price),
            foreign key(orderid) references orders(orderid),
            foreign key(productid) references products(productid)
        );"""

        payments_table_query = """create table if not exists payments(
            paymentid bigint auto_increment primary key,
            userid bigint,
            orderid bigint,
            method enum('cash', 'upi', 'netbanking'),
            amount float(20,2) default 0.0,
            created_at timestamp default current_timestamp,
            foreign key(userid) references users(userid),
            foreign key(orderid) references orders(orderid)
        );"""

        cart_table_query = """create table if not exists cart(
            cartid bigint auto_increment primary key,
            userid bigint,
            productid bigint,
            quantity int default 1,
            foreign key(userid) references users(userid),
            foreign key(productid) references products(productid)
        );"""

        tables = [
            users_table_query,
            products_table_query,
            orders_table_query,
            orderdetails_table_query,
            payments_table_query,
            cart_table_query
        ]

=======
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
>>>>>>> b8ff824 (Register Completed)
        for table_query in tables:
            cursor.execute(table_query)

        return "Tables Created"

<<<<<<< HEAD
=======

>>>>>>> b8ff824 (Register Completed)
    except Exception as e:
        return f"Somthing wrong in database/tables.py:{e}"