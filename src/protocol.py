import json
import hashlib
from datetime import datetime

class Command:
    FETCH = "fetch"
    SYNC  = "sync"
    DS    = "disconnect"


KEY = "asdqwezxc"

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
        return f"From:{self._sender} - {self._timestamp}: {self._msg}"
    
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
            self.byteflow = "err"
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
    
    @staticmethod
    def buildpackage():
        return Package().add_field("timestamp",  datetime.timestamp(datetime.now()))
    
    @staticmethod
    def parsebyteflow(byteflow: bytes):
        return Package().set_byteflow(byteflow).decrypt()
    