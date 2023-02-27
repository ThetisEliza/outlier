'''
Date: 2023-01-07 22:59:34
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-01-10 19:58:51
FilePath: /outlier/src/utils.py
'''
import logging
import time
import socket
from logging import handlers
from typing import Callable, Any
FORMAT = '%(asctime)s - %(message)s'

def init_logger(level, format=FORMAT, filehandlename=None):
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
    


            
def retry_process(
        func: Callable[[Any], int], 
        args,
        failedfunc: Callable[[Exception, Any], int], 
        failedargs, 
        uppertimers:int
    ) -> None:
    
    errortime = 0
    while True:
        try:
            if errortime >= uppertimers or func(*args) == -1:
                break
            errortime = 0
        except Exception as e:
            errortime += 1  
            failedfunc(e, *failedargs)
            time.sleep(0.1)
            

        
    

def getConnectAddr() -> str:
    """This function is to check the ipaddress that a host should be bind

    Returns:
        str: ip address
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()
        return ip[0]




class A:
    ins = None
    def __new__(cls: 'A') -> 'A':
        if A.ins is None:
            A.ins =  super().__new__(cls)
        return A.ins    
