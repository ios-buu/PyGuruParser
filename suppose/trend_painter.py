# code=utf-8
import matplotlib as mpl

mpl.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.graphics.tsaplots import acf, pacf, plot_acf, plot_pacf
from statsmodels.tsa.arima_model import ARMA
from suppose.parser import Method, Info, Request, Response, Uri
from suppose import parser
from suppose import trend_counter

import logging
import sys
import time
from suppose import scanner
import yaml

log_name = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
# handler = logging.FileHandler(f"{log_name} parser.log")
# handler.setLevel(logging.WARN)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.INFO)

# logger.addHandler(handler)
logger.addHandler(console)


def uri_layer():
    limit = 80000
    m = {}
    x = []
    y = []
    api_total = []
    session = parser.init_session('localhost', 'root', 'root', 'api_version')
    logger.info('开始')
    sql = "SELECT id FROM info group by new_path having count(id) >= 12"
    result = session.execute(sql)
    be_regular_api_id_list = []
    for result_data in result:
        be_regular_api_id_list.append(result_data[0])
    logger.info(f'预计统计{len(be_regular_api_id_list)}篇文档，共计{int((session.query(Uri).count() / limit) + 1)}页')
    for page_index in range(1, int((session.query(Uri).count() / limit) + 1)):
        logger.info(f'[{page_index}]开始处理第{page_index}页')
        temp_uri_total = 0
        temp_api_total = 0
        for uri in session.query(Uri).order_by(Uri.update_time.asc()).limit(limit).offset((page_index - 1) * limit):
            if uri.info_id in be_regular_api_id_list:
                if uri.update_time not in m:
                    m[uri.update_time] = [0, 0]
                url = str(uri.uri).replace('"', '')
                if len(url) > 1 and url != '/':
                    m[uri.update_time][0] = m[uri.update_time][0] + len(url.split('/'))
                m[uri.update_time][1] = m[uri.update_time][1] + 1
                temp_uri_total = temp_uri_total + 1
                if uri.info_id not in api_total:
                    api_total.append(uri.info_id)
                    temp_api_total = temp_api_total + 1
        logger.info(f'本次统计api{temp_api_total}个，uri{temp_uri_total}个')
    for update_time in m:
        x.append(update_time)
        if m[update_time][0] == 0:
            y.append(0)
        else:
            y.append(m[update_time][0] / m[update_time][1])
    trend_counter.auto(x, y, "The Trend of the average of Uri's Layer")


def api_resource():
    limit = 80000
    x = []
    y = []
    m = {}
    api_set = set()
    session = parser.init_session('localhost', 'root', 'root', 'api_version')
    logger.info('开始')
    sql = "SELECT id FROM info group by new_path having count(id) >= 12"
    result = session.execute(sql)
    be_regular_api_id_list = []
    for result_data in result:
        be_regular_api_id_list.append(result_data[0])
    logger.info(f'预计统计{len(be_regular_api_id_list)}篇文档，共计{int((session.query(Uri).count() / limit) + 1)}页')
    for page_index in range(1, int((session.query(Uri).count() / limit) + 2)):
        logger.info(f'[{page_index}]开始处理第{page_index}页')
        temp_uri_total = 0
        temp_api_total = 0
        for uri in session.query(Uri).order_by(Uri.update_time.asc()).limit(limit).offset((page_index - 1) * limit):
            if uri.info_id in be_regular_api_id_list:
                if uri.update_time not in m:
                    m[uri.update_time] = {}
                if uri.info_id not in m[uri.update_time]:
                    m[uri.update_time][uri.info_id] = set()
                for resource in uri.uri.replace('"', "").split('/'):
                    if len(resource) > 0:
                        m[uri.update_time][uri.info_id].add(resource)
                        temp_uri_total += 1
                        if uri.info_id not in api_set:
                            api_set.add(uri.info_id)
                            temp_api_total += 1
        logger.info(f'本次统计api：{temp_api_total}个，uri：{temp_uri_total}个')
    for update_time in m:
        total = 0
        api_count = 0
        available = 0
        for info_id in m[update_time]:
            resource_set = m[update_time][info_id]
            if len(resource_set) > 0:
                available = 1
                total = total + len(resource_set)
                api_count = api_count + 1
        if available == 1:
            x.append(update_time)
            y.append(total / api_count)

    trend_counter.auto(x, y, "The Trend of the average of Uri's Resources")


def endpoint():
    limit = 130000
    x = []
    y = []
    m = {}
    api_set = set()
    session = parser.init_session('localhost', 'root', 'root', 'api_version')
    logger.info('开始')
    sql = "SELECT id FROM info group by new_path having count(id) >= 12"
    result = session.execute(sql)
    be_regular_api_id_list = []
    for result_data in result:
        be_regular_api_id_list.append(result_data[0])
    logger.info(f'预计统计{len(be_regular_api_id_list)}篇文档，共计{int((session.query(Method).count() / limit) + 1)}页')
    for page_index in range(1, int((session.query(Method).count() / limit) + 2)):
        logger.info(f'[{page_index}]开始处理第{page_index}页')
        temp_method_total = 0
        temp_api_total = 0
        for method in session.query(Method).order_by(Method.update_time.asc()).limit(limit).offset((page_index - 1) * limit):
            if method.info_id in be_regular_api_id_list:
                if method.update_time not in m:
                    m[method.update_time] = {}
                if method.info_id not in m[method.update_time]:
                    m[method.update_time][method.info_id] = []
                api_set.add(method.info_id)
                temp_method_total += 1
                if method.info_id not in api_set:
                    api_set.add(method.info_id)
                    temp_api_total += 1
                m[method.update_time][method.info_id].append(method.method+method.uri)
        logger.info(f'本次统计api：{temp_api_total}个，method：{temp_method_total}个')
    for update_time in m:
        total = 0
        api_count = 0
        for info_id in m[update_time]:
            total = total + len(m[update_time][info_id])
            api_count = api_count + 1
        if total != 0 and total != api_count:
            x.append(update_time)
            y.append(total / api_count)
    trend_counter.auto(x, y, "The Trend of the average of Endpoints' Statistics")


endpoint()


def request_param():
    pass


def request_param_location():
    pass
