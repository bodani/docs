# wal 总大小

## 错误描述
在主从复制应用场景中，会遇到一个麻烦事。

```
requested WAL segment 000000020000013F000000E8 has already been removed
```

原因也很简单，就是从库在同步主库的时候，主库的wal日志已经被清理。

之所以麻烦，是因为如果主库的wal没有归档备份，从库只能清空现有数据，重新拉取一份全量。对数据量较大的服务耗时耗力。最好是能尽力避免这样的事情发生。

## 日志保留原则

### 几个重要的参数
- wal_keep_size 默认128MB  ， 版本13 开始 wal_keep_segments参数废弃，取而代之的是wal_keep_size。 wal_keep_size = wal_keep_segments * wal_segment_size (typically 16MB)
- max_wal_size  
- min_wal_size
- max_slot_wal_keep_size

假设pg_wal下的文件为：

```
000000A7000000040000005A
000000A7000000040000005B
000000A7000000040000005C
000000A7000000040000005D
000000A7000000040000005E
000000A7000000040000005F
000000A70000000400000060
000000A70000000400000061
000000A70000000400000062
000000A70000000400000063
000000A70000000400000064
```

假设当前正在写的WAL文件为000000A70000000400000060，则wal_keep_segments控制000000A7000000040000005A到000000A70000000400000060的个数，
而min_wal_size控制000000A70000000400000060到000000A70000000400000064，即这一段至少要保留min_wal_size的WAL日志。

wal 日志的保留主要是由 `min_wal_size + wal_keep_segments` 决定。

### 清理的时机

checkpoint时

实际上参数max_wal_size主要是为了控制checkpoint发生的频繁程度：

target = (double) ConvertToXSegs(max_wal_size_mb) / (2.0 + CheckPointCompletionTarget);

如果checkpoint_completion_target设置为0.5时，则每写了 max_wal_size/2.5 的WAL日志时，就会发送一次checkpoint。

checkpoint_completion_target的范围为0~1，那么结果就是写的WAL的日志量超过: max_wal_size的1/3～1/2时，就会发生一次checkpoint。

## 日志保留策略

过小，容易导致从库wal日志同步时丢失

过大，浪费存储空间。

### 结合slots

复制槽是用来保证逻辑复制或物理复制需要的WAL日志不会被清理掉

避免因slot异常导致wal堆积过多 需要监控 复制槽的状态

```
SELECT slot_name, slot_type, database, xmin,active,active_pid FROM pg_replication_slots ORDER BY age(xmin) DESC;
```

max_slot_wal_keep_size

## 扩展姿势 wal 膨胀预防 

### 长事务

```
select pid,usename, xact_start from pg_stat_activity where now() - xact_start > interval '8 hours';
```

```
select pid,client_addr,usename,datname, xact_start,state from pg_stat_activity where state not in ('active','idle') order by  xact_start;
```



### 两阶段事务

```
SELECT gid, prepared, owner, database, transaction AS xmin
FROM pg_prepared_xacts
ORDER BY age(transaction) DESC;
```

### 主库的WAL日志的归档未成功

https://www.postgresql.org/docs/16/wal-configuration.html