## 维护

etcd 集群需要定期维护才能保持可靠性。etcd 应用程序通常可以自动进行维护，并且不会造成停机或性能大幅下降。

主要通过压缩，空间整理避免空间到达限额 etcd集群进入维护模式影响集群的使用。

### 日志保留
etcd --snapshot-count 配置压缩前内存中保留的应用 Raft 条目的数量， 默认100,1000. 类似checkpoint

高 --snapshot-count 会在快照前在内存中保留更多的 Raft 条目，占用内存多， gc 慢。从库同步快照慢

低 --snapshot-count 磁盘刷新频繁，影响并发

### 空间限额

#### 限额说明
默认空间不是很大2G，可满足大部分应用场景。
当使用空间过大会造成性能下降，当达到阀值时etcd 就会发出全集群警报，使集群进入维护模式，只接受读取和删除。
只有在释放了密钥空间中的足够空间并对后端数据库进行了碎片整理，同时清除了空间配额警报后，集群才能恢复正常运行。

#### 碎片整理
压缩空间后，后端数据库可能会出现内部碎片。压缩旧版本会在后端数据库中留下空隙，从而在内部造成 etcd 碎片。碎片空间可供 etcd 使用，但主机文件系统无法使用。换句话说，删除应用程序数据并不能回收磁盘空间。

碎片整理过程会将这些存储空间释放回文件系统。碎片整理以每个成员为单位进行，这样可以避免整个集群的延迟高峰。

#### 模拟测试

- 配置限额

```
# set a very small 16 MiB quota
$ etcd --quota-backend-bytes=$((16*1024*1024))
```

- 写入数据
```
# fill keyspace
$ while [ 1 ]; do dd if=/dev/urandom bs=1024 count=1024  | ETCDCTL_API=3 etcdctl put key  || break; done
...
Error:  rpc error: code = 8 desc = etcdserver: mvcc: database space exceeded
# confirm quota space is exceeded
$ ETCDCTL_API=3 etcdctl --write-out=table endpoint status
+----------------+------------------+-----------+---------+-----------+-----------+------------+
|    ENDPOINT    |        ID        |  VERSION  | DB SIZE | IS LEADER | RAFT TERM | RAFT INDEX |
+----------------+------------------+-----------+---------+-----------+-----------+------------+
| 127.0.0.1:2379 | bf9071f4639c75cc | 2.3.0+git | 18 MB   | true      |         2 |       3332 |
+----------------+------------------+-----------+---------+-----------+-----------+------------+
# confirm alarm is raised
$ ETCDCTL_API=3 etcdctl alarm list
memberID:13803658152347727308 alarm:NOSPACE
```

- 释放空间
```
# get current revision
$ rev=$(ETCDCTL_API=3 etcdctl --endpoints=:2379 endpoint status --write-out="json" | egrep -o '"revision":[0-9]*' | egrep -o '[0-9].*')
# compact away all old revisions
$ ETCDCTL_API=3 etcdctl compact $rev
compacted revision 1516
# defragment away excessive space
$ ETCDCTL_API=3 etcdctl defrag
Finished defragmenting etcd member[127.0.0.1:2379]
# disarm alarm
$ ETCDCTL_API=3 etcdctl alarm disarm
memberID:13803658152347727308 alarm:NOSPACE
# test puts are allowed again
$ ETCDCTL_API=3 etcdctl put newkey 123
OK
```

- 增加空间限额
```
- --auto-compaction-mode=revision
- --auto-compaction-retention=1000
- --quota-backend-bytes=8589934592

auto-compaction-mode=revision 按版本号压缩
auto-compaction-retention=24 小时
quota-backend-bytes 设置etcd最大容量为8G
```
修改后重启

#### k3s 内置etcd 维护
数据存储位置 `/var/lib/rancher/k3s/server/db/etcd`

```
# alias k3s_etcdctl="ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379   --cert=/var/lib/rancher/k3s/server/tls/etcd/server-client.crt   --key=/var/lib/rancher/k3s/server/tls/etcd/server-client.key   --cacert=/var/lib/rancher/k3s/server/tls/etcd/server-ca.crt"

# k3s_etcdctl endpoint status --write-out=table
+------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|        ENDPOINT        |        ID        | VERSION | DB SIZE | IS LEADER | IS LEARNER | RAFT TERM | RAFT INDEX | RAFT APPLIED INDEX | ERRORS |
+------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
| https://127.0.0.1:2379 | c02555d2c59f97bf |  3.5.13 |   32 MB |     false |      false |        11 |   30427186 |           30427186 |        |
+------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+

# k3s_etcdctl endpoint status --write-out=json | egrep -o '"revision":[0-9]*' | egrep -o '[0-9].*'
27951671

# k3s_etcdctl compact 27951671
compacted revision 27951671

# k3s_etcdctl  endpoint status --write-out=table
+------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|        ENDPOINT        |        ID        | VERSION | DB SIZE | IS LEADER | IS LEARNER | RAFT TERM | RAFT INDEX | RAFT APPLIED INDEX | ERRORS |
+------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
| https://127.0.0.1:2379 | c02555d2c59f97bf |  3.5.13 |   18 MB |     false |      false |        11 |   30431611 |           30431611 |        |
+------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
数据备份
# k3s etcd-snapshot save

/var/lib/rancher/k3s/server/db/etcd/snapshot
```

#### 空间监控


- etcd_mvcc_db_total_size_in_use_in_bytes 实际使用，压缩后的使用量
- etcd_mvcc_db_total_size_in_bytes 实际磁盘占用空间

#### 数据备份

```
$ etcdctl snapshot save backup.db
$ etcdutl --write-out=table snapshot status backup.db
+----------+----------+------------+------------+
|   HASH   | REVISION | TOTAL KEYS | TOTAL SIZE |
+----------+----------+------------+------------+
| fe01cf57 |       10 |          7 | 2.1 MB     |
+----------+----------+------------+------------+
```