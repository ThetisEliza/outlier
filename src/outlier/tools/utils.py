import logging
from logging import handlers
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