from transmission.tcpservice import TcpListenService
from encryption.sessionservice import ServerSessService
from biz.bizservice import Server

class Conf:
    ...
    
conf = Conf()
conf.ip = "127.0.0.1"
conf.port = 8809



ts = TcpListenService(conf, False)
ss = ServerSessService(ts)
bs = Server(ss)

ts.startlistenloop()

import signal
signal.signal(signal.SIGINT, ts.close)
input()
