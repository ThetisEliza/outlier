'''
Date: 2022-11-16 16:49:18
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2022-11-18 18:47:27
FilePath: /outlier/src/server.py

I found `python` is really hard to write a project. It's too flexiable to organize the structure ...
'''

from manager import Config, ServerManager


conf = Config()

def main():
    sm = ServerManager(conf)
    sm.start()
    

if __name__ == '__main__':
    main()
    
    