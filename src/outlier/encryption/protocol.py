import hashlib
import json
from datetime import datetime

KEY = "asdqwezxc"

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
    
    def encrypt(self) -> bytes:
        try:
            data = json.dumps(self.data)
            return Encrption.entrypt(data)
        except json.JSONDecodeError as e:
            # print(e)
            return b""
        
    @staticmethod
    def decrypt(byteflow: bytes) -> 'Package':
        try:
            data = Encrption.decrypt(byteflow)
            # print(data)
            data = json.loads(data)
            return Package(**data)
        except json.JSONDecodeError as e:
            # print(e)
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
    
        
    