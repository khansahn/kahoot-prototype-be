import unittest

from ..utils.crypt import encrypt, decrypt

class TestCryptMethods(unittest.TestCase) :

    def testEncrypt(self):
        self.assertEqual(encrypt("keys"),"rl5z")
        self.assertEqual(encrypt("haha"),"rl5z")

    def testDecrypt(self):
        self.assertEqual(decrypt("rl5z"),"haha")
        self.assertEqual(decrypt("rl5z"),"keys")



if __name__ == "__main__" :
    unittest.main()