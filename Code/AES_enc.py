import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import pyodbc
import csv
import secrets

"""
This class takes a connection_string argument to establish a connection to the database, and has a method encrypt_column that takes the table name, column name to encrypt, and new column name to store the encrypted data in. The encryption key and IV are generated randomly, and the key is saved to a file using CSV format. The encrypted data is stored in the newly created column in the same table.
"""


class DatabaseEncryptor:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.conn = pyodbc.connect(connection_string)
        self.cursor = self.conn.cursor()

    def __del__(self):
        # Đóng kết nối
        self.conn.close()

    def generate_random_key(self):
        return secrets.token_bytes(32)

    def save_key_to_file(self, filename, key, new_column_name):
        # Encode key to Base64
        encoded_key = base64.b64encode(key)

        # Write column names and encoded_key to file
        with open(filename, "a", newline="") as key_file:
            writer = csv.writer(key_file)
            writer.writerow([new_column_name, encoded_key.decode("utf-8")])

    def generate_iv_from_key(self, key):
        # Tạo đối tượng băm SHA-256
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())

        # Cập nhật dữ liệu cần băm
        digest.update(key)

        # Lấy giá trị băm
        iv = digest.finalize()[:16]
        return iv

    def encrypt_column(self, table_name, column_name, new_column_name, filekey):
        encryption_key = self.generate_random_key()
        iv = self.generate_iv_from_key(encryption_key)
        self.save_key_to_file(filekey, encryption_key, new_column_name)

        # Truy vấn dữ liệu
        sql = f"SELECT {column_name} FROM {table_name}"
        self.cursor.execute(sql)

        # Duyệt qua từng hàng và mã hóa dữ liệu với key và iv tương ứng
        for row in self.cursor.fetchall():
            data = getattr(row, column_name).encode("utf-8")

            print("data:", data)
            print("type:", type(data))

            # Thêm padding cho dữ liệu để có độ dài là bội của 16 byte
            padding_length = 16 - (len(data) % 16)
            data += bytes([padding_length]) * padding_length

            # Mã hóa dữ liệu
            cipher = Cipher(
                algorithms.AES(encryption_key), modes.CBC(iv), backend=default_backend()
            )
            encryptor = cipher.encryptor()
            encrypted_data = encryptor.update(data) + encryptor.finalize()

            print("encrypted_data:", base64.b64encode(encrypted_data).decode("utf-8"))
            print("type:", type(base64.b64encode(encrypted_data).decode("utf-8")))

            # Cập nhật dữ liệu đã mã hóa vào cột "new_column_name"
            update_sql = (
                f"UPDATE {table_name} SET {new_column_name} = ? WHERE {column_name} = ?"
            )
            self.cursor.execute(
                update_sql,
                base64.b64encode(encrypted_data).decode("utf-8"),
                getattr(row, column_name),
            )

        # Lưu các thay đổi vào cơ sở dữ liệu
        self.conn.commit()
        print(
            f"Column '{column_name}' in table '{table_name}' has been encrypted and saved to column '{new_column_name}'"
        )


if __name__ == "__main__":

    # Kết nối tới cơ sở dữ liệu
    connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:1iat.database.windows.net,1433;Database=ql_cuahang;Uid=CloudSA74ba38a1;Pwd={DucTai143140066.};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    encryptor = DatabaseEncryptor(connection_string)
    encryptor.encrypt_column("customers", "password", "password", "key.csv")
