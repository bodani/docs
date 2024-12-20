# mysql 日常管理


# 查看Innodb引擎状态，查看上次死锁详情
SHOW ENGINE INNODB STATUS;

# 查看当前 MySQL 执行进程列表
SHOW FULL PROCESSLIST;

# 如果是Mysql 8之前的版本，查看锁信息
SELECT * FROM INFORMATION_SCHEMA.INNODB_LOCKS;
SELECT * FROM INFORMATION_SCHEMA.INNODB_LOCK_WAITS;

# 如果是Mysql 8之后的版本，查看锁信息
select * from performance_schema.data_locks; 
select * from performance_schema.data_lock_waits;

# 如果是Mysql 8 版本之后，一句SQL排查出相关阻塞原因；
select c.SQL_TEXT  from performance_schema.events_statements_current c  inner join  performance_schema.data_lock_waits w ON c.THREAD_ID  = w.BLOCKING_THREAD_ID or c.THREAD_ID  = w.REQUESTING_THREAD_ID 

# 使用SQL判断，最大连接数
show variables like "max_connections";

# 显示 mysql的当前连接数
SHOW STATUS LIKE 'Threads_connected';

# 临时修改mysql配置，重启数据库失效
set GLOBAL max_connections=1000;

# 永久性设置方案
在[mysqld]下面添加：
max_connections=1000