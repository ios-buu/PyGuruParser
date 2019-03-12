# code-utf-8

from util import parser, scanner

import sys

import yaml

sys.setrecursionlimit(2000)

file_paths = scanner.scan('/Users/canfuu/Documents/python/code/final_project/openapi-directory',
                          match_file_name='swagger.yaml')
for path in file_paths:
    text = ""
    with open(path, 'r', encoding='utf-8') as file:
        text = file.read()
    try:
        data = yaml.load(text)
        parser.insert(data, 'localhost', 'root', 'root', 'api_swagger_source')
    except Exception as e:
        print("不符合yaml语法规则，文件内容格式错误" + path)
        print(e)
