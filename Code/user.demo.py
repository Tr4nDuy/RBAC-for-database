from charm.toolbox.pairinggroup import PairingGroup
from charm.core.engine.util import bytesToObject
import socket
import ssl
import pickle
from c_owner import Owner
from c_client import Client
from f_login import FirebaseAuth
import csv


# Thiết lập kết nối SSL/TLS với server
def setup_tls_connection():
    # Tạo context SSL/TLS
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations(cafile=r"server.crt")
    context.check_hostname = False

    # Thiết lập socket kết nối
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_ssl = context.wrap_socket(client, server_hostname=HOST)
    client_ssl.connect((HOST, SERVER_PORT))
    return client_ssl


# Nhận key từ server
def get_key(client):
    data = b""
    while True:
        chunk = client.recv(BUFFER_SIZE)
        if chunk.decode(FORMAT) == "__end__":
            break  # End of data received
        data += chunk

    group = PairingGroup("SS512")
    return bytesToObject(data, group)


# Thiết lập thông tin kết nối
HOST = "127.0.0.1"
SERVER_PORT = 49999
BUFFER_SIZE = 1024
FORMAT = "utf-8"


def get_pk():
    # Thiết lập kết nối SSL/TLS
    client = setup_tls_connection()

    # Thực hiện kết nối và gửi/nhận dữ liệu
    try:
        msg = "get_pubKey"
        client.sendall(msg.encode(FORMAT))
        client.send("x".encode(FORMAT))
        pk = get_key(client)

    except Exception as e:
        print("Error:", e)

    finally:
        client.close()
        return pk


def keygen(att_list):
    # Thiết lập kết nối SSL/TLS
    client = setup_tls_connection()

    # Thực hiện kết nối và gửi/nhận dữ liệu
    try:
        msg = "gen_secretKey"
        client.sendall(msg.encode(FORMAT))
        client.sendall(pickle.dumps(att_list))
        client.send("x".encode(FORMAT))
        sk = get_key(client)

    except Exception as e:
        print("Error:", e)

    finally:
        client.close()
        return sk


if __name__ == "__main__":

    username = input("Enter your email: ")
    password = input("Enter password: ")

    auth = FirebaseAuth()
    userID = auth.Login(username, password)
    print("\nreturn userID:", userID)

    if userID:  # check login success or not
        print("\n----- WELCOME! -----")
        groupObj = PairingGroup("SS512")
        while True:
            print("\n=============================================")
            print("             Attribute-Based Encryption")
            print("=============================================")
            print("1. Encrypt File")
            print("2. Decrypt File")
            print("0. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":

                owner = Owner(groupObj)
                """
                Menu for decrypting a file by a client.
                """
                print("\n=============================================")
                print("             Attribute-Based Encryption")
                print("=============================================")
                print("1. Encrypt data")
                print("2. Encrypt AES key")
                choice2 = input("Enter your choice: ")

                if choice2 == "1":
                    table_name = input("Enter table name: ")
                    column_name = input("Enter column name: ")
                    filekey = input("Enter file to save key: ")

                    owner.Encrypt_AES(
                        table_name=table_name,
                        column_name=column_name,
                        new_column_name=column_name,
                        filekey=filekey,
                    )

                elif choice2 == "2":
                    """
                    Menu for encrypting a file by the owner.
                    """
                    print("\n=============================================")
                    print("            Encrypt AES key")
                    print("=============================================")

                    plaintext_path = input("Enter the path to the key file: ")
                    ciphertext_path = input(
                        "Enter the path to save the encrypted key file: "
                    )

                    # plaintext_path = 'keys.csv'
                    # ciphertext_path = 'en_keys.csv'

                    # """
                    # Menu for setting the access policy by the owner.
                    # """
                    # print("\n=============================================")
                    # print("           Set Access Policy")
                    # print("=============================================")
                    # access_policy = input("Enter the access policy: ")
                    # owner.set_access_policy(access_policy)
                    # print("Access policy set.")
                    # owner.encrypt_file(plaintext_path, ciphertext_path, get_pk())

                    """
                    Menu for setting the access policy by the owner.
                    """
                    print("\n=============================================")
                    print("           Set Access Policy")
                    print("=============================================")
                    # encrypted_data = []
                    pubkey = get_pk()
                    with open(plaintext_path, "r") as csvfile:
                        reader = csv.reader(csvfile)
                        for row in reader:
                            row = ", ".join(row)
                            print("key: ", row)

                            access_policy = input("Enter the access policy: ")
                            owner.set_access_policy(access_policy)
                            # print("Access policy set.")

                            cipher = owner.encrypt_message(
                                row, pubkey, access_policy, ciphertext_path
                            )
                            print(cipher)
                            # encrypted_data.append(cipher)

            elif choice == "2":

                client = Client(groupObj)

                userInfo = auth.get_user_data(user_id=userID)
                userAttr = userInfo.get_attributes()

                print("\nYour userID:", userID)
                print("\nYour userInfo:")
                userInfo.display_info()
                print("\nYour userAttr:", userAttr)
                # print('\nYour secret key:', userInfo.secretkey)

                # userAttr = ['ONE', 'TWO', 'THREE']
                sk = keygen(userAttr)
                # auth.db.child("Users").child(userID).update({'secretkey':sk})
                # print(sk)
                # print(auth.get_user_data(user_id= userID).secretkey)

                """
                Menu for decrypting a file by a client.
                """
                print("\n=============================================")
                print("             Attribute-Based Encryption")
                print("=============================================")
                print("1. Decrypt AES key")
                print("2. Decrypt data")
                choice1 = input("Enter your choice: ")

                if choice1 == "1":
                    ciphertext_path = input("Enter the path to the ciphertext file: ")
                    # ciphertext_path = 'en_keys.csv'
                    plaintext_path = input(
                        "Enter the path to save the decrypted file: "
                    )
                    # plaintext_path = 'de_keys.csv'
                    # client.decrypt_file(ciphertext_path, sk, get_pk(), plaintext_path)
                    client.decrypt_message(
                        ciphertext_path, sk, get_pk(), plaintext_path
                    )

                elif choice1 == "2":
                    keyfile = input("Enter file key: ")
                    colum_name = input("Enter column name: ")
                    client.Decrypt_AES(keyfile, colum_name)

            elif choice == "0":
                break
            else:
                print("Invalid choice. Please try again.")

        print("Exiting...")
    else:
        print("Invalid username or password!!")
