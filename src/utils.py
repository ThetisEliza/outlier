'''
Date: 2023-01-07 22:59:34
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-01-10 19:58:51
FilePath: /outlier/src/utils.py
'''
import logging
from logging import handlers

FORMAT = '%(asctime)s - %(message)s'

def init_logger(level, format=FORMAT, filehandlename=None):
    if filehandlename is not None:
        logging.basicConfig(format=format, level=eval("logging."+level), handlers=[handlers.RotatingFileHandler(filehandlename, maxBytes=500000, backupCount=20)])
    else:
        logging.basicConfig(format=format, level=eval("logging."+level))
    
    
def retry_process(tryrecall, tryargs, failrecall, failargs, uppertimes, *args):
    errortime = 0
    while True:
        try:
            if errortime > uppertimes:
                break
            tryrecall(*tryargs)
            errortime = 0
        except Exception as e:
            failrecall(*failargs)
            errortime += 1