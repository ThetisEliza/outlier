'''
Date: 2023-03-08 23:10:22
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-03-14 19:00:55
FilePath: /outlier/src/outlier/encryption/sessionservice.py

This module is to encrypt and decrypt tcp byteflow and provide better interfaces for business layer
'''
import logging
import time
from dataclasses import dataclass
from rsa.pkcs1 import DecryptionError
from typing import Any, Dict

from ..tools.decorators import singleton
from ..tools.events import Ops
from ..tools.threadpool import ThreadPool
from ..tools.utils import RandomGen
from ..transmission.tcpservice import Connection, TcpService
from .protocol import DES, RSA, Base64Encrption, Package


@dataclass
class Session:
    """Encapsuled connection and organize it with group
    """
    conn:   Connection  = None
    group:  int         = -1
    secret: str         = None
    state:  int         = 0
    retry:  int         = 0

class BuildChannelException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
    
class SessionService:
    def __init__(self, service: TcpService, **kwargs) -> None:
        self.tsservice: TcpService = service
        self.tsservice.set_upper_rchandle(self.rchandle)
        self.upper_rchandle = lambda *args: ...
        self.kwargs = kwargs
        
    def set_upper_rchandle(self, upper_rchandle):
        self.upper_rchandle = upper_rchandle
        
    def send(self, package: Package, session: Session = None, cls = Base64Encrption, key = None):
        """General send method, maybe should keep all te parameters here.
        Args:
            package (Package): _description_
            session (Session, optional): _description_. Defaults to None.
            cls (_type_, optional): _description_. Defaults to Base64Encrption.
            key (_type_, optional): _description_. Defaults to None.
        """
        try:
            byteflow = self._convert_package_to_byteflow(package, cls, key)
            self.tsservice.send(byteflow, session.conn)
        except OSError as e:
            logging.warn(f"[Sess layer]\tsend failed {session.conn.addr}")
            
            
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
        ThreadPool().put_task(self._switch_rsa)
          
    def _switch_rsa(self):
        import time
        while True:
            RSA.generate_keys()
            time.sleep(60)
    
    def rchandle(self, ops: Ops, conn: Connection, byteflow: bytes = None, *args):
        session = self.sesss.get(conn.addr)
        if ops == Ops.Add:
            session = Session(conn)
            self.sesss[conn.addr] = session
        elif ops == Ops.Rmv:
            self.sesss.pop(conn.addr)
        elif ops == Ops.Rcv:
            ...
        # make a secret channel
        # 1. give public key, skip biz handler 
        # 2. confirm secret skip biz handler
        # 3. secret established use biz handler
        package = self._channel_state_convert(session, byteflow, ops)
        logging.debug(f"[Sess layer]\trecall {ops}, {conn.addr}")
        self.upper_rchandle(ops, session, package, *args)
    
    def send(self, package: Package, session: Session = None):
        """to send package to the certain session connecting
        Args:
            package (Package): the sending package
            session (Session, optional): the session where to
        """
        if session.secret:
            super().send(package, session, DES, session.secret)
        else:
            super().send(package, session)
            
                    
    def send_group(self, bcpackage: Package, *sessions: Session):
        for session in sessions:
            if session in self.sesss.values():
                self.send(bcpackage, session)
                
    
    def _channel_state_convert(self, session: Session, byteflow: bytes, ops: Ops) -> Package:
        """server session start conversion
        
        0: init state
        1: waiting secret
        2: waiting ack
        5: check

        if any of 0->1, 1->2, 2->5 fails, back to 0

        Args:
            session (Session): _description_
            byteflow (bytes): _description_
            ops (Ops): _description_
        """
        if ops == Ops.Add:
            session.state = 0
        try:
            if session.state == 0:
                self.send(Package.buildpackage().add_field("session_pub", RSA.pub.save_pkcs1().decode()), session)
                session.state = 1
                session.retry += 1
                if session.retry >=3:
                    self.tsservice._rchandle(Ops.Rmv, session.conn, session.conn.sock.fileno())
                return self._convert_byteflow_to_package(byteflow)
            
            elif session.state == 1:
                # reveive secret
                # send secret
                # waiting for confirm
                package = self._convert_byteflow_to_package(byteflow)
                if package.get_field('session_secret') is not None:
                    secret = package.get_field("session_secret")
                    secret = bytes(bytearray(map(int, secret.split('_'))))
                    secret = RSA.decrypt(secret, RSA.pri)
                    session.secret = secret
                    self.send(Package.buildpackage().add_field("session_confirm", True), session)
                    session.state = 2
                    return package
                else:
                    raise BuildChannelException("no `secret` found")
            elif session.state == 2:
                # receive confirm 
                package = self._convert_byteflow_to_package(byteflow, DES, session.secret)
                if package.get_field('session_ack') is True:
                    session.state = 5
                    return package
                else:
                    raise BuildChannelException("no `ack` found")
            elif session.state == 5:
                return self._convert_byteflow_to_package(byteflow, DES, session.secret)
        except (BuildChannelException, DecryptionError, ValueError) as e:
            from traceback import print_exc
            logging.debug(f"[Sess layer]\tbuild channel failed at {print_exc()} retrying")
            logging.warn(f"[Sess layer]\tbuild channel failed at {e}")
            session.state = 0
            session.secret = None
            self.send(Package.buildpackage().add_field("session_state", -1), session)
        return Package.buildpackage()

                
@singleton
class ConnectSessService(SessionService):
    def __init__(self, service: TcpService, **kwargs) -> None:
        super().__init__(service, **kwargs)
        self.session    = Session(service.conn)
        self.session.state = 1
        self.key: bytes = kwargs.get("key", RandomGen.getrandomvalue()[:6]).encode()
        self.ready      = False
        
    def start(self):
        super().start()
    
        
    def send(self, package: Package, session: Session = None):
        session = session if session is not None else self.session
        if self.session.secret is not None:
            super().send(package, session, DES, self.session.secret)
        else:
            super().send(package, session)
        
    
    def rchandle(self, ops: Ops, conn: Connection, byteflow: bytes = None, *args):
        # 1. parse public key
        # 2. parse confirming secrete key and set secrete key
        # 3. user biz communication
        if byteflow is not None:
            package = self._channel_state_convert(self.session, byteflow, ops)
            self.upper_rchandle(ops, self.session, package, *args)
        
        
    def _channel_state_convert(self, session: Session, byteflow: bytes, ops: Ops) -> Package:
        """client session start conversion
        
        0: backup state, ask for pubkey
        1: waiting for pubkey
        2: waiting for confirm
        5: check

        if any of 0->1, 1->2, 2->5 fails, back to 0

        Args:
            session (Session): _description_
            byteflow (bytes): _description_
            ops (Ops): _description_

        Raises:
            BuildChannelException: _description_
            BuildChannelException: _description_

        Returns:
            Package: _description_
        """
        try:
            package = self._convert_byteflow_to_package(byteflow)
            if package.get_field('session_state') == -1:
                raise BuildChannelException("server confirming failded")
                
            if session.state == 1:
                # reveive secret
                # send secret
                # waiting for confirm
                package = self._convert_byteflow_to_package(byteflow)
                if package.get_field('session_pub') is not None:
                    pub = package.get_field('session_pub')
                    print(f"Get public key {pub}\n")
                    pub = RSA.load_public_key(pub.encode())
                    secret = RSA.encrypt(self.key, pub)
                    print(f"Sending your secret key {self.key} on {secret}\n")
                    self.send(Package.buildpackage().add_field("session_secret", "_".join(str(a) for a in secret)))
                    self.session.secret = self.key
                    session.state = 2
                    return package
                else:
                    raise BuildChannelException("no `session_pub` found")
            elif session.state == 2:
                # receive confirm 
                package = self._convert_byteflow_to_package(byteflow, DES, session.secret)
                if package.get_field('session_confirm'):
                    self.send(Package.buildpackage().add_field("session_ack", True))
                    print(f"Server confirmed your key\n")
                    session.state = 5
                    self.ready = True
                    time.sleep(1)
                    print(f"Channel built\n")
                else:
                    raise BuildChannelException("no `session_confirm` found")
            elif session.state == 5:
                return self._convert_byteflow_to_package(byteflow, DES, session.secret)
        except (Exception, ValueError) as e:
            from traceback import print_exc
            logging.debug(f"[Sess layer]\tbuild channel failed at {print_exc()} retrying")
            session.state = 1
            session.secret = None
            session.retry += 1
            print("--- retry ---")
            if session.retry >= 5:
                self.close()
            else:
                self.send(Package.buildpackage(), session)
        return Package.buildpackage()
    