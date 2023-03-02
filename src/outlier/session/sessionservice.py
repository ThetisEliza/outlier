from dataclasses import dataclass

from transmission.tcpservice import TcpService, Connection
from .protocol import Package


@dataclass
class Session:
    conn: Connection


class SessionService:
    def __init__(self, service: TcpService) -> None:
        self.tsservice: TcpService = service
        self.tsservice.set_recvrchd(self.recvhandle)
        
    
        
    def _convert_msg_to_package(self, msg):
        print("package")
        return msg
        
    def _convert_package_to_msg(self, package):
        return package
        
    def send(self, package: Package, session: Session = None):
        msg = self._convert_package_to_msg(package)
        self.tsservice.send(msg, session.conn)
        
        
    def recvhandle(self, msg: bytes, conn:Connection, *args):
        ...
        
        
class ServerSessService(SessionService):
    def __init__(self, service: TcpService) -> None:
        super().__init__(service)
        
    def recvhandle(self, msg: bytes, conn:Connection, *args):
        super().recvhandle(msg, conn, *args)
        self.tsservice.send(msg, conn)
        

class ClientSessService(SessionService):
    def __init__(self, service: TcpService) -> None:
        super().__init__(service)
        
        
    def send(self, package: Package, session: Session = None):
        return super().send(package, Session(self.tsservice.sock))
        
        
    def recvhandle(self, msg: bytes, conn: Connection, *args):
        print(f"recv {msg}")
        return super().recvhandle(msg, conn, *args)
        
        
        
        