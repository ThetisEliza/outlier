
import socket
import select
import time
from enum import Enum
from dataclasses import dataclass
from typing import Callable, Any, List, Tuple, Dict
from tools.threadpool import ThreadPool
from tools.decorators import onexit


@dataclass
class Connection:
    sock: socket.socket
    addr: Any

class Ops(Enum):
    Add = 0
    Rmv = 1
    Rcv = 2
    

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
        self.upper_rchandle: Callable[[Ops, Connection, bytes, Any], Any] = None
            
    def send(self, msg: bytes, conn: Connection = None):
        ...
        
    def get_all_conns(self) -> List[Connection]:
        return list()
        
    def set_upper_rchandle(self, upper_rchandle: Callable[[Ops, Connection, bytes, Any], Any]):
        self.upper_rchandle = upper_rchandle
    
    def _rchandle(self, ops: Ops, conn: Connection, fd:int = -1, msg: bytes = None, *args):
        ...
        
        
    def _loop(self):
        ...
        
    def _startloop(self):
        if self.is_block:
            self._loop()
        else:
            self.threadpool.put_task(self._loop)
        
    @onexit
    def close(self, *args):
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
        
        
    def _rchandle(self, ops: Ops, conn: Connection, fd: int = -1, msg: bytes = None, *args):
        if ops == Ops.Add:
            self.conns[fd] = conn
            self.epctl.register(conn.sock, select.EPOLLIN)
        elif ops == Ops.Rmv:
            try:
                conn = self.conns.get(fd)
                conn.sock.close()
            finally:
                del self.conns[fd]
            print(f"close {conn}")    
        elif ops == Ops.Rcv:
            ...
        if self.upper_rchandle is not None:
            self.upper_rchandle(ops, conn, msg, *args)
    
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
                        msg = conn.sock.recv(1024)
                        if len(msg) == 0:
                            raise ConnectionAbortedError()
                        self.threadpool.put_task(self._rchandle, args=(Ops.Rcv, conn, fd, msg))
                    except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError, ConnectionRefusedError):
                        self._rchandle(Ops.Rmv, conn, fd)
                    except KeyError:
                        print(f"Conn fd {fd} not found, ignore")
    
    def startlistenloop(self):
        self._startloop()
        
    def send(self, msg: bytes, conn: Connection = None):
        if conn:
            conn.sock.send(msg)
            
    def get_all_conns(self) -> List[Connection]:
        return list(self.conns.values())
                        
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
        
    
    def _loop(self):
        # if self.__reconnect(self.conf.ip, self.conf.port, retry_time=30) < 0:
        #     return
        self.sock.connect((self.conf.ip, self.conf.port))
        self.conn = Connection(self.sock, None)
        self.epctl.register(self.sock, select.EPOLLIN)            
        while self.loop:
            events = self.epctl.poll()
            for fd, _ in events:
                if fd == self.sock.fileno():
                    try:
                        msg = self.sock.recv(1024)
                        if len(msg) == 0:
                            raise ConnectionAbortedError()
                        self.threadpool.put_task(self._rchandle, args=(Ops.Rcv, self.conn, fd, msg))
                    except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError, ConnectionRefusedError):
                        print("server failed")
                        self.close()
                        # self.suspend()
        # self.startconnectloop()
                        
        # if self.__reconnect(self.conf.ip, self.conf.port, retry_time=30) < 0:
    

    def _rchandle(self, ops: Ops, conn: Connection, fd: int = -1, msg: bytes = None, *args):
        
        if ops == Ops.Rcv:
            print(msg)
        if self.upper_rchandle is not None:
            self.upper_rchandle(ops, conn, msg, *args)

    def __reconnect(self, ip:str, port:int, retry_time=None):
        import time
        retry = 1 if retry_time is None else retry_time
        for i in range(retry):
            try:
                time.sleep(1)
                self.sock = socket.socket()
                self.sock.connect((ip, port))
                self.conn = Connection(self.sock, None)
                print('reconncting succeed')
                return 1
            except:
                print(f'reconncting failed for {i}/{retry}')
        print('reconnction failed')
        return -1
    
    def suspend(self):
        self.sock.close()
        self.threadpool.close()
        self.loop = False
    
    def startconnectloop(self):
        self._startloop()
        
    def send(self, msg: bytes, conn: Connection = None):
        self.sock.send(msg)


