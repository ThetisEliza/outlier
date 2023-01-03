'''
Date: 2023-01-03 14:58:05
LastEditors: Xiaofei wxf199601@gmail.com
LastEditTime: 2023-01-03 15:34:40
FilePath: /outlier/src/func.py
'''

'''
Functions Frame
'''

class FuncBase:
    def __init__(self,
        command: str,
                    
        **kwargs) -> None:
        
        self._cmd       = command
        self._retcmd    = command
        
        
    
    
    def _interact(self):
        ...
        
    def _clientsend(self):
        ...
        
    def _clientrecv(self):
        ...
        
    def _serverresponse(self):
        ...
        
    def _serverrecv(self):
        ...