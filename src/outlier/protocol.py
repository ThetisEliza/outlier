'''
Date: 2023-01-07 22:59:34
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-01-17 17:27:55
FilePath: /outlier/src/protocol.py
'''
import json
import hashlib
from datetime import datetime


KEY = "asdqwezxc"

def get_round_time(timestamp):
    curr = datetime.now()
    happening = datetime.fromtimestamp(timestamp)
    delta = curr - happening
    if (delta.days > 0):
        return f"{delta.days} days ago"
    elif delta.seconds // 3600 > 0:
        return f"{delta.seconds // 3600} hours ago"
    elif delta.seconds // 60 > 0:
        return f"{delta.seconds // 60} minutes ago"
    else:
        return "just now"
    
    
    

class Message:
    def __init__(self, msg:str, sender:str, timestamp:float) -> None:
        self._msg = msg
        self._sender = sender
        self._timestamp = timestamp
    
    @property
    def msg(self):
        return self._msg
    
    @property
    def sender(self):
        return self._sender
    
    @property
    def timestamp(self):
        return self._timestamp
        
    def __repr__(self) -> str:
        return f"From:{self._sender:10} - {get_round_time(self._timestamp):20}: {self._msg}"
    
    def jsonallize(self):
        return self.__dict__
    
    @staticmethod
    def parse(**data):
        return Message(data["_msg"], data["_sender"], data["_timestamp"])


class Encrption:    
    def entrypt(data:str, key=KEY) -> bytes:
        hashcode = int(hashlib.md5(key.encode()).hexdigest(), 16) % 128
        out = bytearray()
        for b in data.encode('ascii'):
            b ^= hashcode
            hashcode = b
            out.append(b)
        return bytes(out)  
        
    def decrypt(data:bytes, key=KEY) -> str:
        hashcode = int(hashlib.md5(key.encode()).hexdigest(), 16) % 128
        out = bytearray()
        for b in data:
            pre_b = b
            b ^= hashcode
            hashcode = pre_b
            out.append(b)
        return out.decode('ascii')

class Package:
    def __init__(self, **data) -> None:
        self.data = data
        self.byteflow: bytes = None

    def add_field(self, field: str, value):
        self.data[field] = value
        return self
    
    def add_field_if(self, condition: bool, field: str, value):
        if condition:
            self.data[field] = value
        return self
    
    def add_cmd(self, cmd: str):
        self.data["cmd"] = cmd
        return self
    
    def encrypt(self):
        try:
            data = json.dumps(self.data)
            self.byteflow = Encrption.entrypt(data)
        except Exception as e:
            ...
        return self
    
    def decrypt(self):
        try:
            data = Encrption.decrypt(self.byteflow)
            self.data = json.loads(data)
        except Exception as e:
            self.data = {}
        return self
    
    def get_byteflow(self) -> bytes:
        return self.byteflow
    
    def set_byteflow(self, byteflow):
        self.byteflow = byteflow
        return self
    
    def get_data(self):
        return self.data
    
    def tobyteflow(self) -> bytes:
        return self.encrypt().get_byteflow()
    
    def __repr__(self) -> str:
        return f"data:{self.data}, bytes:{self.byteflow}"  
    
    def view(self, isbtyesrepr=False):
        if isbtyesrepr:
            print(repr(self))
        else:
            print(f"data:{self.data}")
        return self
    
    @staticmethod
    def buildpackage():
        return Package().add_field("timestamp",  datetime.timestamp(datetime.now()))
    
    @staticmethod
    def parsebyteflow(byteflow: bytes):
        return Package().set_byteflow(byteflow).decrypt()
    