import ntpath
import os


def get_file_info(file_path : str) -> dict:
    """it takes a file path and returns information about the file like:
    'directory': the directory path where the file resides
    'base_file_name': the file name without extentation example.zip -> example
    'flag_name' : 'base_file_name' + .flg
    'flag_path' : 'directory' + 'flag_name'
    Args:
        file_path (str): path to a file
    Returns:
        dict: file info in dictoinary format
    """        
    directory = os.path.dirname(file_path)
    file_name = ntpath.basename(file_path)
    base_file_name, extention = os.path.splitext(file_name)
    return {'directory':directory,
            'base_file_name':base_file_name,
            'file_name':file_name,
            'extention':extention}