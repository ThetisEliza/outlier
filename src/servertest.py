from transmission.tcpservice import TcpListenService
from session.sessionservice import ServerSessService
from biz.bizservice import ServerBizService

class Conf:
    ...
    
conf = Conf()
conf.ip = "127.0.0.1"
conf.port = 8809



ts = TcpListenService(conf, False)
ts.startlistenloop()

ss = ServerSessService(ts)
bs = ServerBizService(ss)

import signal
signal.signal(signal.SIGINT, ts.close)
ss.send
input()
