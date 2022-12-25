'''
Date: 2022-11-18 13:44:35
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2022-11-18 18:58:28
FilePath: /outlier/src/manager.py
'''
import json

PROJ_PATH = ""

class Config:
    """
    config class
    """    
    def __init__(self, **args):
        with open(PROJ_PATH+"config/config.json") as f:
            self.__dict__.update(json.load(f))
            self.__dict__.update(args)
            


