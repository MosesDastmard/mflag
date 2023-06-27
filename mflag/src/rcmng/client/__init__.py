import socket
import json
import warnings

# Create a socket object
class Worker:
    def __init__(self, port):
        self.port = port
        self.client_socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the server
        self.client_socket_.connect(('127.0.0.1', self.port))
        
    def request(self, data):
        send_data = json.dumps(data)
        self.client_socket_.sendall(send_data.encode('utf-8'))
        self.response = self.recv()
        return self
        
    def recv(self):
        try:
            response = self.client_socket_.recv(1024).decode('utf-8')
            response_data = json.loads(response)
            if response_data is None:
                response_data = {'status': 'rejected'}
        except Exception as e:
            response_data = {'status': 'rejected'}
        return response_data
    
    def close(self):
        self.client_socket_.close()

# Create a socket object
class FakeWorker:
    def __init__(self, port):
        self.port = port
        
    def request(self, data):
        self.response = {'status': 'accepted', 'id': 0}
        return self
        
    def recv(self):
        return {'status': 'accepted', 'id': 0}
    
    def close(self):
        pass
        
# Create a socket object
class Client:
    def __init__(self, port):
        self.port = port
    
    def get(self):
        try:
            worker = Worker(self.port)
        except Exception as e:
            worker = FakeWorker(self.port)
            warnings.warn("server is not running or port is not open, use fake worker instead")
        return worker
