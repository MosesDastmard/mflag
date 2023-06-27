from argparse import ArgumentParser
from . import run as runserver
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("port", type=int, help="bind port")
    args = parser.parse_args()
    port = args.port
    runserver(port)