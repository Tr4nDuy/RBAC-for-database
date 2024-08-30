class UserInfo:
    def __init__(self, username, attributes, secretkey):
        self.username = username
        self.attributes = attributes
        self.secretkey = secretkey

    def display_info(self):
        print("\tUsername:", self.username)
        print("\tAttributes:", self.attributes)
        print("\tSecret key:", self.secretkey)

    def get_attributes(self):
        return self.attributes

    def get_secretkey(self):
        return self.secretkey
