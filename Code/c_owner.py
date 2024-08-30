from charm.toolbox.pairinggroup import PairingGroup
from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
from charm.adapters.abenc_adapt_hybrid import HybridABEnc
from charm.core.engine.util import objectToBytes
import pickle
from AES_enc import DatabaseEncryptor


class Owner:
    def __init__(self, groupObj):
        self.groupObj = groupObj
        self.cpabe = CPabe_BSW07(groupObj)
        self.hyb_abe = HybridABEnc(self.cpabe, groupObj)
        self.policies = None

    def set_access_policy(self, policy):
        self.access_policy = policy

    def encrypt_file(self, plaintext_path, ciphertext_path, pk):
        try:
            with open(plaintext_path, "rb") as plaintext_file:
                plaintext = plaintext_file.read()

            ciphertext = self.hyb_abe.encrypt(pk, plaintext, self.access_policy)
            cipher_bytes = objectToBytes(ciphertext, self.groupObj)

            with open(ciphertext_path, "wb") as ciphertext_file:
                pickle.dump(cipher_bytes, ciphertext_file)

            print("...")
            print(
                "The file '" + ciphertext_path + "' created with policies: ",
                self.access_policy,
            )

        except Exception as e:
            print("Failed to ecrypt file: ", str(e))

    def encrypt_message(self, message, pk, access_policy, ciphertext_path):
        try:
            ciphertext = self.hyb_abe.encrypt(pk, message, access_policy)
            cipher_bytes = objectToBytes(ciphertext, self.groupObj)

            with open(ciphertext_path, "ab") as ciphertext_file:
                ciphertext_file.write(cipher_bytes)
                ciphertext_file.write(b"\n")

            return cipher_bytes

        except Exception as e:
            print("Failed to encrypt message:", str(e))
            return None

    def Encrypt_AES(self, table_name, column_name, new_column_name, filekey):
        # Kết nối tới cơ sở dữ liệu
        connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:1iat.database.windows.net,1433;Database=ql_cuahang;Uid=CloudSA74ba38a1;Pwd={DucTai143140066.};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
        encryptor = DatabaseEncryptor(connection_string)
        encryptor.encrypt_column(table_name, column_name, new_column_name, filekey)


if __name__ == "__main__":

    groupObj = PairingGroup("SS512")
    owner = Owner(groupObj)

    table_name = "customers"
    column_name = "password"
    new_column_name = "password"
    filekey = "key.csv"

    owner.Encrypt_AES(table_name, column_name, new_column_name, filekey)
