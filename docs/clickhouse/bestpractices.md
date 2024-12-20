# 最佳实践

## 批量插入

一次插入多条数据1W~10W, 减少与服务器交互的频率。

### 异步插入

- async_insert 0，默认 同步，1 开启异步 
- async_insert_max_data_size , size 维度
- async_insert_busy_timeout_ms , 时间维度

- wait_for_async_insert= 0 插入缓存后返回,1 刷盘后返回
#### 开启异步的方式
##### 用户级别
```
ALTER USER default SETTINGS async_insert = 1
```
##### 语句级别
```
INSERT INTO YourTable SETTINGS async_insert=1, wait_for_async_insert=1 VALUES (...)
```

##### 连接串方式
```
"jdbc:ch://HOST.clickhouse.cloud:8443/?user=default&password=PASSWORD&ssl=true&custom_http_params=async_insert=1,wait_for_async_insert=1"
```

强烈建议 async_insert=1,wait_for_async_insert=1  同时设置。

### Buffer Table

```
Buffer(database, table, num_layers, min_time, max_time, min_rows, max_rows, min_bytes, max_bytes [,flush_time [,flush_rows [,flush_bytes]]])
```
示例
```
-- 目标表
CREATE TABLE target_table
(
    id UInt64,
    value String
) ENGINE = MergeTree()
ORDER BY id;

-- 缓冲表
CREATE TABLE buffer_table
(
    id UInt64,
    value String
) ENGINE = Buffer('default', 'target_table', 16, 10, 60, 100000, 1000000, 1048576);
```

### 更新和删除

尽量避免 MergeTree 表引擎中进行更新个删除数据。可能引起全表重写风险。使用 ReplacingMergeTree 或 CollapsingMergeTree 实现

### 避免 Nullable 列

### Optimize Final 

导致 parts 重写合并 ，并忽略 max_bytes_to_merge_at_max_space_in_pool  设置。 造成大量IO，类似 vacumn full

### 分区键选择