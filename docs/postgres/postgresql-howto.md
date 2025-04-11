# howto 系列

## explain analyze buffers 理解

hit buffers 的具体含义。 不是表面上理解的命中缓存块的数量，而是次数。

## 影响数据库关闭的事件

当数据库执行关闭操作时，需要长时间的处理问题分析

- 长事务
- 内存脏数据
- 未完成的归档，从库延迟wal日志


三种 关闭模式
- Smart  禁止新连接，然后等待所有现有客户端断开连接
- Fast （默认） 不会等待客户端断开连接。所有活动事务都会回滚，客户端会被强制断开连接，然后服务器就会关闭
- Immediate 立即关闭。不执行checkpoint , 在下次重启的时候执行恢复。

## 数据库启动等待过程分析

当数据库启动时间过长，如何分析数据库正在执行情况，在做什么，哪个阶段，还有多久等

日志内容通常如下
```
FATAL: the database system is starting up
```

1 通过进程分析 当前恢复进度
```
ps ax | grep 'startup recovering'
98786   ??  Us     0:15.81 postgres: startup recovering 000000010000004100000018
```

2 pg_controldata -D $PGDATA 查看数据库元数据进行分析

结合数据库恢复量开始、当前已恢复、目标、分析进度
```
select pg_size_pretty(pg_lsn '4A/E0FFE518' - pg_lsn '45/58000000');
```

3 PG15 中引入的 log_startup_progress_interval

## ctid 页地址

了解数据页物理分布，数据稀疏对性能的影响
```
explain select ctid, * from t1 where  ctid = '(1, 12)';
```
