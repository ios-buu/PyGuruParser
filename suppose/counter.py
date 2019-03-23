# code=utf-8

import logging
import sys
import time

log_name = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler(f"{log_name} parser.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.INFO)

logger.addHandler(handler)
logger.addHandler(console)

def count_uri_layer(data_set):
    """
    从data_set中统计uri相关数据，
    :return: (总数,平均数量,最大层数,层数[1,2,3],每层对应的uri个数[10,10,10])
    """
    pass
def count_api(data_set):
    """
    从data_set中统计api相关数据，
    :return: (总数)
    """
    pass
def count_resource(data_set):
    """
    从data_set中统计资源相关数据，
    :return: (总数,资源数量[1,2,3],每个数量下对应资源的个数[10,10,10])
    """
    pass
