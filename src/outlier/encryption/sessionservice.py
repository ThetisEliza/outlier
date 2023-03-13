'''
Date: 2023-03-08 23:10:22
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-03-13 20:27:46
FilePath: /outlier/src/outlier/encryption/sessionservice.py

This module is to encrypt and decrypt tcp byteflow and provide better interfaces for business layer
'''
import logging
from dataclasses import dataclass
from typing import Any, Dict

from ..tools.decorators import singleton
from ..tools.events import Ops
from ..transmission.tcpservice import Connection, TcpService
from .protocol import DES, Base64Encrption, Package



@dataclass
class Session:
    """Encapsuled connection and organize it with group
    """
    conn:   Connection  = None
    secret: str         = None
    group:  int         = -1
    
    
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
            byteflow = self._convert_package_to_byteflow(package, session.secret)
            self.tsservice.send(byteflow, session.conn)
        except OSError as e:
            logging.debug(f"[Sess layer] send failed {session.conn.addr}")
            
            
    def sendwithBase64(self, package: Package, session: Session = None):
        try:
            byteflow = self._convert_package_to_byteflow(package, session.secret)
            self.tsservice.send(byteflow, session.conn)
        except OSError as e:
            logging.debug(f"[Sess layer] send failed {session.conn.addr}")
            
    def send_group(self, bcpackage: Package, *sessions: Session):
        pass
            
        
    def rchandle(self, ops: Ops, conn: Connection, byteflow: bytes = None, *args):
        pass
        
    def _convert_byteflow_to_package(self, byteflow: bytes, cls = Base64Encrption, key = None) -> Package:
        return Package.decrypt(byteflow, cls, key) if byteflow else Package.buildpackage()
        
    def _convert_package_to_byteflow(self, package: Package, cls = Base64Encrption, key = None) -> bytes:
        return package.encrypt(cls, key) if package else Package().encrypt(cls, key)
    
    
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
        
            # TODO make a secret channel
            
            
            
            if session.secret is None:
                # 1. give public key, skip biz handler
                # 2. confirm secret skip biz handler
                # 3. secret established use biz handler
                session.secret = "asd"
                logging.debug(f"[Sess layer] recall build secret key {ops}, {conn.addr}, {package}")
                self.send(Package.buildpackage().add_field("secret key", session.secret), session)
                return
        
        logging.debug(f"[Sess layer] recall {ops}, {conn.addr}")
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
        self.channel_state = "fetching"
        
        
    def establish(self):
        logging.debug(f"[Sess layer] recall build secret key establish")
        self.send(Package.buildpackage().add_field("establish", "es"))
        
    
    def start(self):
        import time
        super().start()
        time.sleep(0.5)
        self.establish()
        
    def send(self, package: Package, session: Session = None):
        
        # TODO make a secrete channel
        if self.channel_state == "fetching":
            super().send(package, self.session, Base64Encrption)
            # 1. fetch public key
            # 2. send secret key with public key
            # 3. start biz communication
            logging.debug(f"[Sess layer] recall build secret key send")
        
        return super().send(package, session if session is not None else self.session)
    
    def rchandle(self, ops: Ops, conn: Connection, byteflow: bytes = None, *args):
        package = self._convert_byteflow_to_package(byteflow)
        # TODO make a scerate channel
        if self.session.secret is None:
            # 1. parse public key
            # 2. parse confirming secrete key and set secrete key
            # 3. user biz communication
            ...
            self.session.secret = "asd"
            logging.debug(f"[Sess layer] recall build secret key recall {ops}, {conn.addr}, {package}")
            self.send(Package.buildpackage().add_field("establish", "es"))
            return 
        
        logging.debug(f"[Sess layer] recall {ops}, {conn.addr}, {package}")
        self.upper_rchandle(ops, self.session, package, *args)
        
    