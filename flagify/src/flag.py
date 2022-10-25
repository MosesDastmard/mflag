import os
import sys
from os.path import join

from mpath import get_path_info

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


class JobManager(Flag):
    def __init__(self, job_dir, job_id):
        self.job_dir = job_dir
        print(self.job_dir)
        self.job_file_path = os.path.join(self.job_dir, 'job')
        os.makedirs(self.job_dir, exist_ok=True)
        Flag.__init__(self, job_id)
        
    def __enter__(self):
        if self.isFlagged(self.job_file_path):
            sys.settrace(lambda *args, **keys: None)
            frame = sys._getframe(1)
            frame.f_trace = self.trace

    def trace(self, frame, event, arg):
        raise SkipWithBlock()

    def __exit__(self, type, value, traceback):
        if type is None:
            self.putFlag(self.job_file_path)
            return  # No exception
        if issubclass(type, SkipWithBlock):
            return True  # Suppress special SkipWithBlock exception

