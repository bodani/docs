# 配置管理

## 启动参数
```
mysqld --verbose --help
```

## 系统运行变量
```
mysql> SHOW VARIABLES;
mysql> SHOW STATUS;
```

##  系统运行变量
```
mysqladmin variables
mysqladmin extended-status
```

## 参数验证
```
mysqld --validate-config --log_error_verbosity=2
```

## 正在执行语句查看
```
 show processlist;
```

## 查看运行状态
```
mysqladmin status -h 10.10.2.11 -pmysql_4U
```

## 日志相关

### 慢查询阈值
```
long_query_time
```

### 日志输出位置 table file none
```
log_output
```

```
general_log
general_log_file
```

```
slow_query_log
slow_query_log_file
```

session 中关闭操作记录

## 错误日志
```
log_error /var/log/mysql/error.log
```


## 二进制日志

```
加密
binlog_encryption

max_binlog_size  
# 日志存储位置 mkdir binlog chmod 700 binlog  chown mysql:mysql -R binlog
log_bin                 = /var/lib/mysql/binlog/mysql-bin.log
relay-log = /var/lib/mysql/relaylog/mysql-relay.log

```

```
binlog_format= ROW #ROW, STATEMENT ,MIXED 
```

## 慢查询
```
slow_query_log_file | /var/lib/mysql/node1-slow.log
```

## 日志管理
日志保留时间默认 30d
```
binlog_expire_logs_auto_purge = ON
binlog_expire_logs_seconds = 2592000 
expire_logs_days
```

## 需要修改的参数

```
# 并发查询数
innodb_thread_concurrency = 0

# redolog size 默认128MB 过小
```


innodb_max_dirty_pages_pct     | 90.000000 |
innodb_max_dirty_pages_pct_lwm | 10.000000 |


## 安全
参数
sql_safe_updates
工具
flashback
mysqlbinlog

## 参数
innodb_dedicated_server
慢日志
