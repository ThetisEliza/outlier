from transmission.tcpservice import TcpConnectService
from encryption.sessionservice import ConnectSessService, Package
from biz.bizservice import Client, BizRequest

class Conf:
    ...
    
conf = Conf()
conf.ip = "127.0.0.1"
conf.port = 8809

import time

ts = TcpConnectService(conf, False)
ss = ConnectSessService(ts)
bs = Client(ss)


        
    

ts.startconnectloop()
time.sleep(0.5)

# ss.send(Package.buildpackage().add_field("cmd", "connectuser").add_field("name", "Alice"))

bs.connect()


import signal
signal.signal(signal.SIGINT, ss.close)

while True:
    a = input()
    bs.process_input(a)
    # bs.process_input(a)
    