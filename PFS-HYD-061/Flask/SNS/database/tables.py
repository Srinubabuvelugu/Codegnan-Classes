from database.connection import DatabaseConnection

# tables defination function
def createTables():
    try:
        db_config = DatabaseConnection()
        cursor = db_config.cursor()

        users_table_query = """create table if not exists users(
                            userid bigint auto_increment primary key,
                            username varchar(100) not null,
                            email varchar(100) not null unique,
                            hashpassword varchar(255) not null,
                            created_at timestamp default current_timestamp
                        );"""
        notes_table_query = """create table if not exists notes(
                        notesid bigint auto_increment primary key,
                        userid bigint not null,
                        title varchar(100) not null, 
                        content text not null,
                        created_at timestamp default current_timestamp,
                        updated_at timestamp default current_timestamp on update current_timestamp,
                        foreign key(userid) references users(userid)
                        );"""
        files_table_query = """create table if not exists files(
                            fileid bigint auto_increment primary key,
                            userid bigint not null,
                            filename varchar(100) not null,
                            uniquefilename varchar(255) not null, 
                            mimetype varchar(100),
                            filepath varchar(255) not null,
                            filesize int,
                            created_at timestamp default current_timestamp,
                            foreign key(userid) references users(userid)
                        );"""
        # execute the table queries
        cursor.execute(users_table_query)
        cursor.execute(notes_table_query)
        cursor.execute(files_table_query)
        db_config.close()
        cursor.close()

        return "Tables created successfully"
    except Exception as e:
        return f"Something wrong in database.tables.createTables():{e}"