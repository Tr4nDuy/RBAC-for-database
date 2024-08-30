import pyodbc


class DatabaseManager:
    def __init__(self, server, database, username, password):
        self.server = server
        self.database = database
        self.username = username
        self.password = password

    def connect(self):
        connection_string = f"Driver={{ODBC Driver 18 for SQL Server}};Server=tcp:{self.server},1433;Database={self.database};Uid={self.username};Pwd={self.password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
        self.conn = pyodbc.connect(connection_string)
        self.cursor = self.conn.cursor()

    def disconnect(self):
        self.conn.close()

    def get_encryption_keys(self, table):
        sql = f"SELECT encryption_key FROM {table}"
        self.cursor.execute(sql)
        encryption_keys = [row.encryption_key for row in self.cursor.fetchall()]
        return encryption_keys

    def save_to_file(self, data, file_path):
        with open(file_path, "w") as file:
            file.write("\n".join(data))

        print("Dữ liệu đã được lưu vào file:", file_path)


server = "1iat.database.windows.net"
database = "ql_cuahang"
username = "CloudSA74ba38a1"
password = "DucTai143140066."
table = "customers"
file_path = "keys.csv"

db_manager = DatabaseManager(server, database, username, password)
db_manager.connect()
encryption_keys = db_manager.get_encryption_keys(table)
db_manager.disconnect()

db_manager.save_to_file(encryption_keys, file_path)
