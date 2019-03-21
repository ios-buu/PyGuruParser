# code-utf-8

from suppose import parser, scanner

import sys

import yaml
import logging
import MySQLdb
logger = logging.getLogger(__name__)
logger.setLevel(level = logging.INFO)
handler = logging.FileHandler("数据拆分.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.INFO)

logger.addHandler(handler)
logger.addHandler(console)
# sys.setrecursionlimit(50000)
file_paths = scanner.scan('/Users/canfuu/Documents/python/code/final_project/openapi-directory',
                          match_file_name='swagger.yaml')
file_paths = sorted(file_paths)
i = 0
for path in file_paths:
    i += 1
    logger.info(f"{i}\t开始读取{path}")
    text = ""
    try:
        with open(path, 'r', encoding='utf-8') as file:
            text = file.read()
            data = yaml.load(text)
            data['file_path'] = path
            parser.insert(data, host='localhost', username='root', password='root', database='api_swagger_source', build=True)
    except Exception as e:
        logger.error("执行错误 -> " + path)
        logger.error(e)
