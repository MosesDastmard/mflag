from . import Submit, Client
from joblib import Parallel, delayed
import time

client = Client(8889)
submit = Submit(client)

if __name__ == '__main__':
    @submit(cpu=10, mem=10, timeout=5)
    def f(x):
        time.sleep(1)
        print(x)
        return x
        
    print(f("single test passed"))
    
    for i in range(5):
        f(i)
        
    results = Parallel(n_jobs=64)(delayed(f)(i) for i in range(256))
    print(results)
