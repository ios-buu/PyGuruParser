# code=utf-8

import logging
import sys
import time


log_name = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler(f"{log_name} counter.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.INFO)

logger.addHandler(handler)
logger.addHandler(console)

def add_elem(data_list,index,element,default=None):
    if len(data_list) >= index:
        data_list.insert(index,element)
        return data_list
    for i in range(len(data_list),index):
        data_list.insert(i,default)
    data_list.insert(index,element)
    return data_list

def count_api_layer(data_set):
    """
    从data_set中统计uri相关数据，['/user','/user/{id}']
    :return: (总数,众数,平均数量,最大层数,最小层数,层数[1,2,3],每层对应的uri个数[10,10,10])
    """
    for uri in data_set:
        if type(uri) is not str:
            raise Exception("传入数据应为['/user','/user/{id}']格式的数据，list中包含str类型的路径列表")
    count = 0
    most_layer = 0
    maximum_layer = 0
    layer_list = []
    uri_count_every_layer = []

    for uri in data_set:
        count+=1

        if uri == '/':
            layer = 0
        else:
            resource = str(uri).split('/')
            layer = len(resource) - 1

        if len(uri_count_every_layer)<=layer:
            add_elem(uri_count_every_layer,layer,0)

        if layer>=maximum_layer:
            maximum_layer = layer
        if uri_count_every_layer[layer] is not None:
            uri_count_every_layer[layer] = uri_count_every_layer[layer]+1
        else:
            uri_count_every_layer[layer] = 1
    average_sum = 0
    layer = 0
    most_count = 0
    for uri_count in uri_count_every_layer:
        if uri_count is not None:
            if uri_count>most_count:
                most_count = uri_count
                most_layer = layer
            layer_list.append(layer)
            average_sum += (layer * uri_count)
            layer += 1
    if count==0:
        average = 0
    else:
        average = average_sum / count
    return count, average, most_layer, maximum_layer, layer_list, uri_count_every_layer

def count_method(data_set):
    """
    从data_set中获取所有的method，并进行数据分析，[['/uesr','get',info_id],['/user/{id}','post',info_id]]
    :param data_set:
    :return: 最多值['get',0]，最少值['get',0]，['0','33','66']，['get','head','patch'],[0,1,2]
    """
    method_count = []
    method_list = []
    method_index = 0
    method_percentage= []
    method_map = {}
    total = 0
    maximum = ['get',0]
    minimum = ['get',10000000]
    for elem in data_set:
        # TODO 2019-03-26 21:16:00 url可以作为其他的分析目前没用
        url = str(elem[2]) + '<::>'+elem[0]
        method = elem[1]
        total += 1
        if method not in method_list:
            method_count.append(1)
            method_list.append(method)
            method_map[method] = method_index
            method_index += 1
        else:
            method_count[method_map[method]] += 1
    for index in range(0,len(method_list)):
        count = method_count[index]
        method = method_list[index]
        method_percentage.append(count/total)
        if count>maximum[1]:
            maximum[0] = method
            maximum[1] = count
        if count<minimum[1]:
            minimum[0] = method
            minimum[1] = count
    return maximum,minimum,method_percentage,method_list,method_count

def count_data_layer():
    # TODO 2019-03-26 21:37:00 数据层数不好写.....
    pass

def count_version():
    # TODO 2019-03-26 21:37:00 版本统计不好写.....
    pass
def count_constrain():
    # TODO 2019-03-26 21:37:00 约束不好写.....
    pass

def count_request_param(data_set):
    """
    请求参数，[['query','/user/{id}',info_id,'get'],['param','/user/{id}',info_id,'get']]
    :param data_set:
    :return: total,average,['quiry',2000],[1,2,3],[100,200,300],['query','body],[20,50]
    """
    api_set = set()
    param_count = 0
    average = 0
    most = ['default',0]
    param_count_map = {}
    param_count_list = []
    api_count_list = []
    location_list = []
    location_param_count_list = []
    location_index = 0
    location_map = {}
    for elem in data_set:
        in_ = elem[0]
        url = elem[1]
        info_id = elem[2]
        method = elem[3]
        temp_url = str(info_id)+'<::>'+url+'<::>'+method
        api_set.add(temp_url)
        param_count +=1
        if temp_url not in param_count_map:
            param_count_map[temp_url] = 1
        else:
            param_count_map[temp_url] = param_count_map[temp_url] +1
        if in_ not in location_map:
            location_map[in_] = location_index
            location_index += 1
            location_list.append(in_)
            location_param_count_list.append(1)
        else:
            location_param_count_list[location_map[in_]] = location_param_count_list[location_map[in_]]+1
    for uri in param_count_map:
        count = param_count_map[uri]
        if len(api_count_list)<=count:
            add_elem(api_count_list,count,1,default=0)
        else:
            api_count_list[count] = api_count_list[count]+1
    for index in range(0,location_index):
        location = location_list[index]
        count = location_param_count_list[index]
        if count>most[1]:
            most[0]=location
            most[1] = count
    for index in range(0,len(api_count_list)):
        param_count_list.append(index)
    average = param_count/len(api_set)
    return len(api_set),param_count,average,most,param_count_list,api_count_list,location_list,location_param_count_list

def count_request_param_location(data_set):
    """
    请求参数的位置统计，[['query','/user/{id}',info_id,'get'],['param','/user/{id}',info_id,'get']]
    :param data_set:
    :return:
    (['query', 'param'], [0, 1, 2], [[0, 1, 1], [0, 0, 1]], [0, 1, 2], [0, 1, 1])
    ?1: 所有参数位置的列表
    ?2: 参数个数
    ?3: [[0, 1, 1], [0, 0, 1]] 代表着query中没有参数的url有0个，有一个参数的url有1个，有两个参数的url有1个。param中，只有1个带2个参数的url，其他都没有
    ?4: 位置个数
    ?5: [0, 1, 1] 没有参数的url有0个，有1个位置参数的url有1个，有2个位置参数的有1个
    """
    api_in_location_count_map = {}
    api_map = {}
    maximum_location = 0
    maximum_param = 0
    for elem in data_set:
        location = elem[0]
        api = f'{str(elem[2])}<::>{str(elem[3])}<::>{elem[1]}'
        api_count_map = {}
        if location in api_in_location_count_map:
            api_count_map = api_in_location_count_map[location]
        if api not in api_map:
            api_map[api] = set()
        if api not in api_count_map:
            api_count_map[api] = 1
        else:
            api_count_map[api]+=1
        api_map[api].add(location)
        api_in_location_count_map[location] = api_count_map
    location_list = []
    location_index_map = {}
    location_index = 0
    for url in api_map:
        if len(api_map[url])>maximum_location:
            maximum_location= len(api_map[url])
    for location in api_in_location_count_map:
        for info in api_in_location_count_map[location]:
            location_elem = api_in_location_count_map[location][info]
            if location_elem>maximum_param:
                maximum_param = location_elem
        if location not in location_list:
            location_list.append(location)
            location_index_map[location] = location_index
            location_index+=1
    param_count_list_list = []
    param_count_index_list = []
    location_count_list = []
    location_count_index_list = []
    for index in range(0,maximum_param+1):
        param_count_list_list.append(add_elem([],location_index-1, 0, 0))

    for index in range(0,maximum_param+1):
        param_count_index_list.append(index)
    for index in range(0, maximum_location+1):
        location_count_index_list.append(index)
        location_count_list.append(0)
    for location in api_in_location_count_map:
        api_count_map = api_in_location_count_map[location]
        for api in api_count_map:
            param_count_list_list[api_count_map[api]][location_index_map[location]] += 1
    for location_set in api_map:
        location_count_list[len(api_map[location_set])] +=1

    return location_list,param_count_index_list,param_count_list_list,location_count_index_list,location_count_list

def count_resource(data_set):
    """
    请求的资源统计
    :param data_set:  [['/user',info_id],['/user/{id}',info_id],['/user/info',info_id]]
    :return: total,average,most,maximum,minimum,[0,1,2,3,4],[0,10,50,100,200]
    """
    total = 0
    maximum = 0
    minimum = 10000000
    resource_map = {}
    resource_index_list = []
    resource_count_list = []
    for elem in data_set:
        url = elem[0]
        info_id = elem[1]
        if info_id not in resource_map:
            resource_map[info_id] = set()
        if url == '/':
            resource_map[info_id].add('/')
        else:
            for resource in url.split('/'):
                if "{" not in resource and resource is not '':
                    resource_map[info_id].add(resource)
    for info_id in resource_map:
        resource_count = len(resource_map[info_id])
        total += resource_count
        if resource_count>maximum:
            maximum = resource_count
        if resource_count<minimum:
            minimum = resource_count
        if len(resource_count_list)<=resource_count:
            add_elem(resource_count_list,resource_count,1,default=0)
        else:
            resource_count_list[resource_count]+=1
    for index in range(0,len(resource_count_list)):
        resource_index_list.append(index)
    average = total/len(resource_map)
    return total,average,maximum,minimum,resource_index_list,resource_count_list

def count_uri(data_set):
    """
    请求api的数量
    :param data_set: [['/user',info_id],['/user/{id}',info_id],['/user/info',info_id],['/user/auth',info_id]]
    :return: total,average,most,maximum,minimum,[0,1,2,3,4],[0,10,50,100,200]
    """
    total = 0
    maximum = 0
    minimum = 10000000
    api_map = {}
    api_index_list = []
    api_count_list = []
    for elem in data_set:
        url = elem[0]
        info_id = elem[1]
        if info_id not in api_map:
            api_map[info_id] = set()
        api_map[info_id].add(url)
    for info_id in api_map:
        api_count = len(api_map[info_id])
        total += api_count
        if api_count> maximum:
            maximum = api_count
        if api_count<minimum:
            minimum = api_count
        if len(api_count_list)<=api_count:
            add_elem(api_count_list,api_count,1,default=0)
        else:
            api_count_list[api_count]+=1
    for index in range(0,len(api_count_list)):
        api_index_list.append(index)
    average = total / len(api_map)
    return total,average,maximum,minimum,api_index_list,api_count_list

def count_endpoint(data_set):
    """
    请求api的数量
    :param data_set: [['/user','get',info_id],['/user/{id}','get',info_id],['/user/info','get',info_id],['/user/auth','get',info_id]]
    :return: total,average,most,maximum,minimum,[0,1,2,3,4],[0,10,50,100,200]
    """
    total = 0
    maximum = 0
    minimum = 10000000
    endpoint_map = {}
    endpoint_index_list = []
    endpoint_count_list = []
    for elem in data_set:
        url = f'{elem[1]}<::>{elem[0]}'
        info_id = elem[2]
        if info_id not in endpoint_map:
            endpoint_map[info_id] = set()
        endpoint_map[info_id].add(url)
    for info_id in endpoint_map:
        api_count = len(endpoint_map[info_id])
        total += api_count
        if api_count> maximum:
            maximum = api_count
        if api_count<minimum:
            minimum = api_count
        if len(endpoint_count_list)<=api_count:
            add_elem(endpoint_count_list,api_count,1,default=0)
        else:
            endpoint_count_list[api_count]+=1
    for index in range(0,len(endpoint_count_list)):
        endpoint_index_list.append(index)
    average = total / len(endpoint_map)
    return total,average,maximum,minimum,endpoint_index_list,endpoint_count_list
