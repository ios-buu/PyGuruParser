# -*- coding: utf-8 -*-

import numpy as np
import matplotlib
import time

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from suppose import counter
from suppose.parser import Method, Info, Request, Response, Uri
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def auto_label_single(x, y):
    for a, b in zip([x], [y]):
        plt.text(a, b + 0.05, '%.0f' % b, ha='center', va='bottom', fontsize=11)


def auto_label_set(x, y, maximum_limit=None):
    i = 0
    for a, b in zip(x, y):
        if (maximum_limit and i < maximum_limit) or b is not 0:
            plt.text(a, b + 0.05, '%.0f' % b, ha='center', va='bottom', fontsize=11)
        i += 1


def print_endpoint(username, password, host, database):
    engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}/{database}')
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    data_set = []
    for method in session.query(Method).all():
        data_set.append([method.uri, method.method, method.info_id])
    (total, average, maximum, minimum, x, y) = counter.count_endpoint(data_set)
    auto_label_set(x, y)
    width = 0.35
    ind = np.arange(len(x))
    locs, labels = plt.xticks(ind, x)
    plt.yticks(np.arange(0, max(y) + (max(y) / 10), (max(y) + 1) / 10))
    plt.ylabel('The quantity of apis')
    plt.xlabel('The quantity of endpoints in apis')
    plt.title('The statistics of endpoints')
    plt.bar(ind, y, width)
    plt.text(len(x) - len(x) / 3, max(y),
             f'the total quantity of endpoints is {total}\nthe average quantity of endpoints in apis is {average}\nThe maximum quantity of endpoints in apis is {maximum}\nThe minimum of endpoints in apis is {minimum}',
             ha='left', va='top', fontsize=9)
    for label in labels:
        label.set_visible(False)
    for label in labels[::20]:
        label.set_visible(True)
    plt.show()
    plt.close()


def print_uri(username, password, host, database):
    engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}/{database}')
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    data_set = []
    for uri in session.query(Uri).all():
        data_set.append([uri.uri, uri.info_id])
    (total, average, maximum, minimum, x, y) = counter.count_uri(data_set)
    auto_label_set(x, y)
    width = 0.35
    ind = np.arange(len(x))
    locs, labels = plt.xticks(ind, x)
    plt.yticks(np.arange(0, max(y) + (max(y) / 10), (max(y) + 1) / 10))
    plt.ylabel('The quantity of apis')
    plt.xlabel('The quantity of uri in apis')
    plt.title('The statistics of uri')
    plt.bar(ind, y, width)
    plt.text(len(x) - len(x) / 3, max(y),
             f'the total quantity of uri is {total}\nthe average quantity of uri in apis is {average}\nThe maximum quantity of uri in apis is {maximum}\nThe minimum of uri in apis is {minimum}',
             ha='left', va='top', fontsize=9)
    for label in labels:
        label.set_visible(False)
    for label in labels[::20]:
        label.set_visible(True)
    plt.show()
    plt.close()


def print_resource(username, password, host, database):
    engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}/{database}')
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    data_set = []
    for uri in session.query(Uri).all():
        data_set.append([uri.uri, uri.info_id])
    (total, average, maximum, minimum, x, y) = counter.count_resource(data_set)
    auto_label_set(x, y)
    width = 0.35
    ind = np.arange(len(x))
    locs, labels = plt.xticks(ind, x)
    plt.yticks(np.arange(0, max(y) + (max(y) / 10), (max(y) + 1) / 10))
    plt.ylabel('The quantity')
    plt.xlabel('The layer of resource')
    plt.title('The statistics of resource')
    plt.bar(ind, y, width)
    plt.text(len(x) - len(x) / 3, max(y),
             f'the total quantity of resources is {total}\nthe average quantity of resource in api is {average}\nThe maximum quantity of resource in apis is {maximum}\nThe minimum of resource in apis is {minimum}',
             ha='left', va='top', fontsize=9)
    for label in labels:
        label.set_visible(False)
    for label in labels[::20]:
        label.set_visible(True)
    plt.show()
    plt.close()


def print_request_param(username, password, host, database):
    engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}/{database}')
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    data_set = []
    for request in session.query(Request).all():
        data_set.append([request._in, request.uri, request.info_id, request.method])
    (api_count, param_count, average, maximum, x, y, x_, y_) = counter.count_request_param(data_set)
    plt.subplot(2, 1, 1)
    auto_label_set(x, y)
    width = 0.35
    ind = np.arange(len(x))
    locs, labels = plt.xticks(ind, x)
    plt.yticks(np.arange(0, max(y) + (max(y) / 10), (max(y) + 1) / 10))
    plt.ylabel('The quantity of param')
    plt.xlabel('The quantity of endpoint')
    plt.title('The param in endpoint')
    plt.bar(ind, y, width)
    for label in labels:
        label.set_visible(False)
    for label in labels[::20]:
        label.set_visible(True)

    plt.text(max(x) - max(x) / 2, max(y) + 100,
             f"The total of endpoint which has param is {api_count}\nThe quantity of param is {param_count}\nThe average quantity of param in every endpoint is {average}\nThe maximum quantity of parameter's position is {maximum[0]} at {maximum[1]}",
             ha='left', va='top', fontsize=9)

    plt.subplot(2, 1, 2)
    x_list = []
    for index in range(0, len(x_)):
        x_list.append(index)
    auto_label_set(x_list, y_)
    width = 0.35
    ind = np.arange(len(x_))
    plt.xticks(ind, x_)
    plt.yticks(np.arange(0, max(y_) + (max(y_) / 10), (max(y_) + 1) / 10))
    plt.ylabel('The quantity of parameter in position')
    plt.xlabel('The position of parameter')
    plt.title('The position of parameter')
    plt.bar(ind, y_, width)

    plt.show()
    plt.close()


def print_method(username, password, host, database):
    engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}/{database}')
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    data_set = []
    for method in session.query(Method).all():
        data_set.append([method.uri, method.method, method.info_id])
    (maximum, minimum, method_percentage, method_list, y) = counter.count_method(data_set)
    x = []
    for percentage, method in zip(method_percentage, method_list):
        x.append(f"{method}\n{round(percentage,3)}")
    x_list = []
    for index in range(0, len(x)):
        x_list.append(index)
    auto_label_set(x_list, y)
    width = 0.35
    ind = np.arange(len(x))
    plt.xticks(ind, x)
    plt.yticks(np.arange(0, max(y) + (max(y) / 10), (max(y) + 1) / 10))
    plt.ylabel('The number of method')
    plt.xlabel('The fullname and the percentage of method')
    plt.title('The method in api')
    plt.bar(ind, y, width)
    plt.text(len(x) - 6, max(y) + 100,
             f'the maximum quantity of method is {maximum[0]} by {maximum[1]}\nthe minimum quantity of method is {minimum[0]} by {minimum[1]}',
             ha='left', va='top', fontsize=9)
    plt.show()
    plt.close()


def print_api_layer(username, password, host, database):
    engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}/{database}')
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    data_set = []
    for uri in session.query(Uri).all():
        data_set.append(uri.uri)
    (count, average, most_layer, maximum_layer, x, y) = counter.count_api_layer(data_set)
    auto_label_set(x, y)
    width = 0.35
    ind = np.arange(len(x))
    plt.xticks(ind, x)
    plt.yticks(np.arange(0, max(y) + (max(y) / 10), (max(y) + 1) / 10))
    plt.ylabel('The number of uri in every layer')
    plt.xlabel('The number of layer')
    plt.title('The layer in api')
    plt.bar(ind, y, width)
    plt.text(max(x) - 10, max(y) + 100,
             f'The total of api is {count}\nthe average is {average} layers\nthe maximum quantity of api is in {most_layer}-layer\nthe maximum quantity in layers is {maximum_layer} layers',
             ha='left', va='top', fontsize=9)
    plt.show()
    plt.close()


def print_request_param_location(username, password, host, database):
    engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}/{database}')
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    data_set = []
    for request in session.query(Request).all():
        elem = []
        elem.append(request._in)
        elem.append(request.uri)
        elem.append(request.info_id)
        elem.append(request.method)
        data_set.append(elem)
    (x, category, y_list, x_, y_) = counter.count_request_param_location(data_set)
    plt.subplot(1, 2, 1)
    width = 0.35
    ind = np.arange(len(x))
    y_data = []
    bottom = None
    for y in y_list:
        pn = plt.bar(ind, y, width, bottom=bottom)
        if bottom is not None:
            bottom += np.array(y)
        else:
            bottom = y
        y_data.append(pn[0])
    bottom_list = bottom.tolist()
    x_list = []
    for index in range(0, len(x)):
        x_list.append(index)
    auto_label_set(x_list, bottom_list)
    plt.xticks(ind, x)
    plt.yticks(np.arange(0, max(bottom) + (max(bottom) / 5), (max(bottom) + 1) / 10))
    plt.ylabel('The number of endpoints')
    plt.xlabel('The fullname of locations')
    plt.title('The distribution of the location of Request Param')
    plt.legend(['0', '1', '2', '3', '...', len(y_list), 'increase progressively'])

    plt.subplot(1, 2, 2)
    auto_label_set(x_list, y_)
    plt.xticks(ind, x_)
    plt.yticks(np.arange(0, max(y_) + (max(y_) / 10), (max(y_) + 1) / 10))
    plt.ylabel('The number of endpoints')
    plt.xlabel('The number of locations')
    plt.title('The statistics of locations in Request')
    p1 = plt.bar(ind, y_, width)
    plt.legend([p1[0]], ['total'], loc='upper right')
    plt.show()
    plt.close()
