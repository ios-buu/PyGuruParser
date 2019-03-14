# code-utf-8

from suppose import parser, scanner

import sys

import yaml

import MySQLdb
sys.setrecursionlimit(2000)

file_paths = scanner.scan('/Users/canfuu/Documents/python/code/final_project/openapi-directory',
                          match_file_name='swagger.yaml')
i = 0
for path in file_paths:
    i += 1
    if i % 50 == 0:
        print(i)
    text = ""
    with open(path, 'r', encoding='utf-8') as file:
        text = file.read()
    try:
        data = yaml.load(text)
        data['file_path'] = path

        parser.insert(data, host='localhost', username='root', password='root', database='api_swagger_source', build=True)
    except Exception as e:
        print("执行错误 -> " + path)
        print(e)