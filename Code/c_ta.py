from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
from charm.adapters.abenc_adapt_hybrid import HybridABEnc


class TA:
    def __init__(self, groupObj):
        self.cpabe = CPabe_BSW07(groupObj)
        self.hyb_abe = HybridABEnc(self.cpabe, groupObj)
        self.pk = None
        self.mk = None

    def setup(self):
        (self.pk, self.mk) = self.hyb_abe.setup()
        # return (self.pk, self.mk)

    def keygen(self, attributes):
        return self.hyb_abe.keygen(self.pk, self.mk, attributes)

    # def encrypt(self, pk, message, access_policy):
    #     return self.hyb_abe.encrypt(pk, message, access_policy)

    # def decrypt(self, pk, sk, ciphertext):
    #     return self.hyb_abe.decrypt(pk, sk, ciphertext)

    def get_pk(self):
        """
        Get the public key.
        """
        return self.pk

    def get_mk(self):
        """
        Get the master key.
        """
        return self.mk
