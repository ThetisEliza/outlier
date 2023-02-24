'''
Date: 2022-11-18 13:44:35
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2022-11-18 18:58:28
FilePath: /outlier/src/manager.py
'''
import json


class Config:
    """
    config class
    """    
    
    def __init__(self, **args):
        self.__dict__.update(args)
        try:
            with open(""+"config/config.json") as f:
                self.__dict__.update(json.load(f))
        except:
            ...
        
            


