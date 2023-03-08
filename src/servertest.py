import logging
from argparse import ArgumentParser

from biz.server import Server
from encryption.sessionservice import ServerSessService
from transmission.tcpservice import TcpListenService

from outlier.tools.utils import gethostaddr, initlogger


def main():
    argparse = ArgumentParser(prog="Chat room", description="This is a chat room for your mates")
    argparse.add_argument("-l", "--log", default="INFO", type=str, choices=["DEBUG", "INFO", "ERROR", "debug", "info", "error"])
    argparse.add_argument("-lh", "--loghandler", default=None, type=str)
    argparse.add_argument("-i", "--ip",     required=False, type=str, default=gethostaddr())
    argparse.add_argument("-p", "--port",   required=False, type=int, default=8809)
        
    kwargs = vars(argparse.parse_args())
    initlogger(kwargs.get('log').upper(), filehandlename=kwargs.get('loghandler'))    

    # logger = logging.getLogger("Server")
    
    logging.info(f"Check init parameters {kwargs}")
    
    logging.info(f"Build tcp service")
    ts = TcpListenService(True, **kwargs)
    
    logging.info(f"Build Encryption service")
    ss = ServerSessService(ts, **kwargs)
    
    logging.info(f"Build server")
    bs = Server(ss, **kwargs)
    
    logging.info(f"Server start")
    bs.start()
    
if __name__ == '__main__':
    main()



