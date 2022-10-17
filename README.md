# flagify: powerful Python toolkit for mark/unmark files and directories 
[![PyPI Latest Release](https://img.shields.io/pypi/v/pandas.svg)](https://pypi.org/project/flagify/)

## What is it?

**flagify** is a Python package that provides marking/unmarking files and directores. For years, dealing with processing files, we understood that we need to put flag for files/directories that are already processed. This package provides the ability to mark files/directories and avoid any unnecessary repeatitive processing of same files/directories.
It also can manage serveral processes that willing to write on/in same files/directories. For example, we want to write to a parquet file, the whole processing generate part of the parquet file managed by a separate parallel processes. Using **flagify** avoid writing errors that happen at same time.

## Where to get it
The source code is currently hosted on GitHub at:
https://github.com/MosesDastmard/flagify

Binary installers for the latest released version are available at the [Python
Package Index (PyPI)](https://pypi.org/project/flagify/)


```python
# !pip install flagify
from flagify import Flag, FlagPath
import pandas as pd
import os
```


```python
# lets make a simple csv file
data = {'name':['flagify', 'pandas', 'numpy'],
        'toolkit':['marking', 'data analysis', 'data computing']}

pd.DataFrame(data).to_csv('data.csv', index=False)

class Process(Flag):
    def __init__(self, process_name):
        self.process_name = process_name
        Flag.__init__(self, process_name)
        
    def run(self, csv_path, parquet_path):
        if not self.isFlagged(csv_path):
            pd.read_csv(csv_path).to_parquet(parquet_path)
            self.putFlag(csv_path)
        else:
            print(f"the file {csv_path} is already processed")
```


```python
Process(process_name='convert_csv_to_parquet').run('data.csv', 'data.parquet')
```


```python
Process(process_name='convert_csv_to_parquet').run('data.csv', 'data.parquet')
```

    the file data.csv is already processed



```python
with FlagPath("data.csv", "contextmanagertest"):
    if os.path.exists("data.csv"):
        print("file exists")
    else:
        print("file does not exist")
```

    file exists



```python
with FlagPath("data.csv", "contextmanagertest"):
    if os.path.exists("data.csv"):
        print("file exists")
    else:
        print("file does not exist")
```
