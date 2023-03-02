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
        self.data = data
        self.byteflow: bytes = None

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
    
    def encrypt(self) -> 'Package':
        try:
            data = json.dumps(self.data)
            self.byteflow = Encrption.entrypt(data)
        except json.JSONDecodeError as e:
            ...
        return self
    
    def decrypt(self) -> 'Package':
        try:
            data = Encrption.decrypt(self.byteflow)
            self.data = json.loads(data)
        except json.JSONDecodeError as e:
            self.data = {}
        return self
    
    def get_byteflow(self) -> bytes:
        return self.byteflow
    
    def set_byteflow(self, byteflow) -> 'Package':
        self.byteflow = byteflow
        return self
    
    def get_data(self) -> dict:
        return self.data
    
    def tobyteflow(self) -> bytes:
        return self.encrypt().get_byteflow()
    
    def __repr__(self) -> str:
        return f"data:{self.data}, bytes:{self.byteflow}"  
    
    def view(self, isbtyesrepr=False) -> 'Package':
        if isbtyesrepr:
            print(repr(self))
        else:
            print(f"data:{self.data}")
        return self
    
    @staticmethod
    def buildpackage() -> 'Package':
        return Package().add_field(Package.TIME,  datetime.timestamp(datetime.now()))
    
    @staticmethod
    def parsebyteflow(byteflow: bytes) -> 'Package':
        return Package().set_byteflow(byteflow).decrypt()
    