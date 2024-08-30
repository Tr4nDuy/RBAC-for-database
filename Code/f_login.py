import pyrebase
from userinfo import UserInfo


firebaseConfig = {
    "apiKey": "AIzaSyCkwfyyOvRhiGtn-h-7AuUJtK11Cp3Q4gU",
    "authDomain": "userattribute-a278d.firebaseapp.com",
    "databaseURL": "https://userattribute-a278d-default-rtdb.firebaseio.com",
    "projectId": "userattribute-a278d",
    "storageBucket": "userattribute-a278d.appspot.com",
    "messagingSenderId": "344624997297",
    "appId": "1:344624997297:web:b9a8a15ac38d90fc4b9390",
    "measurementId": "G-998PP2MHCD",
}


class FirebaseAuth:

    def __init__(self, firebase_config=firebaseConfig):
        self.firebase = pyrebase.initialize_app(firebase_config)
        self.auth = self.firebase.auth()
        self.db = self.firebase.database()

    def get_user_data(self, user_id):
        user_ref = self.db.child("Users").child(user_id)
        user_data = user_ref.get().val()
        user_info = UserInfo(
            user_data["username"], user_data["attr_list"], user_data["secretkey"]
        )
        return user_info

    # Login function
    def Login(self, username, password):
        print("Log in...")

        # Email: test@gmail.com
        # Password: 123456

        try:
            resp = self.auth.sign_in_with_email_and_password(username, password)
            print("Authentication successful")

            # Set data for testing
            # try:
            #     attr_list = ['ONE', 'TWO', 'THREE']
            #     data = {
            #         "username": "phuong",
            #         "password": "123",
            #         "attr_list": attr_list,
            #         "secretkey": ""
            #     }

            #     self.db.child("Users").child(resp["localId"]).set(data)
            #     print("Set ok")
            # except Exception as e:
            #     print("Set fail:", str(e))

            # Get response info
            print("\nresponse info:", resp)
            # print('\ntype:', type(resp))
            return resp["localId"]

        except:
            print("Authentication failed")
        return

    # Signup Function
    def signup(self):
        print("Sign up...")
        email = input("Enter email: ")
        password = input("Enter password: ")
        try:
            resp = self.auth.create_user_with_email_and_password(email, password)

            print(resp)
            print(type(resp))

            ask = input("Do you want to login? [y/N] ")
            if ask in "Yy":
                self.Login(email, password)
        except:
            print("Email already exists")
        return


if __name__ == "__main__":

    username = input("Enter your email: ")
    password = input("Enter password: ")

    auth = FirebaseAuth()
    auth.Login(username, password)
