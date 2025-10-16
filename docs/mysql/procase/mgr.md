# 组复制降级

## 从库日志

2025-10-15T05:32:35.796578-00:00 15 [ERROR] [MY-010584] [Repl] Replica SQL for channel 'group_replication_applier': Worker 1 failed executing transaction '928237fa-a63a-11f0-9468-ca3f25023d79:248969'; Could not execute Update_rows event on table xxx; Can't find record in 'xxx', Error_code: 1032; handler error HA_ERR_KEY_NOT_FOUND, Error_code: MY-001032
2025-10-15T05:32:35.796755-00:00 14 [Warning] [MY-010584] [Repl] Replica SQL for channel 'group_replication_applier': ... The replica coordinator and worker threads are stopped, possibly leaving data in inconsistent state. A restart should restore consistency automatically, although using non-transactional storage for data or info tables or DDL queries could lead to problems. In such cases you have to examine your data (see documentation for details). Error_code: MY-001756
2025-10-15T05:32:35.796826-00:00 14 [ERROR] [MY-011451] [Repl] Plugin group_replication reported: 'The applier thread execution was aborted. Unable to process more transactions, this member will now leave the group.'
2025-10-15T05:32:35.796924-00:00 12 [ERROR] [MY-011452] [Repl] Plugin group_replication reported: 'Fatal error during execution on the Applier process of Group Replication. The server will now leave the group.'
2025-10-15T05:32:35.797160-00:00 12 [ERROR] [MY-011712] [Repl] Plugin group_replication reported: 'The server was automatically set into read only mode after an error was detected.'
2025-10-15T05:32:35.797290-00:00 12 [System] [MY-011565] [Repl] Plugin group_replication reported: 'Setting super_read_only=ON.'
2025-10-15T05:32:41.560786-00:00 0 [System] [MY-011504] [Repl] Plugin group_replication reported: 'Group membership changed: This member has left the group.'

## 主库日志

2025-10-15T05:32:36.986976-00:00 0 [Warning] [MY-011499] [Repl] Plugin group_replication reported: 'Members removed from the group: mgr-2:3306, mgr-1:3306'
2025-10-15T05:32:36.987107-00:00 0 [System] [MY-011503] [Repl] Plugin group_replication reported: 'Group membership changed to mgr-0:3306 on view 17601430949724618:8.'

## 主库 binlog 日志

mysqlbinlog --no-defaults --base64-output=decode-rows --include-gtids='928237fa-a63a-11f0-9468-ca3f25023d79:248969' mysql-bin.000003 > /tmp/fatal_transaction1.sql

grep -A 15 "alert_dispose_rule_config" /tmp/fatal_transaction1.sql

## 分析

错误提示，在更新的时候从库没有对应的记录。查看，主从数据库表，发现数据不一致。 进一步查看主库日志。 发现只有创建表和发生错误时的更新记录。没有数据插入记录。

根本原因。在数据插入的时候缺失 binlog 记录。

引起这种情况的原因。
