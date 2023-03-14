'''
Date: 2023-03-08 23:10:22
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-03-14 13:12:25
FilePath: /outlier/src/outlier/encryption/sessionservice.py

This module is to encrypt and decrypt tcp byteflow and provide better interfaces for business layer
'''
import logging
from dataclasses import dataclass
from typing import Any, Dict

from ..tools.decorators import singleton
from ..tools.events import Ops
from ..transmission.tcpservice import Connection, TcpService
from .protocol import DES, Base64Encrption, Package, RSA, rsa


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
        
        
    def send(self, package: Package, session: Session = None, cls = Base64Encrption, key = None):
        try:
            byteflow = self._convert_package_to_byteflow(package, cls, key)
            self.tsservice.send(byteflow, session.conn)
        except OSError as e:
            logging.debug(f"[Sess layer]\tsend failed {session.conn.addr}")
            
            
            
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
        logging.debug(f"[Sess layer]\tclose with {args}")
        self.tsservice.close()
    
@singleton    
class ServerSessService(SessionService):
    def __init__(self, service: TcpService, **kwargs) -> None:
        super().__init__(service, **kwargs)
        self.sesss: Dict[Any, Session] = dict()
        
    
    def rchandle(self, ops: Ops, conn: Connection, byteflow: bytes = None, *args):
        session = self.sesss.get(conn.addr)
        
        
        if session is not None and session.secret is not None:
            package = self._convert_byteflow_to_package(byteflow, DES, session.secret)
        else:
            package = self._convert_byteflow_to_package(byteflow)
        
        if ops == Ops.Add:
            session = Session(conn)
            self.sesss[conn.addr] = session
            super().send(Package.buildpackage().add_cmd("newconnection"), session)
        elif ops == Ops.Rmv:
            self.sesss.pop(conn.addr)
        elif ops == Ops.Rcv:
            pass
        
            # TODO make a secret channel
            # 1. give public key, skip biz handler
            # 2. confirm secret skip biz handler
            # 3. secret established use biz handler
            if session.secret is None:
                package = self._convert_byteflow_to_package(byteflow)
                if package.get_field("cmd") == "fetchpub":
                    self.send(Package.buildpackage().add_field("pub", RSA.pub.save_pkcs1().decode()), session)
                if package.get_field('secret') is not None:
                    secret = package.get_field("secret")
                    secret = bytes(bytearray(map(int, secret.split('_'))))
                    secret = RSA.decrypt(secret, RSA.pri)
                    super().send(Package.buildpackage().add_cmd("confirm secret"), session, DES, secret)
                    session.secret = secret
        
        
        logging.debug(f"[Sess layer]\trecall {ops}, {conn.addr}")
        self.upper_rchandle(ops, session, package, *args)
    
    def send(self, package: Package, session: Session = None):
        """to send package to the certain session connecting
        Args:
            package (Package): the sending package
            session (Session, optional): the session where to
        """
        if session.secret is not None:
            logging.debug(f"[Sess layer]\tsending DES, {session.conn.addr}, {package}, {session.secret}")
            super().send(package, session, DES, session.secret)
        else:
            logging.debug(f"[Sess layer]\tsending default {session.conn.addr}, {package}, {session.secret}")
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
          
    
    def start(self):
        import time
        super().start()
        time.sleep(0.1)
        pkg = Package.buildpackage().add_cmd("fetchpub")
        self._convert_package_to_byteflow(pkg)
        
    
        
    def send(self, package: Package, session: Session = None):
        
        # TODO make a secrete channel
        
        # 1. fetch public key
        # 2. send secret key with public key
        # 3. start biz communication
        # logging.debug(f"[Sess layer]\tsending, {self.session.conn.addr}, {package}, {self.session.secret}")
        if self.session.secret is not None:
            logging.debug(f"[Sess layer]\tsending DES, {self.session.conn.addr}, {package}, {self.session.secret}")
            super().send(package, session if session is not None else self.session, DES, self.session.secret)
        else:
            logging.debug(f"[Sess layer]\tsending default, {self.session.conn.addr}, {package}, {self.session.secret}")
            super().send(package, session if session is not None else self.session)
        
    
    def rchandle(self, ops: Ops, conn: Connection, byteflow: bytes = None, *args):
        
        # TODO make a scerate channel
        # 1. parse public key
        # 2. parse confirming secrete key and set secrete key
        # 3. user biz communication
        
        if self.session.secret is None:
            package = self._convert_byteflow_to_package(byteflow)
            logging.debug(f"[Sess layer]\trecall {ops}, {conn.addr}, {package}")
            if package.get_field('cmd') == 'newconnection':
                self.send(Package.buildpackage().add_cmd("fetchpub"))
            elif package.get_field('pub') is not None:
                pub = package.get_field('pub').encode()
                pub = rsa.PublicKey.load_pkcs1(pub)
                secret = self.generate_secret(pub)
                print(secret)
                
                self.send(Package.buildpackage().add_field("secret", "_".join(str(a) for a in secret)))
                self.session.secret = b"asd"
                return 
        else:
            package = self._convert_byteflow_to_package(byteflow, DES, b'asd')
            logging.debug(f"[Sess layer]\trecall use secret {ops}, {conn.addr}, {package}")
            if package.get_field('cmd') == "confirm secret":
                print("Confirmed")
        
        self.upper_rchandle(ops, self.session, package, *args)
        
    
    def generate_secret(self, pub):
        return RSA.encrypt("asd".encode(), pub)