from typing import Optional
import mysql.connector
from mysql.connector import Error
import dlog


class MySQLService:
    def __init__(self, host: str, user: str, password: str, database: str, port: int = 3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection: Optional[mysql.connector.connection_cext.CMySQLConnection] = None
        self.ensure_database_exists()
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                database=self.database
            )
            if self.connection.is_connected():
                cursor = self.connection.cursor()
                cursor.execute("CREATE DATABASE IF NOT EXISTS DOCUMENTS_MANAGER")
                dlog.dlog_i("Connected to MySQL successfully")
        except Exception as exc:
            dlog.dlog_i("Connected to MySQL Unsuccessfully")
            dlog.dlog_e(exc)

    def disconnect(self):
        if self.connection is not None and self.connection.is_connected():
            self.connection.close()
            self.connection = None
            dlog.dlog_i("Disconnected to MySQL successfully")

    def get_health(self):
        if self.connection is not None and self.connection.is_connected():
            return True
        return False

    def create_tables(self):
        create_user_table_query = """
            CREATE TABLE IF NOT EXISTS user (
                id INT AUTO_INCREMENT PRIMARY KEY,
                role VARCHAR(255),
                username VARCHAR(255),
                phone VARCHAR(255),
                password VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            );
        """

        create_files_table_query = """
            CREATE TABLE IF NOT EXISTS documents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                content MEDIUMTEXT,
                title VARCHAR(255),
                filename VARCHAR(255),
                url VARCHAR(255),
                category_id INT,
                user_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
            );
        """

        create_category_table_query = """
            CREATE TABLE IF NOT EXISTS categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            );
        """

        cursor = self.connection.cursor()

        # Execute the queries
        cursor.execute(create_category_table_query)
        cursor.execute(create_user_table_query)
        cursor.execute(create_files_table_query)

        # Commit the changes
        self.connection.commit()

        cursor.close()
        cursor.close()
        dlog.dlog_i("Tables created successfully")

    def ensure_database_exists(self):
        try:
            # Kết nối không chỉ định database
            temp_connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port
            )

            cursor = temp_connection.cursor()
            # Tạo database nếu chưa tồn tại
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            dlog.dlog_i(f"Database '{self.database}' is ready.")
        except Error as exc:
            dlog.dlog_e(f"{exc}")
