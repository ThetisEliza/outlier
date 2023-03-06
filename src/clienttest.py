from transmission.tcpservice import TcpConnectService
from session.sessionservice import ClientSessService, Package
from biz.bizservice import ClientBizService, BizResponse

class Conf:
    ...
    
conf = Conf()
conf.ip = "127.0.0.1"
conf.port = 8809

import time

ts = TcpConnectService(conf, False)
ss = ClientSessService(ts)
bs = ClientBizService(ss)


ts.startconnectloop()
time.sleep(0.5)

# ss.send(Package.buildpackage().add_field("cmd", "connectuser").add_field("name", "Alice"))

bs.connectuser()


import signal
signal.signal(signal.SIGINT, ts.close)
while True:
    a = input()
    bs.process_input(a)
    