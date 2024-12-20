# 配置管理

## 查看配置文件位置
```
mysql --verbose --help | grep -A 1 'Default options'
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

### 慢查询
```
long_query_time # 日志阀值（秒）
log_queries_not_using_indexes # 记录没走索引的sql
log_throttle_queries_not_using_indexes # 每秒中记录没走索引的sql数量，防止过多。默认0
```
https://ma.ttias.be/mysql-slow-query-log-without-restart/

```
slow_query_log=ON
slow_query_log_file='/var/lib/mysql/node1-slow.log'
log_output='FLIE'
```
mysqldumpslow 慢查询显示格式工具

### 日志输出位置 table file none
log_output='TABLE' # 将慢日志输入到Table中。

```
SELECT 
    start_time,
    user_host,
    query_time,
    lock_time,
    rows_sent,
    rows_examined,
    db,
    last_insert_id,
    insert_id,
    server_id,
    CONVERT(sql_text USING utf8mb4) AS sql_text,
    thread_id
FROM 
    mysql.slow_log\G
```
### 通用日志 
```
general_log=OFF
general_log_file
```
session 中关闭操作记录

### 错误日志
```
log_error=/var/log/mysql/error.log
log_error_verbosity=2 
log-warnings：是否将警告信息输出到错误日志中。
log_warnings 为0， 表示不记录告警信息。
log_warnings 为1， 表示告警信息写入错误日志。log_warnings 大于1， 表示各类告警信息，例如：有关网络故障的信息和重新连接信息写入
错误日志
```

### 二进制日志

```
加密
binlog_encryption=OFF

max_binlog_size=1073741824 # 设置单个binlog文件的最大大小为1GB
# 日志存储位置 mkdir binlog chmod 700 binlog  chown mysql:mysql -R binlog
log_bin=ON
log_bin_basename=/var/lib/mysql/binlog/mysql-bin.log
log_bin_index=/var/lib/mysql/binlog/mysql-bin.index
sql_log_bin=ON # 当sql_log_bin关闭后,主库服务器上的改动不记录bin log,不会复制到从库
```
```
binlog_format= ROW #ROW, STATEMENT ,MIXED 
```
日志保留时间默认 30d
```
binlog_expire_logs_auto_purge = ON
binlog_expire_logs_seconds = 2592000 
expire_logs_days=0 # 参数已失效
```

查看日志文件
show binary logs;
show master logs;

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

### innodb 参数

#### innodb_dedicated_server
根据探测服务器内存自动配置 通常会占用50%~75%的内存. 25% 内存可用于每个连接。
```
innodb_dedicated_server # 自动适配如下参数

innodb_buffer_pool_size=134217728 (128MB)
innodb_log_file_size=50331648 (48MB)
innodb_log_files_in_group=2 
innodb_redo_log_capacity=104857600
innodb_flush_method=fsync
```

官方给出的规则如下：

| 服务器内存大小           | buffer_pool_size大小            |
|-----------------------|-----------------------------|
| 一档  | Less than 1GB            | 128MB (the default value)     |
| 二档  | 1GB to 4GB               | detected server memory * 0.5  |
| 三挡  | Greater than 4GB         | detected server memory * 0.75 |

比较激进
#### innodb_buffer_pool_size

总内存的50%-60%

关联参数

- innodb_buffer_pool_instances= cpu核数*N
- innodb_buffer_pool_chunk_size=128MB
- innodb_buffer_pool_size=innodb_buffer_pool_instances * innodb_buffer_pool_chunk_size * N

```
SELECT @@innodb_buffer_pool_size as pool_size,
    -> @@innodb_buffer_pool_instances as pool_instances,
    -> @@innodb_buffer_pool_chunk_size as chunk_size;
```

#### innodb_flush_method

- fsync
- O_DSYNC
- O_DIRECT

#### innodb_file_per_table

独立表空间 

如果启用了innodb_file_per_talbe参数，需要注意的是每张表的表空间内存放的只是数据、索引和插入缓冲Bitmap页，其他数据如：回滚信息、插入缓冲索引页、系统事物信息、二次写缓冲（Double write buffer）等还是放在原来的共享表空间内。同时说明了一个问题：即使启用了innodb_file_per_table参数共享表空间还是会不断的增加其大小的。

#### innodb_flush_log_at_trx_commit

通常我们说MySQL的“双1”配置，指的就是sync_binlog和
innodb_flush_log_at_trx_commit都设置成 1
```
sync_binlog=1
innodb_flush_log_at_trx_commit=1
```
#### innodb_redo_log_capacity
redo log 大小
```
innodb_log_file_size=50331648 (48MB)  # 旧版参数已失效
innodb_log_files_in_group=2       # 旧版参数已失效
innodb_redo_log_capacity # 8.0.30 新参数。 设置这个参数后前面的两个失效
```
当前所有活跃redo log的状态
```
SELECT * FROM performance_schema.innodb_redo_log_files;
show global status like '%innodb%redo%';
```
https://www.cnblogs.com/greatsql/p/16883835.html

redo log存储在 datadir/#innodb_redo下，由32个文件组成。文件命名为 #ib_redoN**，每个文件大小是 innodb_redo_log_capacity/32

有两种类型的redo log文件，一种是当前正在使用的（ordinary），文件名是正常的 #ib_redoN；另一种是空闲的（spare），文件名为 #ib_redoN_tmp，多加了个 _tmp 后缀。

```
#innodb_redo$ ls -l
total 102400
-rw-r----- 1 1001 1001 3276800 Nov 11 03:30 '#ib_redo199'
-rw-r----- 1 1001 1001 3276800 Nov 11 07:32 '#ib_redo200'
-rw-r----- 1 1001 1001 3276800 Nov 11 11:35 '#ib_redo201'
-rw-r----- 1 1001 1001 3276800 Nov 11 15:38 '#ib_redo202'
-rw-r----- 1 1001 1001 3276800 Nov 11 19:38 '#ib_redo203'
-rw-r----- 1 1001 1001 3276800 Nov 11 23:38 '#ib_redo204'
-rw-r----- 1 1001 1001 3276800 Nov 12 03:40 '#ib_redo205'
-rw-r----- 1 1001 1001 3276800 Nov 12 07:39 '#ib_redo206'
-rw-r----- 1 1001 1001 3276800 Nov 12 08:00 '#ib_redo207'
-rw-r----- 1 1001 1001 3276800 Nov 11 01:40 '#ib_redo208_tmp'
-rw-r----- 1 1001 1001 3276800 Nov 11 01:40 '#ib_redo209_tmp'
-rw-r----- 1 1001 1001 3276800 Nov 11 01:40 '#ib_redo210_tmp'
```


