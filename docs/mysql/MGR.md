# 组复制

mysql 8.0 MGR


## 节点规划

- 10.1.2.11
- 10.1.2.12
- 10.1.2.14


## 安装

```
apt-get install mysql-client-8.0 mysql-server-8.0
```

## 用户管理

```
# 本地访问
alter user 'root'@'localhost' identified with mysql_native_password by 'mysql_4U';
# 远端访问
create user 'root'@'%' identified with mysql_native_password by 'mysql_4U';
grant all privileges on *.* to 'root'@'%' with grant option;
flush privileges;
# 复制用户
set sql_log_bin=0;
create user 'repl'@'%' identified by 'repl@12345';
grant replication slave on *.* to 'repl'@'%';
flush privileges;
set sql_log_bin=1;
```

## 配置数据库

`vi /etc/mysql/conf.d/mysql.cnf`

```
[mysqld]
basedir=/usr
datadir=/var/lib/mysql
#修改
server_id=3
socket=/var/lib/mysql/mysql.sock
log-error=/var/lib/mysql/mysqld.log
pid-file=/var/lib/mysql/mysqld.pid

binlog_checksum=NONE
gtid_mode=ON
enforce_gtid_consistency=ON
default_authentication_plugin=mysql_native_password
#loose-group_replication_recovery_get_public_key=on
loose-group_replication_recovery_use_ssl=on
loose-group_replication_group_name="80d51c50-3c11-11ee-bd0f-080027fc0450"
loose-group_replication_start_on_boot=OFF
#修改
loose-group_replication_local_address="10.10.2.11:33061"
loose-group_replication_group_seeds="10.10.2.12:33061,10.10.2.12：33061,10.10.2.13:33061"
loose-group_replication_bootstrap_group=OFF
transaction_write_set_extraction=XXHASH64

[mysql]
prompt="Slave02[\\d]> "
```

重启数据库

```
systemctl restart mysql
```

## 安装插件

```
 INSTALL PLUGIN group_replication SONAME 'group_replication.so';
 INSTALL PLUGIN clone SONAME 'mysql_clone.so';
```

查看插件

```
 show plugins;
```


## 主节点开启组复制

```
 set global group_replication_bootstrap_group=on;
 start group_replication;
 
 select * from performance_schema.replication_group_members;
 set global group_replication_bootstrap_group=off;
```

## 从节点开启组复制

```
reset master;
change master to master_user="repl",master_password="repl@12345" for channel 'group_replication_recovery';
start group_replication;
```

## 查看组复制
```
 select * from performance_schema.replication_group_members;
```

# 手动重启

查看gtid

````
select RECEIVED_TRANSACTION_SET from performance_schema.replication_connection_status where  channel_name = 'group_replication_applier' union all  select variable_value from performance_schema.global_variables where  variable_name = 'gtid_executed';
````

在序号最大的节点上启动引导程序

```
 set global group_replication_bootstrap_group=on;
 start group_replication;
 set global group_replication_bootstrap_group=off;
  
 select * from performance_schema.replication_group_members;
```

其他节点

```
start group_replication;
```

## 错误集

断电后二进制日志损坏,发生在从库

```
start group_replication
[ERROR] [MY-010596] [Repl] Error reading relay log event for channel 'group_replication_applier': corrupted data in log event
2024-01-10T02:58:16.082182Z 94 [ERROR] [MY-013121] [Repl] Replica SQL for channel 'group_replication_applier': Relay log read failure: Could not parse relay log event entry. The possible reasons are: the source's binary log is corrupted (you can check this by running 'mysqlbinlog' on the binary log), the replica's relay log is corrupted (you can check this by running 'mysqlbinlog' on the relay log), a network problem, the server was unable to fetch a keyring key required to open an encrypted relay log file, or a bug in the source's or replica's MySQL code. If you want to check the source's binary log or replica's relay log, you will be able to know their names by issuing 'SHOW REPLICA STATUS' on this replica. Error_code: MY-013121
```

解决
```
reset master 
systemctl restart mysql
start group_replication
```

错误
```
[ERROR] [MY-010605] [Repl] Failed in open_index_file() called from Relay_log_info::rli_init_info().
```
解决
```
/var/lib/mysql# mkdir relaylog
chown mysql:mysql relaylog/
```

group_replication_message_cache_size

group_replication_member_expel_timeout

group_replication_consistency


### 组复制限制。 主键
```
SELECT 
  COUNT(1) AS count 
FROM 
  information_schema.TABLES t1 
  LEFT OUTER JOIN information_schema.columns t2 ON t1.table_schema = t2.TABLE_SCHEMA 
  AND t1.table_name = t2.TABLE_NAME 
  AND t2.COLUMN_KEY = 'PRI' 
WHERE 
  t2.table_name IS NULL 
  AND t1.table_type = 'BASE TABLE' 
  AND t1.TABLE_SCHEMA NOT IN(
    'information_schema', 'performance_schema', 
    'mysql', 'sys'
  );
```