
import logging
from logging import handlers

FORMAT = '%(asctime)s - %(message)s'

def init_logger(level, format=FORMAT, filehandlename=None):
    if filehandlename is not None:
        logging.basicConfig(format=format, level=eval("logging."+level), handlers=[handlers.RotatingFileHandler(filehandlename, maxBytes=5000000, backupCount=20)])
    else:
        logging.basicConfig(format=format, level=eval("logging."+level))
    
    