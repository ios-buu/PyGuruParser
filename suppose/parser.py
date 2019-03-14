# code=utf-8

import MySQLdb
import re
import json
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String,ForeignKey
from sqlalchemy.orm import sessionmaker,relationship
from sqlalchemy import create_engine

# info -> 每个API的单独数据

# externalDocs -> 文档信息

# host -> 根目录

# basePath -> 当前文档在host中的目录

# schemes -> 可访问的协议

# consumes | produces -> content-type

# securityDefinitions | security -> 安全协议

# paths -> API文档

# definitions -> 数据定义

# parameters -> 变量的结构及信息

def clean_data_logic(origin, data):
    """
        :param origin: 传入的原数据
        :param data: 递归调用的传递数据
        :return: 返回处理后的结果
        本函数用于清洗data中的引用数据，将所有$ref替换为引用的对象
    """
    if type(data) != dict and type(data) != list:
        return data
    if type(data) == dict:
        for item_name in data:
            if type(data[item_name]) != str:
                return data
            if item_name == '$ref':
                ref_path = data['$ref'].split("/")
                temp = origin
                for path in ref_path[1:]:
                    temp = temp.get(path)
                    if not temp:
                        return data
                data['$ref'] = clean_data_logic(origin, temp)
                return data
            else:
                data[item_name] = clean_data_logic(origin, data[item_name])
    else:
        i = 0
        for item in data:
            if type(item) != str:
                return data
            if re.match('#/', item):
                ref_path = item.split("/")
                temp = origin
                for path in ref_path[1:]:
                    temp = temp.get(path)
                    if not temp:
                        return data
                data[item] = clean_data_logic(origin, temp)
            else:
                data[i] = clean_data_logic(origin, data[i])
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
    db = MySQLdb.connect(
        host,
        username,
        password,
        database,
        charset="utf8"
    )
    # 创建指针
    cursor = db.cursor()
    # 创建信息表
    cursor.execute("CREATE TABLE IF NOT EXISTS info("
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
    cursor.fetchone()
    # 提取info中的字段
    if data.get('info'):
        for column_name in data['info']:
            # 判断是否属于上面的静态字段
            if column_name not in static_column_list:
                column_name = column_name.replace('-', '_')
                result = cursor.execute(f'SELECT 1 '
                                        f'FROM INFORMATION_SCHEMA.COLUMNS '
                                        f'WHERE `TABLE_NAME` = "info" '
                                        f'AND `TABLE_SCHEMA` = "api_swagger_source" '
                                        f'AND `COLUMN_NAME` = "{column_name}"')
                # 如果不存在字段
                if result is 0:
                    # 创建字段
                    cursor.execute(f'ALTER TABLE `info` ADD `{column_name}` text;')

    # 静态的预设字段
    static_column_list = ['info']

    # 提取除info外的所有字段
    for column_name in data:
        if column_name not in static_column_list:
            column_name = column_name.replace('-', '_')
            data = cursor.execute(f'SELECT 1 '
                                  f'FROM INFORMATION_SCHEMA.COLUMNS '
                                  f'WHERE `TABLE_NAME` = "info" '
                                  f'AND `TABLE_SCHEMA` = "api_swagger_source" '
                                  f'AND `COLUMN_NAME` = "{column_name}"')
            if data is 0:
                cursor.execute(f'ALTER TABLE `info` ADD `{column_name}` mediumtext;')
    cursor.fetchall()
    db.close()


def convert(host, username, password, database):
    """
    :param host: 数据库host
    :param username: 数据库用户名
    :param password: 数据库密码
    :param database: 数据库名称
    :return:
    """
    # 建立链接
    db = MySQLdb.connect(
        host,
        username,
        password,
        database,
        charset="utf8"
    )
    # 创建指针
    cursor = db.cursor()
    cursor.execute("SELECT *")

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
    if build:
        build_table(data, host, username, password, database)
    # 建立链接

    db = MySQLdb.connect(
        host,
        username,
        password,
        database,
        charset="utf8"
    )
    # 创建空间
    domain_key = data['host']
    if data.get('basePath'):
        domain_key = domain_key + data['basePath']
    domain_key = domain_key + '|' + data['file_path'].split('APIs')[1].replace('/swagger.yaml', '')
    insert_data = {'domain_key': domain_key.replace('\\', '\\\\')}

    # 创建指针
    cursor = db.cursor()
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
    insert_data = clean_data_logic(insert_data, insert_data)
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
        if type(temp_data) is not str:
            temp_data = json.dumps(temp_data, ensure_ascii=False)
        temp_data = temp_data.replace("'", '"').replace('"', '"')
        # data_text是insert时，要添加的数据部分
        data_text = data_text + f"'{temp_data}',"
        # update_text时update时，要更改的部分字符串
        update_text = update_text + temp_column_name + "='" + temp_data + "',"
    # 查询是否存在
    sql = 'SELECT id FROM info WHERE domain_key = "' + insert_data['domain_key'] + '" AND version ="' + insert_data['version'] + '"'
    # 提交
    cursor.execute(sql)
    # 获取结果
    result = cursor.fetchone()
    # 不存在 -> insert | 存在 -> update
    if not result:
        sql = f'INSERT INTO info({column_text[:-1]}) VALUES({data_text[:-1]})'
    else:
        sql = f'UPDATE info SET {update_text[:-1]} WHERE id={result[0]}'
        print(insert_data['domain_key'] + " " + insert_data['version'] + " " + insert_data['title'])
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except Exception as e:
        print('插入异常 -> ' + insert_data['host'])
        print(e)
        db.rollback()
    db.close()
