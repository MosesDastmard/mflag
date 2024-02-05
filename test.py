from mflag import JobManager, LockManager
import time
from joblib import Parallel, delayed

path_to_sqlite = "lock.sqlite"

lockManager = LockManager(path_to_sqlite)


@lockManager.lock(job_id="job1", prc_id="test", timeout=10)
def job1():
    print("job1 started")
    time.sleep(30)
    print("job1 finished")


@lockManager.lock(job_id="job2", prc_id="test", timeout=10)
def job2():
    print("job2 started")
    time.sleep(10)
    print("job2 finished")


@lockManager.lock(job_id="job3", prc_id="test", timeout=10)
def job3():
    print("job3 started")
    time.sleep(5)
    print("job3 finished")


@lockManager.lock(job_id="job", prc_id="test1", timeout=10)
def job1():
    print("job1 started")
    time.sleep(30)
    print("job1 finished")


@lockManager.lock(job_id="job", prc_id="test2", timeout=10)
def job2():
    print("job2 started")
    time.sleep(10)
    print("job2 finished")


@lockManager.lock(job_id="job", prc_id="test3", timeout=10)
def job3():
    print("job3 started")
    time.sleep(5)
    print("job3 finished")


Parallel(n_jobs=-1)(delayed(job)() for job in [job1, job2, job3])
