# 监控

## mysql_exporter

- global_status
```
SHOW GLOBAL STATUS;
```

- global_variables
```
SHOW GLOBAL VARIABLES;
```

- info_schema.processlist

`--collect.info_schema.processlist`

```
SELECT
    user,
    SUBSTRING_INDEX(host, ':', 1) AS host,
    COALESCE(command, '') AS command,
    COALESCE(state, '') AS state,
    COUNT(*) AS processes,
    SUM(time) AS seconds
FROM information_schema.processlist
    WHERE ID != connection_id()
    AND TIME >= 0
GROUP BY user, host, command, state;
```

- perf_schema.replication_group_members

`--collect.perf_schema.replication_group_members`
```
SELECT * FROM performance_schema.replication_group_members;
```

- perf_schema.replication_group_member_stats

`--collect.perf_schema.replication_group_member_stats`
```
SELECT * FROM performance_schema.replication_group_member_stats\G;
```
view_id:组成员所在组的视图唯一标识符

member_id:组成员的server uuid,mysql实例启动后生成的唯一标识

COUNT_TRANSACTIONS_IN_QUEUE ：等待冲突验证的队列数量，实际上是进行pipeline处理的队列数量（内部表示m_transactions_waiting_certification），单位为事务数量。

COUNT_TRANSACTIONS_REMOTE_IN_APPLIER_QUEUE：等待应用的队列数量（内部表示m_transactions_waiting_apply），单位为事务数量。

    - informationSchema.processlist
    - performanceSchema.replication_group_members
    - performanceSchema.replication_group_member_stats
    - performanceSchema.replication_applier_status_by_worker
    - auto_increment.columns
    - binlog_size

