from transmission.tcpservice import TcpConnectService
from encryption.sessionservice import ConnectSessService
from biz.bizservice import Client

class Conf:
    ...
    
conf = Conf()
conf.ip = "127.0.0.1"
conf.port = 8809
kwargs = vars(conf)


ts = TcpConnectService(False, **kwargs)
ss = ConnectSessService(ts, **kwargs)
bs = Client(ss, **kwargs)
bs.start()
