from argparse import ArgumentParser

from .tools.utils import gethostaddr, RandomGen
from .server import start_server
from .client import start_client

def main():
    argparse = ArgumentParser(prog="python -m outlier", description="This is a chat room for your mates", add_help=False)
    argparse.add_argument("-l", "--log", default="INFO", type=str, choices=["DEBUG", "INFO", "ERROR", "debug", "info", "error"])
    argparse.add_argument("-lh", "--loghandler", default=None, type=str)
    argparse.add_argument("-i", "--ip",     required=False, type=str, default=gethostaddr())
    argparse.add_argument("-p", "--port",   required=False, type=int, default=8809)
    argparse.add_argument("-n", "--name",   required=False, type=str)
    argparse.add_argument("-s", "--server", action="store_true")
    
    
    clientargparse = ArgumentParser(prog="python -m outlier", parents=[argparse], conflict_handler="resolve", usage="python3 -m outlier")
    clientargparse.add_argument("-i", "--ip",     required=True, type=str)
    clientargparse.add_argument("-n", "--name",   required=True, type=str)
    clientargparse.add_argument("-k", "--key",    required=False, type=str, default=RandomGen.getrandomvalue()[:6])
    
    kwargs = vars(argparse.parse_args())
    if kwargs.get('server'):
        start_server(**kwargs)
    else:
        kwargs = vars(clientargparse.parse_args())
        start_client(**kwargs)
    

if __name__ == '__main__':
    main()