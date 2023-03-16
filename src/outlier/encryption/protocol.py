'''
Date: 2023-03-08 23:10:22
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-03-14 18:19:09
FilePath: /outlier/src/outlier/encryption/protocol.py

'''

import base64
import hashlib
import json
from datetime import datetime

import rsa
from pyDes import CBC, PAD_PKCS5, des

KEY = "asdqwezxc"

    

class Encryption:
    @classmethod
    def encrypt(cls, data:bytes, key=KEY) -> bytes:
        hashcode = int(hashlib.md5(key.encode()).hexdigest(), 16) % 256
        out = bytearray()
        for b in data:
            b ^= hashcode
            hashcode = b
            out.append(b)
        return bytes(out)  
    
    @classmethod
    def decrypt(cls, data:bytes, key=KEY) -> bytes:
        hashcode = int(hashlib.md5(key.encode()).hexdigest(), 16) % 256
        out = bytearray()
        for b in data:
            pre_b = b
            b ^= hashcode
            hashcode = pre_b
            out.append(b)
        return bytes(out)  
    

class Base64Encrption(Encryption):
    @classmethod
    def encrypt(cls, content: bytes, key=None) -> bytes:
        bytesflow = base64.b64encode(content)
        return bytesflow

    @classmethod
    def decrypt(cls, flow: bytes, key=None) -> bytes:
        origin = base64.b64decode(flow)
        return origin
    
    
class DES(Encryption):
    SALT = b"outlier_bypassed_you"
    
    
    @classmethod
    def encrypt(cls, content: bytes, key = b"") -> bytes:
        key = (key + DES.SALT)[:8]
        k = des(key, CBC, key, pad=None, padmode=PAD_PKCS5)
        bytesflow = k.encrypt(content, padmode=PAD_PKCS5)
        bytesflow = Base64Encrption.encrypt(bytesflow)
        return bytesflow

    @classmethod
    def decrypt(cls, flow: bytes, key = b"") -> bytes:
        key = (key + DES.SALT)[:8]
        flow = Base64Encrption.decrypt(flow)
        k = des(key, CBC, key, pad=None, padmode=PAD_PKCS5)
        flow = k.decrypt(flow, padmode=PAD_PKCS5)
        return flow

    
class RSA(Encryption):
    pub, pri = rsa.newkeys(1024)
    @classmethod
    def load_public_key(cls, pub: bytes) -> rsa.PublicKey:
        return rsa.PublicKey.load_pkcs1(pub)
    
    @classmethod
    def generate_keys(cls, n=1024):
        RSA.pub, RSA.pri = rsa.newkeys(n)
    
    @classmethod
    def encrypt(cls, content: bytes, pub):
        content = Base64Encrption.encrypt(content)
        return rsa.encrypt(content, pub)
        
    @classmethod
    def decrypt(cls, flow: bytes, pri):
        flow = rsa.decrypt(flow, pri)
        return Base64Encrption.decrypt(flow)
    
    
    
class Package:
    """Package for communication, encapsuling `timestamp`, `cmd` and parameters,
    better be initialized with `Package.buildpackage`
    """
    
    CMD     = "cmd"
    TIME    = "timestamp"
    
    def __init__(self, **data) -> None:
        self.data = data if data is not None else dict()

    def add_field(self, field: str, value) -> 'Package':
        self.data[field] = value
        return self
    
    def add_field_if(self, condition: bool, field: str, value) -> 'Package':
        if condition:
            self.data[field] = value
        return self
    
    def add_cmd(self, cmd: str) -> 'Package':
        self.data[Package.CMD] = cmd
        return self
    
    def encrypt(self, cls = Base64Encrption, key = None) -> bytes:
        try:
            data = json.dumps(self.data).encode()
            return  cls.encrypt(data, key)
        except (json.JSONDecodeError, UnicodeEncodeError) as e:
            return b""
        
    @staticmethod
    def decrypt(byteflow: bytes, cls = Base64Encrption, key = None) -> 'Package':
        try:
            data = cls.decrypt(byteflow, key).decode()
            data = json.loads(data)
            return Package(**data)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            return Package()
    
    @staticmethod
    def buildpackage() -> 'Package':
        return Package().add_field(Package.TIME,  datetime.timestamp(datetime.now()))
    
    
    def __repr__(self) -> str:
        return f"{self.data}"  
    
    def __getitem__(a, b):
        return a.data.get(b, None)
    
    def __setitem__(a, b, c):
        a.data[b] = c
            
    def get_field(self, item, default=None):
        ret = self.data.get(item)
        return ret if ret is not None else default
    
        
    