## mysql 数据库管理

## 安全及权限

### 权限层级

```
在MySQL中，权限可以分为多个层级，包括全局权限、数据库级权限、表级权限、列级权限和例程级权限
```

### 分配的原则

- **最小权限原则**：每个用户只有完成其工作所必需的最小权限集合。
- **按需分配**：根据用户的角色和职责分配权限
- **定期审计**：定期检查用户权限，确保没有不必要的权限遗留。

### 举例

```
-- 只读权限
GRANT SELECT ON mydb.* TO 'data_analyst'@'localhost';

-- 读写权限
GRANT SELECT, INSERT, UPDATE ON mydb.* TO 'app_developer'@'localhost';

-- 数据库管理员需要所有权限
GRANT ALL PRIVILEGES ON mydb.* TO 'db_admin'@'localhost';
```

### 定期审计

```
-- 查看当前所有用户的权限
SELECT * FROM mysql.user\G;

-- 查看特定用户的权限
SHOW GRANTS FOR 'data_analyst'@'localhost';
```

```
-- 回收某个用户的某项权限
REVOKE INSERT ON mydb.* FROM 'app_developer'@'localhost';

-- 删除不再需要的用户账号
DROP USER 'ex_employee'@'localhost';
```

### 数据加密

- 对于敏感字段，如密码、个人信息等，始终使用加密存储。
- 使用强加密算法，如AES。
- 保护好密钥，不要在代码或配置文件中硬编码。

在MySQL中，我们可以使用内置的加密函数来加密数据。

```
-- 假设我们需要存储用户密码
ALTER TABLE user_info ADD COLUMN encrypted_password VARCHAR(255);

-- 使用AES加密用户密码
UPDATE user_info SET encrypted_password = AES_ENCRYPT('password123', 'my_secret_key');
```

### 安全优化Tips

- 使用复杂的密码，并定期更换。
- 不要使用root账户进行日常操作。
- 定期备份数据库，以防万一。

## 性能配置

```
mysqld --verbose --help | grep "Default options" -A 1
```

### 关键配置项

```
「innodb_buffer_pool_size」： InnoDB存储引擎的缓冲池大小，一般建议设置为系统内存的60%-80%
「innodb_log_file_size」： InnoDB的日志文件大小，对于事务的写入有很大影响。如果设置得过小，可能会导致频繁的I/O写入操作
「innodb_flush_log_at_trx_commit」： 控制日志刷新到磁盘的策略。值为1表示每次事务提交都会写入日志，确保数据的安全性，但可能影响性能；值为2或0可以提升性能，但在崩溃时可能丢失数据。
「max_connections」： 允许的最大连接数
「query_cache_size」： 查询缓存的大小 提升读操作的性能。但在高并发写入的场景中，查询缓存可能反而降低性能
「tmp_table_size」 和 「max_heap_table_size」： 决定了临时表的最大大小，如果临时表超过这个大小，它会转换为磁盘上的MyISAM表，影响性能
```

## 备份

逻辑备份，物理备份，热备份，冷备份。clone

这里选用 xtrabackup

```
wget https://downloads.percona.com/downloads/Percona-XtraBackup-8.0/Percona-XtraBackup-8.0.35-30/binary/debian/jammy/x86_64/percona-xtrabackup-80_8.0.35-30-1.jammy_amd64.deb
```

备份设计： on-deman 手动一次触发 sechulder 周期备份。 备份保留策略

```
# 一次全备
xtrabackup --backup --parallel=10 --host=10.10.2.13 --user=root --target-dir=/tmp/full -p
xtrabackup --prepare --use-memory=2G --target-dir=/tmp/full

# 增量备份
xtrabackup --backup --host=10.10.2.13 --user=root --target-dir=/tmp/a/inc1 --incremental-basedir=/tmp/a/ -p

xtrabackup --prepare --apply-log-only --target-dir=/tmp/a  

xtrabackup --prepare --apply-log-only --target-dir=/tmp/a --incremental-dir=/tmp/a/inc1/  

# 压缩备份
xtrabackup --backup  --compress --compress-threads=8 --host=10.10.2.13 --user=root --target-dir=/tmp/c -p

# 流备份
xtrabackup --backup --stream=xbstream --host=10.10.2.13 --user=root --target-dir=/tmp/a -p 2>/data/backup/xtrabackup.log > /tmp/backup0625.xbstream
```



### 数据导出导入

```
--导出表结构
mysqldump -uroot -proot -h192.168.6.10 -P3306 --databases XXX \
--tables XXX --single-transaction \
--hex-blob --no-data --routines --events --triggers --master-data=2 --set-gtid-purged=OFF \
--default-character-set=utf8 | sed -e 's/DEFINER[ ]*=[ ]*[^*]*\*/\*/' \
-e 's/DEFINER[ ]*=.*FUNCTION/FUNCTION/' \
-e 's/DEFINER[ ]*=.*PROCEDURE/PROCEDURE/' \
-e 's/DEFINER[ ]*=.*TRIGGER/TRIGGER/' \
-e 's/DEFINER[ ]*=.*EVENT/EVENT/' \
-e 's/DEFINER[ ]*=.*SQL SECURITY DEFINER/SQL SECURITY DEFINER/' \
> /home/mysql/backup/XXX_ddl.sql

--导出数据,可以带条件  --where="column1=1"
mysqldump -uroot -proot -h192.168.6.10 -P3306 --databases XXX \
--tables XXX \
--single-transaction --hex-blob --no-create-info \
--skip-triggers --master-data=2 \
--default-character-set=utf8 > /home/mysql/backup/XXX_data.sql
```

## 配置

慢查询

 ```
也可以在MySQL命令行中修改参数开启慢查询日志
mysql> SET GLOBAL slow_query_log = 1;
mysql> SET GLOBAL slow_query_log_file = '/data/mysql/log/query_log/slow_statement.log';
mysql> SET GLOBAL long_query_time = 10;
mysql> SET GLOBAL log_output = 'FILE';
连接数
--Connections
# 保持在缓存中的可用连接线程
# default = -1（无）
thread_cache_size = 16
# 最大的连接线程数(关系型数据库)
# default = 151
max_connections = 1000
# 最大的连接线程数(文档型/KV型)
# default = 100
#mysqlx_max_connections = 700

--缓冲区 Buffer
# 缓冲区单位大小；default = 128M
innodb_buffer_pool_size = 128M
# 缓冲区总大小，内存的70%，单位大小的倍数
# default = 128M
innodb_buffer_pool_size = 6G
# 以上两个参数的设定，MySQL会自动改变 innodb_buffer_pool_instances 的值

--I/O 线程数
# 异步I/O子系统
# default = NO
innodb_use_native_aio = NO
# 读数据线程数
# default = 4
innodb_read_io_threads = 32
# 写入数据线程数
# default = 4
innodb_write_io_threads = 32

--Open cache
# default = 5000
open_files_limit = 10000
# 计算公式：MAX((open_files_limit-10-max_connections)/2,400)
# default = 4000
table_open_cache = 4495
# 超过16核的硬件，肯定要增加，以发挥出最大性能
# default = 16
table_open_cache_instances = 32
 ```

binlog 清理

```
## 自动清理
show variables like '%binlog_expire_logs_seconds%'  

mysql8.0
mysql 8开始 expire_logs_days 废弃 ,
启用binlog_expire_logs_seconds设置binlog
自动清除日志时间,保存时间 
以秒为单位；默认2592000 30天
14400   4小时；86400  1天；259200  3天；
mysql> set global binlog_expire_logs_seconds=86400;

## 手动清理
查看日志文件。
mysql>show binary logs;
第二步：查看正在使用的日志文件：show master status;
mysql>show master status;
当前正在使用的日志文件是mysqlhost01-bin.000010，
那么删除日志文件的时候应该排除掉该文件。
删除日志文件的命令：purge binary logs to 'mysqlhost01-bin.000010';
mysql>purge binary logs to 'mysqlhost01-bin.000010';

## 切换日志
flush logs;
```

日志

```
    重做日志（redo log）
    回滚日志（undo log）
    归档日志（binlog）
    错误日志（errorlog）
    慢查询日志（slow query log）
    一般查询日志（general log）
    中继日志（relay log）
```

## 监控

### pmm 

```
mysql 监控管理用户
CREATE USER 'pmm'@'127.0.0.1' IDENTIFIED BY 'pass' WITH MAX_USER_CONNECTIONS 10;
GRANT SELECT, PROCESS, REPLICATION CLIENT, RELOAD, BACKUP_ADMIN ON *.* TO 'pmm'@'127.0.0.1';
```



```
server 端 安装
curl -fsSL https://www.percona.com/get/pmm | /bin/bash
```



```
agent 端 安装
wget https://repo.percona.com/apt/percona-release_latest.generic_all.deb
dpkg -i percona-release_latest.generic_all.deb
apt-get update
apt install -y pmm2-client
apt-get install -y qpress

配置 注册 server
pmm-admin config --server-insecure-tls --server-url=https://admin:admin@10.10.2.14:443
cat /usr/local/percona/pmm2/config/pmm-agent.yaml
pmm-admin  add mysql --query-source=perfschema --host=10.10.2.12 --username=pmm --password=123456789

pmm-admin  add mysql --query-source=slowlog --host=10.10.2.12 --username=pmm --password=123456789

查看
pmm-admin status 
pmm-admin list 

```

# 常用命令

查看当前正在执行的SQL

```
SHOW FULL PROCESSLIST
```

```
show engine innodb status\G
```

