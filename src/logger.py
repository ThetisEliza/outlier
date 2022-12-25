import logging

class Log:
    def __init__(self) -> None:
        pass
    
    def info(self):
        ...
        
    def debug(self):
        ...
        
    def error(self):
        ...

logging.basicConfig(format=FORMAT, level=eval("logging."+conf.log.upper()))
logging.debug(f"{sys._getframe()} start")
    


        
    