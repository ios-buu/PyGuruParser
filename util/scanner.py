# code-utf-8
import os


def scan(path, match_file_name=None):
    file_list = set([])
    if not os.path.isdir(path):
        if match_file_name is None or path == match_file_name:
            file_list.add(path)
    else:
        for file_name in os.listdir(path):
            if not os.path.isdir(path + "/" + file_name):
                if match_file_name is None or file_name == match_file_name:
                    file_list.add(path + "/" + file_name)
            else:
                file_list = scan(path + "/" + file_name,match_file_name) | file_list
    return file_list
