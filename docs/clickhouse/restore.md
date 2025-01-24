# 副本节点数据恢复

## 背景

集群模式， 使用的复制表。

故障，其中一个节点的存储盘坏掉。数据完全丢失。

## 恢复流程

- 节点新建clickhouse服务
- 从其他拷贝拷贝 databases 进行恢复databases ,  /var/lib/clickhouse/metadata/.
- 从其他节点拷贝 tables 集进行恢复tables ,  /var/lib/clickhouse/metadata/.
- 从其他节点拷贝 user 进行恢复 user ,  /var/lib/clickhouse/access/.
- 恢复zk 数据 

### 查看集群节点拓扑信息
```
SELECT shard_num, host_address,is_local FROM system.clusters;

  ┌─shard_num─┬─host_address─┬─is_local─┐
1. │         1 │ 10.0.1.174   │        0 │
2. │         1 │ 10.0.0.127   │        0 │
3. │         1 │ 10.0.2.29    │        0 │
4. │         2 │ 10.0.0.54    │        0 │
5. │         2 │ 10.0.2.55    │        0 │
6. │         2 │ 10.0.1.173   │        1 │
   └───────────┴──────────────┴──────────┘
```

确定和故障节点位置。利用同分配的其他节点的数据进行恢复。

查看数据具体分布情况。
```
select database,table,replica_is_active from system.replicas;
```

### 备份恢复数据

metadata 目录中存放的是表结构信息

access 目录中存放的是用户数据

将同分片的其他正常节点的 metadata ， access 数据拷贝到需要恢复节点的对应目录中。

注意事项，metadata 有两类文件，databasename.sql 文件 和 databasename 目录。 databasename.sql 为创建database的语句。  databasename 目录 为创建表的语句。

并且 databasename 目录 为软连接，真实数据存放在 store 中。
```
4 lrwxrwxrwx 1 clickhouse clickhouse 67 Aug 17 12:05 clickstream_v2 -> /var/lib/clickhouse/store/8aa/8aa609f0-
4525-457c-8aa6-09f04525657c/
4 -rw-r----- 1 clickhouse clickhouse 78 Aug 17 12:05 clickstream_v2.sql
4 lrwxrwxrwx 1 clickhouse clickhouse 67 Aug 17 12:05 default -> /var/lib/clickhouse/store/76a/76a4bffa-4625-
46a3-b6a4-bffa4625b6a3/
4 -rw-r----- 1 clickhouse clickhouse 78 Aug 17 12:05 default.sql
4 lrwxrwxrwx 1 clickhouse clickhouse 67 Aug 17 12:05 system -> /var/lib/clickhouse/store/246/246ce236-ada4-42db-
a46c-e236ada4f2db/
4 -rw-r----- 1 clickhouse clickhouse 78 Aug 17 12:05 system.sql
```
拷贝数据需求分两步进行。第一步恢复 access 用户 和 metadata 中的 databasename.sql 。 测试验证 databasename.sql  和 databasename 中的表结构不能同时恢复。

先恢复database，再恢复 tables 。  

```
mkdir /tmp/clickhouse  && cd /tmp/clickhouse
```

### 备份数据 
```
数据
kubectl exec -n <namespaces> <pod> -- tar cvfh - /var/lib/clickhouse/data/metadata | tar xf - -C .
用户
kubectl exec -n <namespaces> <pod> -- tar cvfh - /var/lib/clickhouse/data/access | tar xf - -C .
```


### 恢复数据
```
数据库信息
tar cf - var/lib/clickhouse/data/metadata/*.sql | kubectl exec -i -n <namespaces> <pod> -- tar xkf - -C /
用户信息
tar cf - var/lib/clickhouse/data/access | kubectl exec -i -n <namespaces> <pod> -- tar xf - -C /
zk 数据 
kubectl exec -i -n <namespaces> <pod> -- touch /drycc/clickhouse/data/flags/force_restore_data
```
重启 clickhouse

```
表结构信息
tar cf - --exclude='*.sql' var/lib/clickhouse/data/metadata/ | kubectl exec -i -n <namespaces> <pod> -- tar xkvf - -C /
```
重启 clickhouse


### 注意事项
 在恢复的时候忽略 default,system 这两个database . 因为在创建database 的时候需要 利用on cluster 创建分布式 database。多副本的业务 database 不在default.和system 中， 所以在恢复的时候不需要考虑，default,和system。避免带来不必要的麻烦。

### 验证

[官网恢复手册](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replication#recovery-after-complete-data-loss)

[其它参考1](https://kb.altinity.com/altinity-kb-setup-and-maintenance/recovery-after-complete-data-loss/)

[其它参考2](https://medium.com/@dimakorp/data-rescue-how-we-recovered-clickhouse-after-one-of-three-nodes-failed-f3b81ec65c5)

[其他](https://zhuanlan.zhihu.com/p/702755018)