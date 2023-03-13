'''
Date: 2023-03-13 14:07:44
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-03-13 19:28:25
FilePath: /outlier/test/test_tmp.py
'''
import base64
import rsa    
from pyDes import des, CBC, PAD_PKCS5 


def retcheck(fn):
    def wrapped(*args, **kwargs):
        ret = fn(*args, **kwargs)
        print(f"After calling {fn.__qualname__}, result {ret}")
        return ret
    return wrapped


class Secret:
    @retcheck
    def encrypt(self, content: str, key=None):
        bytesflow = content.encode()
        return bytesflow
    
    @retcheck
    def decrypt(self, flow: bytes, key=None):
        origin = flow.decode()
        return origin
    
    def get_enc_dec(self):
        return self.encrypt, self.decrypt
    
    
class Base64Secret(Secret):
    @retcheck
    def encrypt(self, content: str, key=None):
        bytesflow = base64.b64encode(content.encode())
        return bytesflow
    
    @retcheck
    def decrypt(self, flow: bytes, key=None):
        origin = base64.b64decode(flow).decode()
        return origin

class DES(Secret):
    @retcheck
    def encrypt(self, content: str, key=None):
        k = des(key, CBC, key, pad=None, padmode=PAD_PKCS5)
        bytesflow = k.encrypt(content.encode(), padmode=PAD_PKCS5)
        return bytesflow
    
    @retcheck
    def decrypt(self, flow: bytes, key=None):
        k = des(key, CBC, key, pad=None, padmode=PAD_PKCS5)
        return k.decrypt(flow, padmode=PAD_PKCS5).decode()
    
  
class RSA(Secret):
    (pub, pri) = rsa.newkeys(512)
    
    
    def encrypt(self, content: str, key=None):
        content = super().encrypt(content, key)
        return rsa.encrypt(content, RSA.pub)
        
    
    def decrypt(self, flow: bytes, key=None):
        content = rsa.decrypt(flow, RSA.pri)
        return super().decrypt(content, key)
    
    


# 1. client fetch pubkey and encrypt a secret key
# 2. server get encrpted secret key and decrypt it with its private key
# 3. confirm the secretkey and use the secrete key to commicate.
# 4. roolling the public key and secret key. Once the communicationg switch the public and private pair, all the communication can never be decrypted.

def showserver(fn):
    def wrapper(*args, **kwargs):
        print(*args, **kwargs)
        ret = fn(*args, **kwargs)
        print(ret)
        return ret
    return wrapper

from dataclasses import dataclass
from threading import Thread

@dataclass
class Conn:
    secret: str
    idx: int

class SACT:
    def __init__(self) -> None:
        self.D = {}
        t = Thread(target=self.rolling_keys)
        t.setDaemon(True)
        t.start()
    
    def get_pub(self):
        return self.pub
    
    def decrypt_with_pri(self, flow):
        content = rsa.decrypt(flow, self.pri)
        return content.decode()
    
    def encrypt(self, content: str, key):
        k = des(key, CBC, key, pad=None, padmode=PAD_PKCS5)
        bytesflow = k.encrypt(content.encode(), padmode=PAD_PKCS5)
        return bytesflow
    
    def rolling_keys(self):
        while True:
            self.pub, self.pri = rsa.newkeys(512)
            print("Rolling keys")
            time.sleep(0.1)
    
    def decrpyt(self, flow: str, key):
        k = des(key, CBC, key, pad=None, padmode=PAD_PKCS5)
        return k.decrypt(flow, padmode=PAD_PKCS5).decode()
    
    
    # @showserver
    def act(self, addr: int, comming_flow=bytes):
        if self.D.get(addr) is not None and self.D[addr].secret:
            try:
                # print("try decrypt with secret")
                decrypted = self.decrpyt(comming_flow, self.D[addr].secret)
                resp = f"resp: {decrypted}"
                return self.encrypt(resp,self.D[addr].secret)
            except Exception as e:
                # print(e)
                ...
        else:
            try:
                # print("not decrypt")
                decryped = comming_flow.decode()
                if 'fetch pub' in decryped:
                    return self.get_pub()
            except Exception as e:
                # print(e)
                ...
                
            try:
                # print("try decrypt with pri")
                decryped = self.decrypt_with_pri(comming_flow)
                if 'secret' in decryped:
                    secret = decryped.strip("secret")
                    # print(f"get secret {secret} from {addr}")
                    self.D[addr] = Conn(secret, addr)
                    return self.encrypt(f"confirming{secret}", self.D[addr].secret)
            except Exception as e:
                # print(e)
                ...
            ...
            
        return f"failed require a new secret channel".encode()
            
        


class CLNT:
    idx = 0
    def __init__(self) -> None:
        self.secret = None
        self.idx = CLNT.idx
        CLNT.idx += 1
    
    def fetch_pub(self, sact: SACT):
        pub = sact.act(self.idx, "fetch pub".encode())
        return pub
        
    def send_secret(self, sact: SACT, secret, pub):
        flow = rsa.encrypt(f"secret{secret}".encode(), pub)
        # print(flow)
        comming_flow = sact.act(self.idx, flow)
        k = des(secret, CBC, secret, pad=None, padmode=PAD_PKCS5)
        decryped = k.decrypt(comming_flow, padmode=PAD_PKCS5).decode()
        if "confirming" in decryped:
            self.secret = secret

    def chat(self, sact: SACT, content: str):
        k = des(self.secret, CBC, self.secret, pad=None, padmode=PAD_PKCS5)
        flow = k.encrypt(content.encode(), padmode=PAD_PKCS5)
        retflow = sact.act(self.idx, flow)
        ret = k.decrypt(retflow, padmode=PAD_PKCS5).decode()
        assert ret == "resp: Hello"
        

import time



# sa = SACT()
# time.sleep(0.3)
# pub = sa.get_pub()
# print(pub)
# pubbytes = pub.save_pkcs1()
# print(pubbytes)
# pubag = rsa.PublicKey.load_pkcs1(pubbytes)
# print(pubag)
# time.sleep(1)

# for _ in range(100):
#     cl = CLNT()
#     pub = cl.fetch_pub(sa)
#     print(pub)
#     print()
#     try:
#         cl.send_secret(sa, "asd12345", pub)
#     except Exception as e:
#         print(e)
#         print("Channel establish failed rebuild")
#         pub = cl.fetch_pub(sa)
#         cl.send_secret(sa, "asd12345", pub)
        
#     print()
#     cl.chat(sa, "Hello")
#     time.sleep(0.1)

                
        
        