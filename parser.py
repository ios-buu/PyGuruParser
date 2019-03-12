# code=utf-8

import MySQLdb


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

def build_table(data, host, username, password, database):
    # 建立链接
    db = MySQLdb.connect(
        host,
        username,
        password,
        database
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
    # 提取info中的字段如果不存在字段则创建字段
    if data.get('info'):
        for column_name in data['info']:
            if column_name not in static_column_list:
                column_name = column_name.replace('-', '_')
                result = cursor.execute(f'SELECT 1 '
                                        f'FROM INFORMATION_SCHEMA.COLUMNS '
                                        f'WHERE `TABLE_NAME` = "info" '
                                        f'AND `TABLE_SCHEMA` = "api_swagger_source" '
                                        f'AND `COLUMN_NAME` = "{column_name}"')
                if result is 0:
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


def insert(data, host, username, password, database, build=False):
    if build:
        build_table(data, host, username, password, database)
    # 建立链接
    db = MySQLdb.connect(
        host,
        username,
        password,
        database
    )
    # 创建空间
    insert_data = {'domain_key': (data['host'] + data['basePath']).replace('\\', '\\\\')}

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
    # insert时的字段字符串
    column_text = ''
    # insert时的数据字符串
    data_text = ''
    # 更新时的字符串
    update_text = ''
    # 包装sql字符串
    for column_name in insert_data:
        temp_column_name = column_name.replace('-', '_')
        column_text = column_text + f'{temp_column_name},'
        temp_data = str(insert_data[column_name]).replace('"', '\\"').replace("'", "\\'")
        data_text = data_text + f'"{temp_data}",'
        update_text = update_text + temp_column_name + '="'+temp_data+'",'
    # 查询是否存在
    sql = 'SELECT id FROM info WHERE domain_key = "' + insert_data['domain_key'] + '"'
    cursor.execute(sql)
    result = cursor.fetchone()
    # 不存在 -> insert | 存在 -> update
    if not result:
        sql = f'insert into info({column_text[:-1]}) values({data_text[:-1]})'
    else:
        sql = f'update info set {update_text[:-1]} where id={result[0]}'
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except:
        db.rollback()
    db.close()
