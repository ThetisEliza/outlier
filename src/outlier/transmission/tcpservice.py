
import socket
import select
from enum import Enum
from dataclasses import dataclass
from typing import Callable, Any, List, Tuple, Dict
from tools.threadpool import ThreadPool
from tools.decorators import onexit
from tools.aux import Ops

@dataclass
class Connection:
    sock: socket.socket
    addr: Any
    
    
class TcpService:
    """This service is to use epoll to provide a bi-direction
    tcp channel, we hope it can be general for both the server and
    the client
    """
    def __init__(self, conf, is_block: bool = False) -> None:
        self.sock = socket.socket()
        self.epctl = select.epoll()
        self.threadpool = ThreadPool()           
        self.is_block = is_block
        self.conf = conf
        self.loop = True
        self.upper_rchandle: Callable[[Ops, Connection, bytes, Any], Any] = lambda *args: ...
        self.conn = Connection(self.sock, None)

            
    def send(self, byteflow: bytes, conn: Connection = None):
        """Actively send message to connection

        Args:
            byteflow (bytes): data
            conn (Connection, optional): connection.
        """
        if conn:    
            conn.sock.send(byteflow)
            
        
    def set_upper_rchandle(self, upper_rchandle: Callable[[Ops, Connection, bytes, Any], Any]):
        """This is provided for upper service to invoke recall funcion.
        Invoked at the time when socket received buffer data.
        Args:
            upper_rchandle (Callable[[Ops, Connection, bytes, Any], Any]): The func to be invoked by upper layer.
        """
        self.upper_rchandle = upper_rchandle
    
    def _rchandle(self, ops: Ops, conn: Connection, fd:int = -1, byteflow: bytes = None, *args):
        pass 
        
    def _loop(self):
        pass
        
    def _startloop(self):
        if self.is_block:
            self._loop()
        else:
            self.threadpool.put_task(self._loop)
        
    @onexit
    def close(self, *args):
        print(f"[Tcp layer] close")
        self.loop = False
        self.epctl.close()
        self.threadpool.close()
        self.sock.close()
        
        
        
        
class TcpListenService(TcpService):
    """This service is a tcp listener used as a server
    """
    def __init__(self, conf, is_block: bool) -> None:
        super().__init__(conf, is_block)
        self.conns: Dict[int, Connection] = dict()
        
        
    def _rchandle(self, ops: Ops, conn: Connection, fd: int = -1, byteflow: bytes = None, *args):
        print(f"[Tcp layer] recall {ops}, {conn.addr}, {fd}, {len(byteflow) if byteflow else None}")
        if ops == Ops.Add:
            self.conns[fd] = conn
            self.epctl.register(conn.sock, select.EPOLLIN)
        elif ops == Ops.Rmv:
            try:
                conn = self.conns.get(fd)
                conn.sock.close()
            finally:
                del self.conns[fd]
            print(f"close {conn.addr}")    
                
        self.upper_rchandle(ops, conn, byteflow, *args)
    
    
    def _loop(self):
        ssock = self.sock
        ssock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        print(self.conf.ip, self.conf.port)
        ssock.bind((self.conf.ip, self.conf.port))
        ssock.listen(5)
        self.epctl = select.epoll()
        self.epctl.register(ssock, select.EPOLLIN)
    
        print("start listen")
        while self.loop:
            events = self.epctl.poll()
            for fd, _ in events:
                if fd == ssock.fileno():
                    sock, addr = ssock.accept()
                    self.threadpool.put_task(self._rchandle, args=(Ops.Add, Connection(sock, addr), sock.fileno()))
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
                        print(f"Conn fd {fd} not found, ignore")
    
    def startlistenloop(self):
        self._startloop()
        
        
    @onexit
    def close(self, *args):
        for fd in self.conns:
            self.conns.get(fd).sock.close()
        super().close()
        
        
class TcpConnectService(TcpService):
    """This service is a tcp listener used as a client
    """
    def __init__(self, conf, is_block: bool) -> None:
        super().__init__(conf, is_block)
        
        
    def startconnectloop(self):
        self._startloop()
    
    def _loop(self):
        self.sock.connect((self.conf.ip, self.conf.port))
        self.epctl.register(self.sock, select.EPOLLIN)       
        self.conn.addr = self.sock.getsockname()
        while self.loop:
            events = self.epctl.poll()
            for fd, _ in events:
                if fd == self.sock.fileno():
                    try:
                        byteflow = self.sock.recv(1024)
                        if len(byteflow) == 0:
                            raise ConnectionAbortedError()
                        self.threadpool.put_task(self._rchandle, args=(Ops.Rcv, self.conn, fd, byteflow))
                    except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError, ConnectionRefusedError):
                        print("server failed")
                        self.close()
                        

    def _rchandle(self, ops: Ops, conn: Connection, fd: int = -1, byteflow: bytes = None, *args):
        print(f"[Tcp layer] recall {ops}, {conn.addr}, {fd}, {len(byteflow) if byteflow else None}")
        self.upper_rchandle(ops, conn, byteflow, *args)