
import logging
from argparse import ArgumentParser

from biz.bizservice import Client
from encryption.sessionservice import ConnectSessService
from transmission.tcpservice import TcpConnectService

from outlier.tools.utils import initlogger


def main():
    argparse = ArgumentParser(prog="Chat room", description="This is a chat room for your mates")
    argparse.add_argument("-l", "--log", default="INFO", type=str, choices=["DEBUG", "INFO", "ERROR", "debug", "info", "error"])
    argparse.add_argument("-n", "--name", required=True, type=str)
    argparse.add_argument("-i", "--ip",   required=True, type=str)
    argparse.add_argument("-p", "--port", required=False, type=int, default=8809)
        
    kwargs = vars(argparse.parse_args())
    initlogger(kwargs.get('log').upper(), filehandlename=kwargs.get('loghandler'))    
    
    ts = TcpConnectService(False, **kwargs)
    ss = ConnectSessService(ts, **kwargs)
    bs = Client(ss, **kwargs)
    bs.start()  

    
if __name__ == '__main__':
    main()
