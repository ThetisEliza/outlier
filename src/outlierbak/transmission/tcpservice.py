'''
Date: 2023-03-08 23:10:22
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-03-14 18:06:24
FilePath: /outlier/src/outlier/transmission/tcpservice.py

This module is to provide stable and reliable layer communication as tcp protocol
'''

import logging
import select
import socket
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict

from ..tools.events import Ops
from ..tools.decorators import onexit, singleton
from ..tools.threadpool import ThreadPool


@dataclass
class Connection:
    sock: socket.socket
    addr: Any
    last: float
    
    
class TcpService:
    
    """This service is to use epoll to provide a bi-direction
    tcp channel, we hope it can be general for both the server and
    the client
    """
    def __init__(self, is_block: bool = False, **kwargs) -> None:
        self.sock = socket.socket()
        # self.epctl = select.epoll()
        self.threadpool = ThreadPool()           
        self.is_block = is_block
        self.rlist = []
        self.kwargs = kwargs
        self.loop = True
        self.upper_rchandle: Callable[[Ops, Connection, bytes, Any], Any] = lambda *args: ...
        self.conn = Connection(self.sock, None, -1)
            
    def send(self, byteflow: bytes, conn: Connection = None):
        """Actively send message to connection

        Args:
            byteflow (bytes): data
            conn (Connection, optional): connection.
        """
        if conn:
            logging.debug(f"[Tcp layer]\tsending {conn.addr}, {byteflow}")
            conn.sock.send(byteflow)
            
        
    def set_upper_rchandle(self, upper_rchandle: Callable[[Ops, Connection, bytes, Any], Any]):
        """This is provided for upper service to invoke recall funcion.
        Invoked at the time when socket received buffer data.
        Args:
            upper_rchandle (Callable[[Ops, Connection, bytes, Any], Any]): The func to be invoked by upper layer.
        """
        self.upper_rchandle = upper_rchandle
    
    def _rchandle(self, ops: Ops, conn: Connection, fd:int = -1, byteflow: bytes = None, *args):
        """Handling the event when something happens on the socket, for server, the event
        for ADD, RECEIVE and REMOVE should be handled, and for clients, the event of REVEIVE and
        ERROR connection should be handled

        Args:
            ops (Ops): Ops
            conn (Connection): connection encapsuled socket
            fd (int, optional): _description_. the file decriptor for socket
            byteflow (bytes, optional): _description_. incomming message flow
        """
        pass 
        
    def _loop(self):
        pass
        
    def startloop(self):
        """This start loop goes as to start the loop for connection receiving, blocking run if 
        instance variable `is_block` is set, otherwise, runs in the thread pool.
        """
        if self.is_block:
            self._loop()
        else:
            self.threadpool.put_task(self._loop)
        
    @onexit
    def close(self, *args):
        """Exiting method for close `loop`, `epoll`, `thread pool` and `socket`
        """
        logging.debug(f"[Tcp layer]\tclose")
        self.loop = False
        # self.epctl.close()
        self.threadpool.close()
        self.sock.close()
        
        
        
@singleton
class TcpListenService(TcpService):
    """This service is a tcp listener used as a server
    """
    def __init__(self, is_block: bool, **kwargs) -> None:
        super().__init__(is_block, **kwargs)
        self.conns: Dict[int, Connection] = dict()
        self.threadpool.put_task(self._tcp_guard)
        
        
    def _rchandle(self, ops: Ops, conn: Connection, fd: int = -1, byteflow: bytes = None, *args):
        logging.debug(f"[Tcp layer]\trecall {ops}, {conn.addr}, {fd}, {len(byteflow) if byteflow else None}")
        if ops == Ops.Add:
            self.conns[fd] = conn
            # self.epctl.register(conn.sock, select.EPOLLIN)
            self.rlist.append(fd)
        elif ops == Ops.Rmv:
            try:
                self.rlist.remove(fd)
                conn = self.conns.get(fd)
                conn.sock.close()
            finally:
                del self.conns[fd]
            logging.debug(f"close {conn.addr}")    
        conn.last = datetime.now().timestamp()
        self.upper_rchandle(ops, conn, byteflow, *args)

    
    def _loop(self):
        ssock = self.sock
        ssock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        ip, port = self.kwargs.get('ip'), self.kwargs.get('port')
        ssock.bind((ip, port))
        ssock.listen(5)
        # self.epctl = select.epoll()
        # self.epctl.register(ssock, select.EPOLLIN)
        self.rlist.append(ssock.fileno())
        logging.info(f"start listen on ip {ip}, port {port}")
        logging.debug(f"using select")
        while self.loop:
            rl, _, _ = select.select(self.rlist, [], [], 0.1)
            # events = self.epctl.poll()
            for fd in rl:
                if fd == ssock.fileno():
                    sock, addr = ssock.accept()
                    self.threadpool.put_task(self._rchandle, args=(Ops.Add, Connection(sock, addr, datetime.now().timestamp()), sock.fileno()))
                else:
                    try:
                        conn = self.conns[fd]
                        byteflow = conn.sock.recv(1024)
                        if len(byteflow) == 0:
                            raise ConnectionAbortedError()
                        self.threadpool.put_task(self._rchandle, args=(Ops.Rcv, conn, fd, byteflow))
                    except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError, ConnectionRefusedError):
                        self._rchandle(Ops.Rmv, conn, fd)
                    except KeyError:
                        logging.debug(f"Conn fd {fd} not found, ignore")
    
    def startlistenloop(self):
        self.startloop()
        
        
    def _tcp_guard(self):
        max_idle = self.kwargs.get('roomgard', 3600)
        import time
        while True:
            rms = []
            for fd, conn in self.conns.items():
                if datetime.now().timestamp() - conn.last > max_idle:
                    logging.info(f"tcp guards remove {conn.addr}")
                    rms.append((conn, fd))
            for conn, fd in rms:
                self._rchandle(Ops.Rmv, conn, fd)
            time.sleep(1)
        
        
    @onexit
    def close(self, *args):
        for fd in self.conns:
            self.conns.get(fd).sock.close()
        super().close()
        
        
@singleton  
class TcpConnectService(TcpService):
    """This service is a tcp listener used as a client
    """
    def __init__(self, is_block: bool, **kwargs) -> None:
        super().__init__(is_block, **kwargs)
        
        
    def startconnectloop(self):
        self.startloop()
    
    def _loop(self):
        try:
            ip, port = self.kwargs.get('ip'), self.kwargs.get('port')
            self.sock.connect((ip, port))
        except (ConnectionRefusedError, socket.gaierror) as e:
            print(f"Connecting to server {ip}:{port} failed, please check your ip and port carefully.")
            self.close()
        # self.epctl.register(self.sock, select.EPOLLIN)  
        self.rlist.append(self.sock.fileno())     
        self.conn.addr = self.sock.getsockname()
        while self.loop:
            # events = self.epctl.poll()
            rl, _, _ = select.select(self.rlist, [], [], 0.1)
            for fd in rl:
                if fd == self.sock.fileno():
                    try:
                        byteflow = self.sock.recv(1024)
                        if len(byteflow) == 0:
                            raise ConnectionAbortedError()
                        self.threadpool.put_task(self._rchandle, args=(Ops.Rcv, self.conn, fd, byteflow))
                    except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError, ConnectionRefusedError):
                        logging.debug("[Tcp layer]\tserver failed")
                        print(f"Server failed")
                        self.close()
                        

    def _rchandle(self, ops: Ops, conn: Connection, fd: int = -1, byteflow: bytes = None, *args):
        logging.debug(f"[Tcp layer]\trecall {ops}, {conn.addr}, {fd}, {len(byteflow) if byteflow else None}")
        self.upper_rchandle(ops, conn, byteflow, *args)