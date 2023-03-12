'''
Date: 2023-03-08 23:10:22
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-03-12 20:14:55
FilePath: /outlier/src/outlier/encryption/sessionservice.py

This module is to encrypt and decrypt tcp byteflow and provide better interfaces for business layer
'''
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Set

from ..tools.decorators import singleton
from ..tools.events import Ops
from ..transmission.tcpservice import Connection, TcpService
from .protocol import Package



@dataclass
class Session:
    """Encapsuled connection and organize it with group
    """
    conn:   Connection = None
    group:  int       = -1
    
    
class SessionService:
    def __init__(self, service: TcpService, **kwargs) -> None:
        self.tsservice: TcpService = service
        self.tsservice.set_upper_rchandle(self.rchandle)
        self.upper_rchandle = lambda *args: ...
        self.kwargs = kwargs
        
        
    def set_upper_rchandle(self, upper_rchandle):
        self.upper_rchandle = upper_rchandle
        
        
    def send(self, package: Package, session: Session = None):
        try:
            byteflow = self._convert_package_to_byteflow(package)
            self.tsservice.send(byteflow, session.conn)
        except OSError as e:
            logging.debug(f"[Sess layer] send failed {session.conn.addr}")
            
    def send_group(self, bcpackage: Package, *sessions: Session):
        pass
            
        
    def rchandle(self, ops: Ops, conn: Connection, byteflow: bytes = None, *args):
        pass
        
    def _convert_byteflow_to_package(self, byteflow: bytes) -> Package:
        return Package.decrypt(byteflow) if byteflow else Package.buildpackage()
        
    def _convert_package_to_byteflow(self, package: Package) -> bytes:
        return package.encrypt() if package else Package().encrypt()
    
    
    def start(self):
        self.tsservice.startloop()
    
    def close(self, *args):
        logging.debug(f"[Sess layer] close with {args}")
        self.tsservice.close()
    
@singleton    
class ServerSessService(SessionService):
    def __init__(self, service: TcpService, **kwargs) -> None:
        super().__init__(service, **kwargs)
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
        logging.debug(f"[Sess layer] recall {ops}, {conn.addr}, {package}")
        self.upper_rchandle(ops, session, package, *args)
    
    def send(self, package: Package, session: Session = None):
        """to send package to the certain session connecting
        Args:
            package (Package): the sending package
            session (Session, optional): the session where to
        """
        super().send(package, session)
            
                    
    def send_group(self, bcpackage: Package, *sessions: Session):
        for session in sessions:
            if session in self.sesss.values():
                self.send(bcpackage, session)
                
                
@singleton
class ConnectSessService(SessionService):
    def __init__(self, service: TcpService, **kwargs) -> None:
        super().__init__(service, **kwargs)
        self.session = Session(service.conn)
        
    def send(self, package: Package, session: Session = None):
        return super().send(package, session if session is not None else self.session)
    
    def rchandle(self, ops: Ops, conn: Connection, byteflow: bytes = None, *args):
        package = self._convert_byteflow_to_package(byteflow)
        logging.debug(f"[Sess layer] recall {ops}, {conn.addr}, {package}")
        self.upper_rchandle(ops, self.session, package, *args)
        
    