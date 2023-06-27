from pathlib import Path
import os
import sys
from os.path import join
from mpath import get_path_info
from datetime import datetime
import json
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
    def __init__(self, job_dir_path, job_id, job_name="", job_description="", process_name=""):
        self.job_dir_path = Path(job_dir_path)
        self.job_id = job_id
        self.job_name = job_name
        self.job_description = job_description
        self.process_name = process_name
        self.job_file_path = os.path.join(self.job_dir_path, self.job_id + ".json")
        
    def __initial_check(self):
        os.makedirs(self.job_dir_path, exist_ok=True)
    
    def __is_job_done(self):
        if not os.path.exists(self.job_file_path):
            job_dict = {'job_id':self.job_id, 'job_name':self.job_name, 'job_description':self.job_description, 'process_name':self.process_name, 'issue_date':str(datetime.now())}
            with open(self.job_file_path, 'w') as f:
                json.dump(job_dict, f)
            return False
        else:
            with open(self.job_file_path, 'r') as f:
                job_dict = json.load(f)
                if 'finish_date' in job_dict.keys():
                    print(f"job_id={self.job_id} is already done, no need to run it again")
                    return True
            return False

    def __enter__(self):
        self.__initial_check()
        if self.__is_job_done():
            sys.settrace(lambda *args, **keys: None)
            frame = sys._getframe(1)
            frame.f_trace = self.trace

    def trace(self, frame, event, arg):
        raise SkipWithBlock()
    
    def __finish_job(self):
        with open(self.job_file_path, 'r') as f:
            job_dict = json.load(f)
            job_dict['finish_date'] = str(datetime.now())
        with open(self.job_file_path, 'w') as f:
            json.dump(job_dict, f)
        
    def __exit__(self, type, value, traceback):
        if type is None:
            self.__finish_job()
            return  # No exception

        if issubclass(type, SkipWithBlock):
            return True
