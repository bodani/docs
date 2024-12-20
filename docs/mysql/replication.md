# 主从复制

## Binary Log File Position Based Replication 

- source 主库
- replica 从库

支持根据需求复制指定dbs或tables, 注意在replica端设置

### 前期准备

```
server_id #  unique ID
## 以下与主从相关的默认值
log_bin= ON
innodb_flush_log_at_trx_commit=1
sync_binlog=1
skip_networking=OFF

## replica 级联复制
log_replica_updates=ON
log_slave_updates=ON 
```

### 复制用户

复制用户需要权限 `REPLICATION SLAVE`

提示: 复制用户密码会明文存放在 mysql.slave_master_info 中。

```
mysql> CREATE USER 'repl'@'%.example.com' IDENTIFIED BY 'password';
mysql> GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%.example.com';
```

提示: caching_sha2_password 默认加密方式，需要加密方式连接。

### File Position

source 
```
-- 禁止写入
mysql>  FLUSH TABLES WITH READ LOCK;
-- 获取位置信息
mysql> SHOW MASTER STATUS\G
```

### 拷贝数据

如果source 中有数据
- mysqldump
- clone
- xtrabackup

https://www.modb.pro/db/49521

### 配置主从

```
mysql> UNLOCK TABLES;
```

```
mysql> CHANGE MASTER TO
    ->     MASTER_HOST='source_host_name',
    ->     MASTER_USER='replication_user_name',
    ->     MASTER_PASSWORD='replication_password',
    ->     MASTER_LOG_FILE='recorded_log_file_name',
    ->     MASTER_LOG_POS=recorded_log_position;

Or from MySQL 8.0.23:
mysql> CHANGE REPLICATION SOURCE TO
    ->     SOURCE_HOST='source_host_name',
    ->     SOURCE_USER='replication_user_name',
    ->     SOURCE_PASSWORD='replication_password',
    ->     SOURCE_LOG_FILE='recorded_log_file_name',
    ->     SOURCE_LOG_POS=recorded_log_position;
```

注意事项: event_scheduler


skip_slave_start

```
select * from  mysql.slave_relay_log_info\G;
```

```
select * from mysql.slave_master_info\G;
```
## 基于 gtid

```
server_id 
```

```
log_bin=ON
binlog_format=ROW
gtid_mode=ON
enforce-gtid-consistency=ON
log_slave_updates
super_read_on=on

````

mysql_native_password

```
CREATE USER 'replica_user'@'%' IDENTIFIED BY 'replica_user';
GRANT REPLICATION SLAVE ON *.* TO 'replica_user'@'%'
```

clone 

```
CHANGE MASTER TO MASTER_HOST = 10.1.40.84, MASTER_PORT = 3306, MASTER_USER = , MASTER_PASSWORD = password, MASTER_AUTO_POSITION = 1;
Or from MySQL 8.0.22:
CHANGE REPLICATION SOURCE TO SOURCE_HOST = '10.1.40.84', SOURCE_PORT = 3306,SOURCE_USER = 'replica_user',SOURCE_PASSWORD = 'replica_user', SOURCE_AUTO_POSITION = 1;
```

```
mysql> START SLAVE;
Or from MySQL 8.0.22:
mysql> START REPLICA;
```

主从切换

reset relaylog


过滤备份新增数据库 
https://mp.weixin.qq.com/s/VnTrFfgiXBzl07CrczyMGQ