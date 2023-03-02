from dataclasses import dataclass
from typing import List, Dict
from transmission.tcpservice import TcpService, Connection, Ops
from .protocol import Package


@dataclass
class Session:
    conn: Connection


class SessionService:
    def __init__(self, service: TcpService) -> None:
        self.tsservice: TcpService = service
        self.tsservice.set_upper_rchandle(self.rchandle)
        
    def _convert_msg_to_package(self, msg):
        print("package")
        return msg
        
    def _convert_package_to_msg(self, package):
        return package
        
    def send(self, package: Package, session: Session = None):
        if session is not None:
            msg = self._convert_package_to_msg(package)
            self.tsservice.send(msg, session.conn)
        else:
            print("No session specfied")
        
        
    def rchandle(self, ops: Ops, conn: Connection, msg: bytes = None, *args):
        ...
        
        
class ServerSessService(SessionService):
    def __init__(self, service: TcpService) -> None:
        super().__init__(service)
        self.sesss: List[Session] = list()
    
    def rchandle(self, ops: Ops, conn: Connection, msg: bytes = None, *args):
        super().rchandle(msg, conn, *args)
        session = self._get_session(conn)
        if ops == Ops.Add:
            self.sesss.append(Session(conn))
        elif ops == Ops.Rcv:
            self.send(self._convert_msg_to_package(msg), session)
        elif ops == Ops.Rmv:
            self.sesss.remove(session)
                    
    def _get_session(self, conn) -> Session:
        for session in self.sesss:
            if session.conn == conn:
                return session
        return None
        
        
        
    def send(self, package: Package, session: Session = None, bcpackage: Package = None, sessions: List[Session] = list()):
        """to send package to the certain session connecting, or broadcast package
        Args:
            package (Package): the sending package
            session (Session, optional): the session where to.
            bcpackage (Package, optional): broadcasting package.
            sessions (List[Session], optional): the sessions where broadcasting to.
        """
        super().send(package, session)    
        if bcpackage:
            msg = self._convert_package_to_msg(bcpackage)
            for session in sessions:
                self.tsservice.send(msg, session.conn)
    

        

class ClientSessService(SessionService):
    def __init__(self, service: TcpService) -> None:
        super().__init__(service)
        
        
    def send(self, package: Package):
        return super().send(package, Session(self.tsservice.sock))
        
        
    def recvhandle(self, msg: bytes, conn: Connection, *args):
        print(f"recv {msg}")
        return super().recvhandle(msg, conn, *args)
        
        
        
        