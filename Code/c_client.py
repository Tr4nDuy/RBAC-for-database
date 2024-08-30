from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
from charm.adapters.abenc_adapt_hybrid import HybridABEnc
from charm.core.engine.util import bytesToObject
import pickle
from AES_dec import DataDecryptor


class Client:
    def __init__(self, groupObj):
        self.groupObj = groupObj
        self.cpabe = CPabe_BSW07(groupObj)
        self.hyb_abe = HybridABEnc(self.cpabe, groupObj)
        self.att = None
        self.sk = None

    def set_attributes(self, attributes):
        self.att = attributes

    def set_secretKey(self, secretKey):
        self.sk = secretKey

    def decrypt_file(self, ciphertext_path, sk, pk, plaintext_path):

        try:
            with open(ciphertext_path, "rb") as ciphertext_file:
                cipher_bytes = pickle.load(ciphertext_file)

            ciphertext = bytesToObject(cipher_bytes, self.groupObj)
            plaintext = self.hyb_abe.decrypt(pk, sk, ciphertext)

            with open(plaintext_path, "wb") as plaintext_file:
                plaintext_file.write(plaintext)

            print("...")
            print("File decrypted successfully !!")

        except Exception as e:
            print("Failed to decrypt file:", str(e))

    def decrypt_message(self, ciphertext_path, sk, pk, plaintext_path):
        try:
            with open(ciphertext_path, "rb") as ciphertext_file:
                with open(plaintext_path, "a") as plaintext_file:
                    while True:
                        try:
                            cipher_bytes = ciphertext_file.readline()
                            if not cipher_bytes:
                                break

                            # Loại bỏ ký tự xuống dòng ở cuối mỗi dòng
                            # print(cipher_bytes)
                            cipher_bytes = cipher_bytes.rstrip(b"\n")

                            ciphertext = bytesToObject(cipher_bytes, self.groupObj)

                            plaintext = self.hyb_abe.decrypt(pk, sk, ciphertext).decode(
                                "utf-8"
                            )

                            print(plaintext, "...success")
                            plaintext_file.write(plaintext)
                            plaintext_file.write("\n")

                        except Exception as e:
                            print("Failed to decrypt key:", str(e))
                            plaintext_file.write("Decryption failed\n")
                            continue

        except Exception as e:
            print("Failed to open ciphertext file:", str(e))

    def Decrypt_AES(self, keyfile, column_name):
        # Sử dụng class DataDecryptor
        server = "1iat.database.windows.net"
        database = "ql_cuahang"
        connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:1iat.database.windows.net,1433;Database=ql_cuahang;Uid=CloudSA74ba38a1;Pwd={DucTai143140066.};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
        table_name = "customers"

        decryptor = DataDecryptor(
            key_file=keyfile,
            column_name=column_name,
            server=server,
            database=database,
            connection_string=connection_string,
            table_name=table_name,
        )
        decryptor.decrypt_database()
