from pathlib import Path
import os
import sys
from os.path import join
import pandas as pd
from mpath import get_path_info
from datetime import datetime
flag_extention = '.flg'

class Flag:
    def __init__(self, process_name, hidden=True) -> None:
        self.process_name = process_name
        self.hidden = hidden
        self.get_path_info = get_path_info

    def get_flag_path(self, file_path):
        file_info = self.get_path_info(file_path)
        if self.hidden:
            flag_name = "." + file_info.name + "." + self.process_name + flag_extention
        else:
            flag_name = file_info.name + "." + self.process_name + flag_extention
        flag_path = join(file_info.directory, flag_name)
        return flag_path

    def isFlagged(self, file_paths : str) -> bool:
        """validates if for a given file, the flag file exists, if so
        Args:
            file_path (str): file path
        Returns:
            bool: True if flag file for given file exists, otherwise False
        """
        if type(file_paths) == str:
             file_paths = [file_paths]
        if type(file_paths) != list:
            raise Exception('file_paths should be a string path or list of string paths')
        for file_path in file_paths:   
            flag_path = self.get_flag_path(file_path)
            if not os.path.exists(flag_path):
                return False
        return True

    def __flag(self, file_paths: list, mode):
        """it drops flag file along the given files that their full path provided
        Args:
            file_paths (list): list of files path, if an string provided, it converts to a list of single path
        Raises:
            Exception: if file path is not valid
        """        

        if type(file_paths) == str:
             file_paths = [file_paths]
        if type(file_paths) != list:
            raise Exception('file_paths should be a string path or list of string paths')
        for file_path in file_paths:
            flag_path = self.get_flag_path(file_path)
            if mode == 'put':
                open(flag_path, 'w').close()
            elif mode == 'remove':
                if os.path.exists(flag_path):
                    os.remove(flag_path)
            else:
                raise Exception(f'mode has to be eigther "put" or "remove" (mode={mode} is not acceptable)')

    def putFlag(self, file_paths):
        self.__flag(file_paths=file_paths, mode='put')

    def removeFlag(self, file_paths):
        self.__flag(file_paths=file_paths, mode='remove')
        
        
class SkipWithBlock(Exception):
    pass


class JobManager:
    def __init__(self, job_file_path, job_id, job_name="", job_description="", process_name=""):
        self.job_file_path = Path(job_file_path)
        assert not os.path.isdir(self.job_file_path), f"job_file_path={self.job_file_path} is not a valid file path"
        self.job_id = job_id
        self.job_name = job_name
        self.job_description = job_description
        self.process_name = process_name
        self.job_file_dir = self.job_file_path.parent.absolute()
        
    def __initial_check(self):
        os.makedirs(self.job_file_dir, exist_ok=True)
        if not os.path.exists(self.job_file_path):
            self.__create_empty_job_file()
    
    def __create_empty_job_file(self):
        job_df = pd.DataFrame(columns=['job_id', 'job_name', 'job_description', 'process_name', 'issue_date', 'finish_date'])
        job_df.set_index('job_id', inplace=True)
        job_df.to_csv(self.job_file_path)
    
    def __is_job_done(self):
        job_df = pd.read_csv(self.job_file_path, index_col=0)
        if self.job_id not in job_df.index:
            for col, value in {'job_name':self.job_name, 'job_description':self.job_description, 'process_name':self.process_name, 'issue_date':datetime.now(), 'finish_date':None}.items():
                job_df.loc[self.job_id, col] = value
            job_df.to_csv(self.job_file_path)
            return True
        job_row = job_df.loc[self.job_id]
        if pd.isna(job_row['finish_date']):
            return True
        else:
            print(f"job_id={self.job_id} is already done, no need to run it again")
            return False

    def __enter__(self):
        self.__initial_check()
        if not self.__is_job_done():
            sys.settrace(lambda *args, **keys: None)
            frame = sys._getframe(1)
            frame.f_trace = self.trace

    def trace(self, frame, event, arg):
        raise SkipWithBlock()
    
    def __finish_job(self):
        job_df = pd.read_csv(self.job_file_path, index_col=0)
        job_df.loc[self.job_id, 'finish_date'] = datetime.now()
        job_df.to_csv(self.job_file_path)
        
    def __exit__(self, type, value, traceback):
        if type is None:
            self.__finish_job()
            return  # No exception

        if issubclass(type, SkipWithBlock):
            return True
