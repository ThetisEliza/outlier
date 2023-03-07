from dataclasses import dataclass, field
from typing import List, Set, Dict, Any
from transmission.tcpservice import TcpService, Connection, Ops
from .protocol import Package

@dataclass
class Session:
    conn:   Connection = None
    group:  int       = -1
    
    
class SessionService:
    def __init__(self, service: TcpService) -> None:
        self.tsservice: TcpService = service
        self.tsservice.set_upper_rchandle(self.rchandle)
        self.upper_rchandle = lambda *args: ...
        
        
    def set_upper_rchandle(self, upper_rchandle):
        self.upper_rchandle = upper_rchandle
        
        
    def send(self, package: Package, session: Session = None):
        try:
            byteflow = self._convert_package_to_byteflow(package)
            self.tsservice.send(byteflow, session.conn)
        except OSError as e:
            print(f"[Sess layer] send failed {session.conn.addr}")
            
    def send_group(self, bcpackage: Package, session: Session = None):
        pass
            
        
    def rchandle(self, ops: Ops, conn: Connection, byteflow: bytes = None, *args):
        pass
        
    def _convert_byteflow_to_package(self, byteflow: bytes) -> Package:
        return Package.decrypt(byteflow) if byteflow else Package.buildpackage()
        
    def _convert_package_to_byteflow(self, package: Package) -> bytes:
        return package.encrypt() if package else Package().encrypt()
    
    def close(self, *args):
        print(f"[Sess layer] close with {args}")
        self.tsservice.close()
    
    
class ServerSessService(SessionService):
    def __init__(self, service: TcpService) -> None:
        super().__init__(service)
        self.sesss: Dict[Any, Session] = dict()
    
    def rchandle(self, ops: Ops, conn: Connection, byteflow: bytes = None, *args):
        package = self._convert_byteflow_to_package(byteflow)
        session = self.sesss.get(conn.addr)
        if ops == Ops.Add:
            session = Session(conn)
            self.sesss[conn.addr] = session
        elif ops == Ops.Rmv:
            self.sesss.pop(conn.addr)
        elif ops == Ops.Rcv:
            pass
        # self.send(session, package)
        # self.send_group(session, package.add_field("notes", "bc").add_field("from", session.conn.addr))
        print(f"[Sess layer] recall {ops}, {conn.addr}, {package}")
        self.upper_rchandle(ops, session, package, *args)
    
    def send(self, package: Package, session: Session = None):
        """to send package to the certain session connecting
        Args:
            package (Package): the sending package
            session (Session, optional): the session where to
        """
        super().send(package, session)
            
                    
    def send_group(self, bcpackage: Package, session: Session = None):
        for other in self.sesss:
            if other != session.conn.addr and session.group == self.sesss[other].group:
                othersession = self.sesss[other] 
                super().send(bcpackage, othersession)
                
        
class ConnectSessService(SessionService):
    def __init__(self, service: TcpService) -> None:
        super().__init__(service)
        self.session = Session(service.conn)
        
    def send(self, package: Package, session: Session = None):
        return super().send(package, session if session is not None else self.session)
    
    def rchandle(self, ops: Ops, conn: Connection, byteflow: bytes = None, *args):
        package = self._convert_byteflow_to_package(byteflow)
        print(f"[Sess layer] recall {ops}, {conn.addr}, {package}")
        self.upper_rchandle(ops, self.session, package, *args)
        
    