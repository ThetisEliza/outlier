'''
Date: 2023-03-13 19:17:55
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-03-14 18:22:12
FilePath: /outlier/test/test_encryption.py
'''
import unittest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src" ))

from outlier.encryption.protocol import DES, RSA, Base64Encrption, Encryption


class TestEncryption(unittest.TestCase):
    
    test_contents = [
            "Hello world",
            "你好",
            "{'timestamp': 1678706203.87447, 'cmd': 'enterroom', 'param': 'Create and enter room 1'}",
            "⚔️"
            "(*^▽^*)",
            open(__file__, encoding='utf-8').read(),
        ]
    
    
    def test_encryption(self):
        for test_str in TestEncryption.test_contents:
            origin = test_str.encode()
            encrypted = Encryption.encrypt(origin)
            # print(encrypted)
            decrypted = Encryption.decrypt(encrypted)
            self.assertEqual(origin, decrypted)
            
    def test_base64Encrption(self):
        for test_str in TestEncryption.test_contents:
            origin = test_str.encode()
            encrypted = Base64Encrption.encrypt(origin)
            # print(encrypted)
            decrypted = Base64Encrption.decrypt(encrypted)
            self.assertEqual(origin, decrypted)
            
    def test_des(self):
        for test_str in TestEncryption.test_contents:
            origin = test_str.encode()
            encrypted = DES.encrypt(origin)
            # print(encrypted)
            decrypted = DES.decrypt(encrypted)
            self.assertEqual(origin, decrypted)
            
    def test_rsa(self):
        for test_str in TestEncryption.test_contents:
            if len(test_str) < 117:
                origin = test_str.encode()
                encrypted = RSA.encrypt(origin, RSA.pub)
                # print(encrypted)
                decrypted = RSA.decrypt(encrypted, RSA.pri)
                self.assertEqual(origin, decrypted)
        
        
