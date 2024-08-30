from charm.toolbox.pairinggroup import PairingGroup
from c_client import Client
from c_owner import Owner
from c_ta import TA
from f_login import Login

if __name__ == "__main__":
    groupObj = PairingGroup("SS512")
    ta = TA(groupObj)

    ta.setup()
    # print(ta.get_pk(), '\n\n', ta.get_mk())

    username = input("Enter username: ")
    password = input("Enter password: ")

    if Login(username, password):  #

        while True:
            print("\n=============================================")
            print("             Attribute-Based Encryption")
            print("=============================================")
            print("1. Encrypt File ")
            print("2. Decrypt File (Just for Client)")
            print("0. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":

                owner = Owner(groupObj)
                """
                Menu for encrypting a file by the owner.
                """
                print("\n=============================================")
                print("            Encrypt File")
                print("=============================================")
                plaintext_path = input("Enter the path to the plaintext file: ")
                ciphertext_path = input("Enter the path to save the encrypted file: ")
                """
                Menu for setting the access policy by the owner.
                """
                print("\n=============================================")
                print("           Set Access Policy")
                print("=============================================")
                access_policy = input("Enter the access policy: ")
                owner.set_access_policy(access_policy)
                print("Access policy set.")

                owner.encrypt_file(plaintext_path, ciphertext_path, ta.get_pk())

            elif choice == "2":

                att_list = []  ### beign test
                while True:
                    att = input("Enter an attribute (or 'q' to quit): ")
                    if att == "q":
                        break
                    att_list.append(att.upper())
                print(att_list)  ### end test

                client = Client(groupObj)

                sk = ta.keygen(att_list)
                """
                Menu for decrypting a file by a client.
                """
                print("\n=============================================")
                print("           Decrypt File")
                print("=============================================")
                ciphertext_path = input("Enter the path to the ciphertext file: ")

                plaintext_path = input("Enter the path to save the decrypted file: ")

                client.decrypt_file(ciphertext_path, sk, ta.get_pk(), plaintext_path)

            elif choice == "0":
                break
            else:
                print("Invalid choice. Please try again.")

        print("Exiting...")
    else:
        print("Invalid username or password!!")
