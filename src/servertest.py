from transmission.tcpservice import TcpListenService
from encryption.sessionservice import ServerSessService
from biz.bizservice import Server


class Conf:
    ...
    
conf = Conf()
conf.ip = "127.0.0.1"
conf.port = 8809
kwargs = vars(conf)


ts = TcpListenService(True, **kwargs)
ss = ServerSessService(ts, **kwargs)
bs = Server(ss, **kwargs)

bs.start()
