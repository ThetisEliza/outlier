from transmission.tcpservice import TcpConnectService
from session.sessionservice import ClientSessService

class Conf:
    ...
    
conf = Conf()
conf.ip = "127.0.0.1"
conf.port = 8809



ts = TcpConnectService(conf, False)
ts.startconnectloop()

c = ClientSessService(ts)

import signal
signal.signal(signal.SIGINT, ts.close)
while True:
    a = input()
    c.send(a.encode())
    