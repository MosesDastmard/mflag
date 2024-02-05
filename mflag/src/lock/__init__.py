from pathlib import Path
import sqlite3
import os
from datetime import datetime, timedelta
import time


def lock(sqlite_path: str, job_id: str, prc_id: str, timeout: int):
    # if job_id and prc_id are in sqllite, we update the expiration time and return 0
    # if job_id and prc_id are not in sqllite, we insert them and set expiration time based on timeout and return 0
    # if job_id exists, but prc_id is different, we return (expiration - now)
    # query the get the row where job_id = job_id
    connection = sqlite3.connect(sqlite_path)
    connection.execute(
        "CREATE TABLE IF NOT EXISTS locks (job_id TEXT PRIMARY KEY, prc_id TEXT, expiration DATETIME)"
    )
    connection.commit()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM locks WHERE job_id = ?", (job_id,))
    rows = cursor.fetchall()
    if len(rows) == 0:
        expiration = datetime.now() + timedelta(seconds=timeout)
        cursor.execute(
            "INSERT INTO locks (job_id, prc_id, expiration) VALUES (?, ?, ?)",
            (job_id, prc_id, expiration),
        )
        connection.commit()
        print(f"lock {job_id} acquired by {prc_id}")
        return 0
    else:
        if rows[0][1] == prc_id:
            expiration = datetime.now() + timedelta(seconds=timeout)
            cursor.execute(
                "UPDATE locks SET expiration = ? WHERE job_id = ? AND prc_id = ?",
                (expiration, job_id, prc_id),
            )
            connection.commit()
            print(f"lock {job_id} reacquired by {prc_id}")
            return 0
        else:
            datetime_ = datetime.fromisoformat(rows[0][2])
            waiting_time = (datetime_ - datetime.now()).seconds
            if waiting_time < 0:
                unlock(sqlite_path, job_id, rows[0][1])
                return lock(sqlite_path, job_id, prc_id, timeout)
            print(
                f"{prc_id}: {job_id} is locked by {rows[0][1]} for {waiting_time} seconds"
            )
            return waiting_time


def unlock(sqlite_path: str, job_id: str, prc_id: str):
    connection = sqlite3.connect(sqlite_path)
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM locks WHERE job_id = ? AND prc_id = ?", (job_id, prc_id)
    )
    connection.commit()
    print(f"lock {job_id} released by {prc_id}")
    return 0


class LockManager:
    def __init__(self, path_to_sqlite: str):
        self.path_to_sqlite = path_to_sqlite
        Path(path_to_sqlite).parent.mkdir(parents=True, exist_ok=True)

    def lock(self, job_id: str, prc_id: str, timeout: int):
        def decorator(func):
            def wrapper(*args, **kwargs):
                while True:
                    waiting_time = lock(self.path_to_sqlite, job_id, prc_id, timeout)
                    if waiting_time == 0:
                        break
                    else:
                        print(f"waiting for {waiting_time} seconds")
                        time.sleep(waiting_time)
                result = func(*args, **kwargs)
                unlock(self.path_to_sqlite, job_id, prc_id)
                return result

            return wrapper

        return decorator
