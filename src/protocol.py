import json
from datetime import datetime

def pack(cmd, **param):
    
    return json.dumps({"cmd": cmd, **param})


print(datetime.timestamp(datetime.now()))