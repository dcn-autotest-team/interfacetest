# 配置文件撰写说明1.0
## 支持特性        
1 支持通过#和;2种方式添加注释
2 支持ExtendedInterpolation特性(变量替换)
```
[URL]
api = api/v1/login
[SETTINGS]
# 接口访问url -->注释1
base_url = http://192.168.1.1:8082/
request = {base_url}{URL:api}--->变量替换，另外也支持跨section
; 连接数据库配置 -->注释2
config =
        user: dscc  -->字典，目前只支持1层嵌套
        password: dscc
        host: 72.1.1.100
        port: 3306
        database: dscc

# 设置数据库中表的autoincrement值
autoincrement = 6 

```

## 撰写规范
**1** 变量名默认小写（有特殊需求的书写成大写）  
**2** 支持${report_dir_path}的方式引用前面定义的变量，如果跨Section则${REPORT：report_dir_path}  
**3** 如果有嵌套字典则写成如下形式（注意空格）
```config =
        user: dscc ---> :分隔
        password: dscc
        host: 72.1.1.100
        port: 3306
        database: dscc```
                  
