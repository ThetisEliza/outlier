'''
Date: 2023-03-08 23:10:22
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-03-14 18:06:36
FilePath: /outlier/src/outlier/tools/utils.py
'''
import logging
import hashlib
import random
import socket
from logging import handlers
from datetime import datetime

FORMAT = '%(asctime)s - %(message)s'



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
    

class RandomGen:
    @staticmethod
    def getrandomvalue():
        return hashlib.md5(str(random.randint(0, 1024) + datetime.now().timestamp()).encode()).hexdigest()