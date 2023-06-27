import time
from ..client import Client
from copy import copy

def Submit(client):
    def submit(cpu, mem, timeout, sleep=0.1):
        def wrapper(func):
            def inner_wrapper(*args, **kwargs):
                client_ = client.get()
                data = {'cpu':cpu, 'mem':mem, 'timeout':timeout, 'method': 'attach'}
                sleep_ = sleep
                while client_.request(data).response['status'] != 'accepted':
                    time.sleep(sleep_)
                output = func(*args, **kwargs)
                id_ = client_.response['id']
                data = {'id':id_, 'method': 'dettach'}
                client_.request(data)
                client_.close()
                return output
            return inner_wrapper
        return wrapper
    return submit
                
            
            
    