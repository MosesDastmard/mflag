from argparse import ArgumentParser
from . import Client
import json

if __name__ == "__main__":
    # Send data to the server
    parser = ArgumentParser()
    parser.add_argument("port", type=int, help="bind port")
    args = parser.parse_args()
    port = args.port
    client = Client(port)
    data = {'cpu':20, 'mem': 10, 'timeout':10, 'method': 'attach'}
    client.request(data)
    print('Server response:', client.response)