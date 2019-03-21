## 解析guru项目的解析器
### 使用方法
#### 解析单个swagger文件

`python main.py --file=/../swagger.yaml --host=db_host --username=db_username --password=db_password --database=db_name`

#### 批量解析当前目录及其子目录下的所有swagger文件

`python document-parser-starter.py --host=db_host --username=db_username --password=db_password --database=db_name`

#### 文档属性详情拆分

`python attributes-parser-starter.py --host=db_host --username=db_username --password=db_password --database=db_name`
