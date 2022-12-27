
import logging
import sys

FORMAT = '%(asctime)s - %(message)s'

def init_logger(level, format=FORMAT):
    logging.basicConfig(format=format, level=eval("logging."+level))