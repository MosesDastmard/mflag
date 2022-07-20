import os
from os.path import join
from .util import get_file_info
import time
import sys
import inspect


class SkipWithBlock(Exception):
    pass


class Flag:
    def __init__(self, flag_extention) -> None:
        self.flag_extention = flag_extention
        self.get_file_info = get_file_info

    def get_flag_path(self, file_path):
        file_info = self.get_file_info(file_path)
        flag_name = "." + file_info['file_name'] + "." + self.flag_extention + '.flg'
        flag_path = join(file_info['directory'], flag_name)
        return flag_path

    def check_flagged(self, file_path : str) -> bool:
        """validates if for a given file, the flag file exists, if so
        Args:
            file_path (str): file path
        Returns:
            bool: True if flag file for given file exists, otherwise False
        """        
        flag_path = self.get_flag_path(file_path)
        if os.path.exists(flag_path):
            return True
        else:
            return False

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
                os.remove(flag_path)
            else:
                raise Exception(f'mode has to be eigther "put" or "remove" (mode={mode} is not acceptable)')

    def put_flag(self, file_paths):
        self.__flag(file_paths=file_paths, mode='put')

    def remove_flag(self, file_paths):
        self.__flag(file_paths=file_paths, mode='remove')
        
        
    class MakeBusy:
        def __init__(self, path : str, max_attempts:int=100, check_interval:int=10, raise_error:bool=True):
            """In case several process has to access the same file or directory, and we have to avoid them all at once,
            this context manager will be used to check if the file or directory is busy with other processes or not, in case
            it's idle, it will make the file busy so that other processes can't access it. Use this in case of write action.
            It's not necessary for full read actions of the same file or directory.

            Args:
                path (str): path to file or directory
                max_attempts (int, optional): max number of tries till it find the file or directory idle. Defaults to 100.
                check_interval (int, optional): time between two busy checking tries. Defaults to 10.
                raise_error (bool, optional): the action if the file or directory not getting idle after max tries. Defaults to True.
                in case it's set to False, the code block in context manager will skip.
            """                
            self.path = path
            self.max_attempts = max_attempts
            self.check_interval = check_interval
            self.raise_error = raise_error
            
        def __enter__(self):
            self.flag = Flag('busy')
            attepmt = 1
            while True:
                if self.flag.check_flagged(self.path):
                    time.sleep(self.check_interval/1000)
                else:
                    self.flag.put_flag(self.path)
                    break
                attepmt += 1
                if attepmt >= self.max_attempts:
                    if self.raise_error:
                        raise Exception('Maximum attempt exceeded')
                    else:
                        # Do some magic
                        sys.settrace(lambda *args, **keys: None)
                        frame = sys._getframe(1)
                        frame.f_trace = self.trace
                        return None
                                    
        def trace(self, frame, event, arg):
            raise SkipWithBlock()
            

        def __exit__(self, type, value, traceback):
            if type is None:
                self.flag.remove_flag(self.path)
                return
            if issubclass(type, SkipWithBlock):
                return True
        