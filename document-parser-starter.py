# code-utf-8

from suppose import parser, scanner
import yaml
import logging
import time
a_parser = argparse.ArgumentParser(description="p18004 server example")
a_parser.add_argument('--host')
a_parser.add_argument('--username')
a_parser.add_argument('--password')
a_parser.add_argument('--database')
args = a_parser.parse_args()

log_name = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
logger = logging.getLogger(__name__)
logger.setLevel(level = logging.INFO)
handler = logging.FileHandler(f"{log_name} handler.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.INFO)

logger.addHandler(handler)
logger.addHandler(console)

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
            parser.insert(data, args.host,args.username,args.password,args.database, build=True)
    except Exception as e:
        logger.error("执行错误 -> " + path)
        logger.error(e)
