from dataclasses import dataclass, field
from typing import List, Set
from transmission.tcpservice import TcpService, Connection, Ops
from .protocol import Package


@dataclass
class Session:
    conn: Connection = None
    group: Set       = -1

class SessionService:
    def __init__(self, service: TcpService) -> None:
        self.tsservice: TcpService = service
        self.tsservice.set_upper_rchandle(self.rchandle)
        self.upper_rchandle = None
        
    def set_upper_rchandle(self, upper_rchandle):
        self.upper_rchandle = upper_rchandle
        
    def send(self, session: Session, package: Package,  bcpackage: Package = None):
        if session is not None:
            byteflow = self._convert_package_to_byteflow(package)
            self.tsservice.send(byteflow, session.conn)
        else:
            print("No session specfied")
        
        
    def rchandle(self, ops: Ops, conn: Connection, byteflow: bytes = None, *args):
        ...
        
    def _convert_byteflow_to_package(self, byteflow: bytes) -> Package:
        return Package.decrypt(byteflow if byteflow else b'')
        
    def _convert_package_to_byteflow(self, package: Package) -> bytes:
        return package.encrypt() if package else b""
    
        
        
        
class ServerSessService(SessionService):
    def __init__(self, service: TcpService) -> None:
        super().__init__(service)
        self.sesss: List[Session] = list()
    
    def rchandle(self, ops: Ops, conn: Connection, byteflow: bytes = None, *args):
        super().rchandle(byteflow, conn, *args)
        session = self._get_session(conn)
        package = self._convert_byteflow_to_package(byteflow)
        if ops == Ops.Add:
            session = Session(conn)
            self.sesss.append(session)
        elif ops == Ops.Rcv:
            # self.send(package, session)
            ...
        elif ops == Ops.Rmv:
            self.sesss.remove(session)
            
        if self.upper_rchandle is not None:
            self.upper_rchandle(ops, session, package, *args)
            
        
    def send(self, session: Session, package: Package, bcpackage: Package = None):
        """to send package to the certain session connecting, or broadcast package
        Args:
            package (Package): the sending package
            session (Session, optional): the session where to
            bcpackage (Package, optional): broadcasting package
            sessions (List[Session], optional): the sessions where broadcasting to
        """
        super().send(session, package)
        if bcpackage:
            byteflow = self._convert_package_to_byteflow(bcpackage)
            
            for other in self.sesss:
                if other.group == session.group and other != session:
                    self.tsservice.send(byteflow, session.conn)
    
    
    def _get_session(self, conn) -> Session:
        for session in self.sesss:
            if session.conn == conn:
                return session
        return None
        

        

class ClientSessService(SessionService):
    def __init__(self, service: TcpService) -> None:
        super().__init__(service)
        
        
    def send(self, package: Package):
        return super().send(Session(self.tsservice.conn), package)
        
        
    def rchandle(self, ops: Ops, conn: Connection, byteflow: bytes = None, *args):
        # print(f"recv {byteflow}")
        super().rchandle(ops, byteflow, conn, *args)
        if self.upper_rchandle is not None:
            session = Session(self.tsservice.conn)
            package = self._convert_byteflow_to_package(byteflow)
            self.upper_rchandle(ops, session, package, *args)
        
        
        
        