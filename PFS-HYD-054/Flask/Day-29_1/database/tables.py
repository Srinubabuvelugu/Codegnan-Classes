from database.connection import DatabaseConnction


def createTables():
    db = DatabaseConnction()
    cur = db.cursor()
    statements = [
        """CREATE TABLE IF NOT EXISTS users(
            userid BIGINT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            hashpassword VARCHAR(255) NOT NULL,
            role ENUM('admin','user') NOT NULL DEFAULT 'user',
            gender ENUM('male','female'),
            phone VARCHAR(20),
            dateofbirth DATE,
            profilename VARCHAR(255),
            profilepath VARCHAR(255),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS products(
            productid BIGINT AUTO_INCREMENT PRIMARY KEY,
            productname VARCHAR(100) NOT NULL,
            description TEXT,
            category VARCHAR(50),
            quantity INT UNSIGNED DEFAULT 0,
            buyprice DECIMAL(12,2) DEFAULT 0,
            saleprice DECIMAL(12,2) DEFAULT 0,
            imgname VARCHAR(100),
            storedpath VARCHAR(255),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS orders(
            orderid BIGINT AUTO_INCREMENT PRIMARY KEY,
            userid BIGINT NOT NULL,
            status VARCHAR(30) NOT NULL DEFAULT 'pending',
            address VARCHAR(1000),
            total_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
            payment_method VARCHAR(30),
            payment_status VARCHAR(30) NOT NULL DEFAULT 'pending',
            razorpay_order_id VARCHAR(100),
            razorpay_payment_id VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY(userid) REFERENCES users(userid)
        )""",
        """CREATE TABLE IF NOT EXISTS order_details(
            orderdetailid BIGINT AUTO_INCREMENT PRIMARY KEY,
            orderid BIGINT NOT NULL,
            productid BIGINT NOT NULL,
            quantity INT UNSIGNED NOT NULL,
            price DECIMAL(12,2) NOT NULL,
            subtotal DECIMAL(12,2) GENERATED ALWAYS AS (quantity * price) STORED,
            FOREIGN KEY(orderid) REFERENCES orders(orderid),
            FOREIGN KEY(productid) REFERENCES products(productid)
        )""",
        # Dedicated transaction ledger requested for checkout/payment tracking.
        """CREATE TABLE IF NOT EXISTS transactions(
            transactionid BIGINT AUTO_INCREMENT PRIMARY KEY,
            userid BIGINT NOT NULL,
            orderid BIGINT NOT NULL,
            transaction_type VARCHAR(30) NOT NULL DEFAULT 'payment',
            method VARCHAR(30),
            amount DECIMAL(12,2) NOT NULL DEFAULT 0,
            status VARCHAR(30) NOT NULL DEFAULT 'pending',
            gateway_order_id VARCHAR(100),
            gateway_payment_id VARCHAR(100),
            failure_reason VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY(userid) REFERENCES users(userid),
            FOREIGN KEY(orderid) REFERENCES orders(orderid)
        )""",
        # Keep the original payments table for compatibility with the existing project.
        """CREATE TABLE IF NOT EXISTS payments(
            paymentid BIGINT AUTO_INCREMENT PRIMARY KEY,
            userid BIGINT NOT NULL,
            orderid BIGINT NOT NULL,
            method VARCHAR(30),
            amount DECIMAL(12,2) DEFAULT 0,
            status VARCHAR(30) DEFAULT 'pending',
            razorpay_order_id VARCHAR(100),
            razorpay_payment_id VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(userid) REFERENCES users(userid),
            FOREIGN KEY(orderid) REFERENCES orders(orderid)
        )""",
        """CREATE TABLE IF NOT EXISTS cart(
            cartid BIGINT AUTO_INCREMENT PRIMARY KEY,
            userid BIGINT NOT NULL,
            productid BIGINT NOT NULL,
            quantity INT NOT NULL DEFAULT 1,
            UNIQUE KEY uq_cart_user_product(userid,productid),
            FOREIGN KEY(userid) REFERENCES users(userid),
            FOREIGN KEY(productid) REFERENCES products(productid)
        )"""
    ]
    try:
        for sql in statements:
            cur.execute(sql)

        # Migrations for databases created by the earlier project version.
        migrations = {
            'order_details': [('orderdetailid', 'BIGINT AUTO_INCREMENT PRIMARY KEY')],
            'orders': [
                ('total_amount', 'DECIMAL(12,2) NOT NULL DEFAULT 0'),
                ('payment_method', 'VARCHAR(30)'),
                ('payment_status', "VARCHAR(30) NOT NULL DEFAULT 'pending'"),
                ('razorpay_order_id', 'VARCHAR(100)'),
                ('razorpay_payment_id', 'VARCHAR(100)'),
                ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
            ],
            'payments': [
                ('status', "VARCHAR(30) DEFAULT 'pending'"),
                ('razorpay_order_id', 'VARCHAR(100)'),
                ('razorpay_payment_id', 'VARCHAR(100)')
            ],
            'transactions': [
                ('transaction_type', "VARCHAR(30) NOT NULL DEFAULT 'payment'"),
                ('method', 'VARCHAR(30)'),
                ('amount', 'DECIMAL(12,2) NOT NULL DEFAULT 0'),
                ('status', "VARCHAR(30) NOT NULL DEFAULT 'pending'"),
                ('gateway_order_id', 'VARCHAR(100)'),
                ('gateway_payment_id', 'VARCHAR(100)'),
                ('failure_reason', 'VARCHAR(255)'),
                ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
            ]
        }
        for table, cols in migrations.items():
            cur.execute(f'SHOW COLUMNS FROM {table}')
            existing = {row[0] for row in cur.fetchall()}
            for name, definition in cols:
                if name not in existing:
                    cur.execute(f'ALTER TABLE {table} ADD COLUMN {name} {definition}')

        cur.execute("ALTER TABLE orders MODIFY status VARCHAR(30) NOT NULL DEFAULT 'pending'")
        cur.execute("ALTER TABLE payments MODIFY method VARCHAR(30)")
        db.commit()
        return 'Tables created/verified successfully.'
    except Exception as e:
        db.rollback()
        return f'Database setup failed: {e}'
    finally:
        cur.close()
        db.close()
