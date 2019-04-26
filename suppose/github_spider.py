# code=utf-8
import parser
import yaml
import json
from pydriller import RepositoryMining
import logging
import time


log_name = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler(f"{log_name} github_spider.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.INFO)

logger.addHandler(handler)
logger.addHandler(console)

def crawl(folder_path, host, username, password, database,start_commit_hash = None):
    mine = RepositoryMining(folder_path)
    i=0
    start = start_commit_hash is None
    for commit in mine.traverse_commits():
        if not start and start_commit_hash == commit.hash:
            start = True
        for mod in commit.modifications:
            if mod.filename == 'swagger.yaml' or mod.filename == 'swagger.json':
                i += 1
                if start:
                    try:
                        schema = mod.filename.split(".")[1]
                        text = mod.source_code
                        if schema=='yaml':
                            data = yaml.load(text)
                        elif schema=='json':
                            data = json.loads(text)
                        data['file_path'] = mod.new_path
                        data['old_path'] = mod.old_path
                        data['new_path'] = mod.new_path
                        data['update_time'] = str(commit.committer_date)
                        data['hash'] = commit.hash
                        logger.info(f'[{data["hash"]}] [{i}]开始...')
                        parser.insert(data, host, username, password, database, build=True,only_insert=True,allow_update=False)
                    except Exception as e:
                        logger.error(f"[{commit.hash}]执行错误 -> {mod.new_path}")
                        logger.error(e)
                else:
                    logger.info(f'[{commit.hash}] [{i}]跳过...')
crawl('/Users/canfuu/Documents/github/openapi-directory/openapi-directory','www.canfuu.com','canfuu','Cts1997..','api_version',start_commit_hash='a5afb0c211cf420599456e3e7d8a82ad1c0c419e')
