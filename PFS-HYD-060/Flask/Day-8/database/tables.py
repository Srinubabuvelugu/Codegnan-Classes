from database.connection import DatabaseConnection


def createTables():
    try:
        db_config = DatabaseConnection()
        cursor = db_config.cursor()

        users_table_query = """create table if not exists users(
            userid bigint auto_increment primary key,
            username varchar(50) not null,
            email varchar(100) not null unique,
            hashpassword varchar(255) not null,
            is_active boolean default true,
            created_at timestamp default current_timestamp
            )"""
        notes_table_query = """create table if not exists notes(
            notesid bigint auto_increment primary key,
            userid bigint,
            title varchar(255) not null,
            content text not null,
            created_at timestamp default current_timestamp,
            updated_at timestamp default current_timestamp on update current_timestamp,
            foreign key(userid) references users(userid)
            on delete cascade
            )"""
        files_table_query = """create table if not exists files(
            fileid bigint auto_increment primary key,
            userid bigint,
            originalname varchar(100) not null,
            storedname varchar(100) not null,
            mimetype varchar(255) not null,
            size int,
            filepath varchar(255),
            created_at timestamp default current_timestamp,
            foreign key(userid) references users(userid)
            on delete cascade
            )"""
        cursor.execute(users_table_query)
        cursor.execute(notes_table_query)
        cursor.execute(files_table_query)
        cursor.close()
        db_config.close()
        return "Tables created"

    except Exception as e:
        return f"Something wrong in database/tables.py:{e}"