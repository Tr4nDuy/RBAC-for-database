import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import csv
import pyodbc


class DataDecryptor:
    def __init__(
        self, key_file, column_name, server, database, connection_string, table_name
    ):
        self.key = self.read_key_from_file(key_file, column_name)
        self.iv = self.generate_iv_from_key(self.key)
        self.server = server
        self.database = database
        self.connection_string = connection_string
        self.table_name = table_name
        self.column_name = column_name

    def generate_iv_from_key(self, key):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(key)
        iv = digest.finalize()[:16]
        return iv

    def read_key_from_file(self, filename, column_name):
        with open(filename, "r", newline="") as key_file:
            reader = csv.reader(key_file)
            for row in reader:
                if len(row) > 1 and row[0] == column_name:
                    encoded_key = row[1].strip()
                    key = base64.b64decode(encoded_key.encode("utf-8"))
                    return key
            raise ValueError(f"Column '{column_name}' not found in the key file.")

    def decrypt_data(self, encrypted_data):
        cipher = Cipher(
            algorithms.AES(self.key), modes.CBC(self.iv), backend=default_backend()
        )
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        padding_length = decrypted_data[-1]
        decrypted_data = decrypted_data[:-padding_length]
        return decrypted_data.decode("utf-8")

    def decrypt_database(self):
        conn = pyodbc.connect(self.connection_string)
        cursor = conn.cursor()
        sql = f"SELECT {self.column_name} FROM {self.table_name}"
        cursor.execute(sql)

        with open("plain.csv", "w", newline="") as plain_file:
            writer = csv.writer(plain_file)

            for row in cursor.fetchall():
                encrypted_data = base64.b64decode(getattr(row, self.column_name))
                decrypted_data = self.decrypt_data(encrypted_data)
                writer.writerow([decrypted_data, getattr(row, self.column_name)])

        conn.commit()
        conn.close()
        print("Decrypt data successfully")
