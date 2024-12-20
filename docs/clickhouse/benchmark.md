# 压力测试

## clickhouse-benchmark
```
-- 查看集群名称
show clusters;
-- 创建db
CREATE DATABASE dbbenchmark ON CLUSTER cluster

use dbbenchmark
-- 创建本地表
CREATE TABLE dbbenchmark.test_table_local  ON CLUSTER cluster (
    id UInt64,
    name String,
    value Float64,
    timestamp DateTime
) ENGINE = ReplicatedMergeTree()
ORDER BY id;
-- 创建分布表
CREATE TABLE test_table_distributed  ON CLUSTER cluster ENGINE = Distributed('cluster', 'dbbenchmark', 'test_table_local', rand());
-- 生成测试数据
INSERT INTO dbbenchmark.test_table_distributed SELECT 
    number AS id, 
    concat('name_', toString(number)) AS name, 
    rand() % 100 AS value, 
    now() - INTERVAL rand() % 10000 SECOND AS timestamp 
FROM numbers(1000000);

-- 简单压测

clickhouse-benchmark --query "SELECT count(*) FROM test_table_distributed WHERE value > 50"


clickhouse-benchmark --query "SELECT avg(value) FROM test_table_distributed WHERE timestamp > now() - INTERVAL 1 HOUR"

clickhouse-benchmark --query "SELECT * FROM dbbenchmark.test_table_distributed ORDER BY value DESC LIMIT 100"
```

## 查看表大小
```
SELECT
    table,
    formatReadableSize(sum(bytes_on_disk)) AS total_size
FROM system.parts
WHERE database = 'mgbench'
GROUP BY table
ORDER BY total_size DESC;
```
```
SELECT
    `table`,
    active,
    formatReadableSize(sum(bytes_on_disk)) AS total_size,
    count() AS parts_count
FROM system.parts
WHERE database = 'mgbench'
GROUP BY
    `table`,
    active
ORDER BY total_size DESC
```

```
SELECT
    name AS table,
    formatReadableSize(total_bytes) AS total_size
FROM system.tables
WHERE database = 'mgbench'
ORDER BY total_size DESC;
```

