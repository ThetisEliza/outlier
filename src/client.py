'''
Date: 2022-11-16 16:59:28
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-01-10 18:07:52
FilePath: /outlier/src/client.py
'''

from argparse import ArgumentParser    
import utils
from manager import Config

          

       
        
def main():
    argparse = ArgumentParser(prog="Chat room", description="This is a chat room for your mates")
    argparse.add_argument("-l", "--log", default="INFO", type=str, choices=["DEBUG", "INFO", "ERROR", "debug", "info", "error"])
    argparse.add_argument("-n", "--name", required=True, type=str)
    args = argparse.parse_args()
    
    conf = Config(**{"log": args.log, "username": args.name})
    utils.init_logger(conf.log.upper())
    
    from _client import Client  
    Client(conf)
    
    

    
if __name__ == '__main__':
    main()