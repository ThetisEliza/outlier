'''
Date: 2023-03-08 23:10:22
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-03-09 11:46:53
FilePath: /outlier/src/outlier/tools/utils.py
'''
import logging
from logging import handlers
import socket
import sys

FORMAT = '%(asctime)s - %(message)s'

def singleton(clazz):
    clazz.ins = None
    clazz.inited = False
    clazz.origin_init = clazz.__init__
    
    def wrappednew(cls, *args, **kwargs):
        if clazz.ins is None:
            # print(f"created cls {cls}")
            clazz.ins = super(clazz, cls).__new__(cls)
        return clazz.ins
    
    def wrappedinit(self, *args, **kwargs):
        if not clazz.inited:
            # print(f"init cls {self}")
            clazz.origin_init(self, *args, **kwargs)
            clazz.inited = True
            
    
    clazz.__new__ = wrappednew
    clazz.__init__ = wrappedinit
    return clazz


def initlogger(level, format=FORMAT, filehandlename=None):
    """To init log with certain level and format,
    or designate a filename for rotating file log
    handler

    Args:
        level (_type_): level
        format (_type_, optional): _description_. Defaults to FORMAT as `%(asctime)s - %(message)s`.
        filehandlename (_type_, optional): _description_. Defaults to None.
    """
    
    if filehandlename is not None:
        logging.basicConfig(format=format, level=eval("logging."+level), handlers=[handlers.RotatingFileHandler(filehandlename, maxBytes=500000, backupCount=20)])
    else:
        logging.basicConfig(format=format, level=eval("logging."+level))
    
    
 
def gethostaddr() -> str:
    """This function is to check the ipaddress that a host should be bind

    Returns:
        str: ip address
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()
        return ip[0]