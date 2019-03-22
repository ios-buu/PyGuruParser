# code=utf-8

import re
import json
from sqlalchemy import Column, String, Integer, Text, CLOB, JSON, create_engine
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm import sessionmaker,mapper
from sqlalchemy.ext.declarative import declarative_base
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
# info -> 每个API的单独数据

# externalDocs -> 文档信息

# host -> 根目录

# basePath -> 当前文档在host中的目录

# schemes -> 可访问的协议

# consumes | produces -> content-type

# securityDefinitions | security -> 安全协议

# paths -> API文档

Base = declarative_base()


class Info(Base):
    __tablename__ = 'info'
    id = Column(Integer, primary_key=True)
    version = Column(String)
    basePath = Column(String)
    host = Column(String)
    termsOfService = Column(String)
    title = Column(String)
    schemes = Column(String)
    paths = Column(String)
    domain_key = Column(String)


class Uri(Base):
    # 表的名字:
    __tablename__ = 'uri'
    # 表的结构:
    id = Column(Integer)
    uri = Column(String, primary_key=True)
    method_count = Column(Integer)
    info_id = Column(Integer, primary_key=True)
    version = Column(String)
    title = Column(String)


class Method(Base):
    # 表的名字:
    __tablename__ = 'method'
    # 表的结构:
    id = Column(Integer)
    uri_id = Column(Integer)
    uri = Column(String, primary_key=True)
    method = Column(String, primary_key=True)
    info_id = Column(Integer)
    description = Column(String)
    has_param = Column(Integer)
    request = Column(JSON)
    request_count = Column(Integer)
    response = Column(JSON)


class Request(Base):
    # 表的名字:
    __tablename__ = 'request'
    __table_args__ = {"useexisting": True}
    # 表的结构:
    id = Column(Integer)
    info_id = Column(Integer)
    uri_id = Column(Integer)
    uri = Column(String, primary_key=True)
    method_id = Column(Integer)
    method = Column(String, primary_key=True)
    name = Column(String, primary_key=True)
    description = Column(String)
    required = Column(Integer)
    type = Column(String)
    _in = Column(String)
    minimum = Column(String)
    maximum = Column(String)
    format = Column(String)
    pattern = Column(String)
    schema = Column(JSON)


class Response(Base):
    # 表的名字:
    __tablename__ = 'response'
    # 表的结构:
    id = Column(Integer)
    info_id = Column(Integer, primary_key=True)
    uri_id = Column(Integer)
    uri = Column(String, primary_key=True)
    method_id = Column(Integer)
    method = Column(String, primary_key=True)
    code = Column(String, primary_key=True)
    description = Column(String)
    schema = Column(JSON)


# definitions -> 数据定义

# parameters -> 变量的结构及信息

def list_to_string(list):
    result = ""
    for elem in list:
        if type(elem) is list or type(elem) is dict:
            return list
        result+=(str(elem) + ',')
    return result[:-1]
def alter_column(temp_session, alter_table, alter_table_name, alter_column_name, column_data_type, database):
    data = temp_session.execute(f'SELECT 1 '
                                f'FROM INFORMATION_SCHEMA.COLUMNS '
                                f'WHERE `TABLE_NAME` = "{alter_table_name}" '
                                f'AND `TABLE_SCHEMA` = "{database}" '
                                f'AND `COLUMN_NAME` = "{alter_column_name}"')
    column_type = MEDIUMTEXT
    if column_data_type != str:
        column_type = JSON
    if data.rowcount is 0:
        temp_session.execute(f'ALTER TABLE `{alter_table_name}` ADD `{alter_column_name}` mediumtext default "";')
    try:
        setattr(alter_table, f'{alter_column_name}', Column(column_type,default=""))
    except:
        pass


def clean_transform_means_logic(data):
    if type(data) != dict and type(data) != list:
        if type(data) == str:
            return data.replace('\\"', "'").replace('"', "'").replace('\\', '\\\\')
        return data
    result = None
    if type(data) == dict:
        result = {}
        for key in data:
            result[key] = clean_transform_means_logic(data[key])
    elif type(data) == list:
        result = []
        for elem in data:
            result.append(clean_transform_means_logic(elem))
    return result


def clean_ref_data_logic(origin, data, path=None):
    """
        :param origin: 传入的原数据
        :param data: 递归调用的传递数据
        :return: 返回处理后的结果
        本函数用于清洗data中的引用数据，将所有$ref替换为引用的对象
    """
    filter_list = ['name', 'description', 'type', 'in', 'operationId', 'tags', 'file_path']
    if type(data) != dict and type(data) != list:
        return data
    if type(data) is dict:
        for item_name in data:
            if item_name == '$ref' and type(data[item_name]) == str:
                ref_paths = data[item_name].split("/")
                temp = origin
                has_ref = False
                node = None
                for ref_path in ref_paths[1:]:
                    node = ref_path
                    has_ref = True
                    temp = temp.get(ref_path)
                    if not temp:
                        return data
                if f'{node}/' in f"{path}":
                    return data
                if has_ref:
                    ref = clean_ref_data_logic(origin, temp, f"{path}{node}/")
                    data['$ref'] = ref
                return data
            elif item_name == '$ref' and type(data[item_name]) != str:
                return data
            elif item_name not in filter_list:
                data[item_name] = clean_ref_data_logic(origin, data[item_name], f"{path}{item_name}/")
    else:
        i = 0
        for item in data:
            if type(item) == str and '#/' in item:
                ref_path = item.split("/")
                temp = origin
                has_ref = False
                for path in ref_path[1:]:
                    temp = temp.get(path)
                    if not temp:
                        return data
                if has_ref:
                    data[item] = clean_ref_data_logic(origin, temp, f"{path}{i}/")
            else:
                data[i] = clean_ref_data_logic(origin, data[i], f"{path}{i}/")
            i += 1
    return data


def build_table(data, host, username, password, database):
    """
    :param data: 转换成dict的yaml数据
    :param host: 数据库host
    :param username: 数据库用户名
    :param password: 数据库密码
    :param database: 数据库名称
    :return: void
    """
    # 建立链接
    engine = create_engine(f'mysql://{username}:{password}@{host}/{database}')
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    # 创建指针
    # 创建信息表
    session.execute("CREATE TABLE IF NOT EXISTS info("
                   "id INT PRIMARY KEY AUTO_INCREMENT,"
                   "domain_key VARCHAR(512) NOT NULL,"
                   "version VARCHAR(64),"
                   "title VARCHAR(256),"
                   "description VARCHAR(2048),"
                   "x_logo VARCHAR(2048),"
                   " UNIQUE KEY `unique_key_1` (`version`,`domain_key`)"
                   ")")
    # 静态的预设字段
    static_column_list = ['id', 'version', 'title', 'description', 'x-logo']
    # 提交一次
    session.flush()
    # 提取info中的字段
    if data.get('info'):
        for column_name in data['info']:
            # 判断是否属于上面的静态字段
            if column_name not in static_column_list:
                column_name = column_name.replace('-', '_')
                data = session.execute(f'SELECT 1 '
                                            f'FROM INFORMATION_SCHEMA.COLUMNS '
                                            f'WHERE `TABLE_NAME` = "info" '
                                            f'AND `TABLE_SCHEMA` = "{database}" '
                                            f'AND `COLUMN_NAME` = "{column_name}"')

                if data.rowcount is 0:
                    session.execute(f'ALTER TABLE `info` ADD `{column_name}` mediumtext default "";')

    # 静态的预设字段
    static_column_list = ['info']

    # 提取除info外的所有字段
    for column_name in data:
        if column_name not in static_column_list:
            column_name = column_name.replace('-', '_')
            data = session.execute(f'SELECT 1 '
                                   f'FROM INFORMATION_SCHEMA.COLUMNS '
                                   f'WHERE `TABLE_NAME` = "info" '
                                   f'AND `TABLE_SCHEMA` = "{database}" '
                                   f'AND `COLUMN_NAME` = "{column_name}"')

            if data.rowcount is 0:
                session.execute(f'ALTER TABLE `info` ADD `{column_name}` mediumtext default "";')
    session.commit()
    session.close()


def convert(host, username, password, database):
    """
    :param host: 数据库host
    :param username: 数据库用户名
    :param password: 数据库密码
    :param database: 数据库名称
    :return:
    """
    # 建立链接
    logger.info('建立连接')
    engine = create_engine(f'mysql://{username}:{password}@{host}/{database}')
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    # 创建指针
    info_list = session.query(Info).all()
    uri_id = 1
    method_id = 1
    request_id = 1
    response_id = 1
    info_count = 1
    request_field = ['id','info_id','uri_id','uri','method_id','type','method','name','description','required','_in','in','minimum','maximum','format','pattern','schema']

    for info_pojo in info_list:
        logger.info(f'[{info_pojo.id}] 开始处理编号为{info_pojo.id}的文档「{info_pojo.domain_key}」')
        try:
            paths = json.loads(info_pojo.paths.replace("\\", "\\\\"), strict=False)
            logger.info(f'[{info_pojo.id}] 开始匹配资源路径，编号从{uri_id}开始，预计处理{len(paths)}条。')
            for uri_str in paths:
                try:
                    uri = paths[uri_str]
                    if 'parameters' in uri:
                        del uri['parameters']
                    uri_pojo = Uri(
                        id=uri_id,
                        uri=uri_str,
                        method_count=len(uri),
                        version=json.loads(info_pojo.version),
                        title=json.loads(info_pojo.title),
                        info_id=info_pojo.id
                    )
                    uri_id += 1
                    session.add(uri_pojo)
                    logger.info(f'[{info_pojo.id}] 开始匹配[{uri_pojo.uri}]资源的谓词，编号从{method_id}开始，预计处理{len(uri)}条。')
                    for method_str in uri:
                        try:
                            methods = uri[method_str]
                            method_pojo = Method(
                                id=method_id,
                                method=method_str,
                                description=methods.get('description'),
                                has_param=1 if (methods.get('parameters') and len(methods.get('parameters')) > 0) else 0,
                                request=json.dumps(methods.get('parameters')),
                                request_count=len(methods.get('parameters')) if methods.get('parameters') is not None else 0,
                                response=json.dumps(methods.get('responses')),
                                uri_id=uri_pojo.id,
                                info_id=info_pojo.id,
                                uri=uri_pojo.uri
                            )
                            method_id += 1
                            session.add(method_pojo)
                            if "responses" in methods:
                                responses = methods['responses']
                                logger.info(f'[{info_pojo.id}] 开始匹配[{uri_pojo.uri}]资源的谓词[{method_pojo.method}]的response，编号从{response_id}开始，预计处理{len(responses)}条。')
                                for response_code in responses:
                                    try:
                                        response = responses[response_code]
                                        response_pojo = Response(
                                            id=response_id,
                                            info_id=info_pojo.id,
                                            uri_id=uri_pojo.id,
                                            uri=uri_pojo.uri,
                                            method_id=method_pojo.id,
                                            method=method_pojo.method,
                                            code=response_code,
                                            description=response.get('description')
                                        )
                                        if "schema" in response and "$ref" in response["schema"] and type(response["schema"]['$ref']) != str:
                                            response_pojo.__setattr__('schema', response["schema"]['$ref'])
                                        elif "schema" in response:
                                            response_pojo.__setattr__('schema', response["schema"])
                                        response_id += 1
                                        session.add(response_pojo)
                                    except:
                                        logger.exception(f"[{info_pojo.id}][{uri_pojo.uri}][{method_pojo.method}] -> res[{response_pojo.code}]出现错误 ->  {sys.exc_info()}]")

                            if "parameters" in methods:
                                parameters = methods['parameters']
                                logger.info(f'[{info_pojo.id}] 开始匹配[{uri_pojo.uri}]资源的谓词[{method_pojo.method}]的request，编号从{request_id}开始，预计处理{len(responses)}条。')
                                for param_elem in parameters:
                                    try:
                                        if "$ref" in param_elem:
                                            param_elem = param_elem['$ref']
                                        request_pojo = Request(
                                            id=request_id,
                                            info_id=info_pojo.id,
                                            uri_id=uri_pojo.id,
                                            uri=uri_pojo.uri,
                                            method_id=method_pojo.id,
                                            method=method_pojo.method
                                        )
                                        if type(param_elem) is not dict:
                                            request_pojo.__setattr__('schema',param_elem)
                                            continue
                                        request_pojo.__setattr__('_in', param_elem.get('in'))
                                        request_pojo.__setattr__('name',"None" if param_elem.get('name')else param_elem['name'])
                                        if param_elem.get("schema") and param_elem.get("schema").get('$ref') and type(
                                                param_elem.get("schema").get('$ref')) != str:
                                            request_pojo.__setattr__('schema', param_elem.get("schema").get('$ref'))
                                        elif "schema" in param_elem:
                                            request_pojo.__setattr__('schema', param_elem.get("schema"))

                                        for param_elem_name in param_elem:
                                            temp_param_elem_name = param_elem_name.replace('-','_')
                                            if param_elem_name not in request_field:
                                                alter_column(session, Request, "request", temp_param_elem_name, type(param_elem[param_elem_name]),database)
                                                Base.metadata.create_all(engine)
                                                request_field.append(param_elem_name)
                                                request_field.append(temp_param_elem_name)
                                            insert_elem = param_elem[param_elem_name]
                                            if type(param_elem[param_elem_name])==list:
                                                insert_elem = list_to_string(param_elem[param_elem_name])
                                            request_pojo.__setattr__(temp_param_elem_name, insert_elem)
                                        request_id += 1
                                        session.add(request_pojo)

                                    except:
                                        logger.exception(f"[{info_pojo.id}][{uri_pojo.uri}][{method_pojo.method}] -> req出现错误 ->  {sys.exc_info()}]")
                        except:
                            logger.exception(f"[{info_pojo.id}][{uri_pojo.uri}][{method_pojo.method}] 执行错误 ->  {sys.exc_info()}]")
                except:
                    logger.exception(f"[{info_pojo.id}][{uri_pojo.uri}] 执行错误 ->  {sys.exc_info()}]")
            session.commit()
        except:
            logger.exception(f"[{info_pojo.id}] 执行错误 ->  {sys.exc_info()}]")
        info_count += 1
    session.close()
    logger.info(f'本次共遍历info数据{info_count}条，解析出来uri{uri_id}个,method{method_id}个,request{request_id}个,response{response_id}个')
convert('localhost','root','root','api_swagger_source')

def insert(data, host, username, password, database, build=False):
    """
    :param data: 转换成dict的yaml数据
    :param host: 数据库host
    :param username: 数据库用户名
    :param password: 数据库密码
    :param database: 数据库名称
    :param build: 是否初始化数据库
    :return: void
    """
    logger.info('建立数据库连接...')
    if build:
        build_table(data, host, username, password, database)
    # 建立链接

        # 建立链接
    engine = create_engine(f'mysql://{username}:{password}@{host}/{database}')
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    # 创建空间
    domain_key = data['host']
    if data.get('basePath'):
        domain_key = domain_key + data['basePath']
    if data.get('file_path') and 'APIs' in data['file_path']:
        domain_key = domain_key + '|' + data['file_path'].split('APIs')[1].replace('/swagger.yaml', '')
    insert_data = {'domain_key': domain_key}
    # 创建指针
    # 包装info
    if data.get('info'):
        for column_name in data['info']:
            insert_data[column_name] = data['info'][column_name]
    # 包装data
    if data:
        for column_name in data:
            if column_name != 'info':
                insert_data[column_name] = data[column_name]
    # 清洗data
    logger.info('清洗data的ref')
    insert_data = clean_ref_data_logic(insert_data, insert_data, path='$ref/')
    logger.info('清洗data的特殊字符')
    insert_data = clean_transform_means_logic(insert_data)
    # insert时的字段字符串
    column_text = ''
    # insert时的数据字符串
    data_text = ''
    # 更新时的字符串
    update_text = ''
    # 包装sql字符串
    for column_name in insert_data:
        # 替换字符 - 为 _
        temp_column_name = column_name.replace('-', '_')
        # column_text是insert时，要添加的字段部分
        column_text = column_text + f'{temp_column_name},'
        # temp_data 作临时转存
        temp_data = insert_data[column_name]
        temp_data = json.dumps(temp_data, check_circular=False, ensure_ascii=False) \
            .replace('"', '\\"') \
            .replace("\n", "") \
            .replace("'", "\\'")
        # data_text是insert时，要添加的数据部分
        data_text = data_text + f"'{temp_data}',"
        # update_text时update时，要更改的部分字符串
        update_text = update_text + temp_column_name + "='" + temp_data + "',"
    # 查询是否存在
    sql = "SELECT id FROM info WHERE domain_key = '" + insert_data['domain_key'] + "' AND version ='" + insert_data['version'] + "'"

    # 提交
    result = session.execute(sql)
    # 获取结果
    # 不存在 -> insert | 存在 -> update
    if result.rowcount is 0:
        sql = f'INSERT INTO info({column_text[:-1]}) VALUES({data_text[:-1]})'
    else:
        sql = f'UPDATE info SET {update_text[:-1]} WHERE id={result[0]}'
    # print(insert_data['domain_key'] + " " + insert_data['version'] + " " + insert_data['title'])
    # logger.info(f'执行sql:[{sql}]')
    try:
        # 执行sql语句
        session.execute(sql)
        # 提交到数据库执行
        session.commit()
    except Exception as e:
        logger.error('插入异常 -> ' + insert_data['host'])
        logger.error(e)
        session.rollback()
    session.close()
