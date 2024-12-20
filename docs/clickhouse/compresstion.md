# 压缩

列存压缩是CH 高性能的秘诀

## 一个示例, 感官认识

```
create database compresstiondb on cluster cluster;
```

### 不压缩
```
CREATE TABLE none_compression_shard ON CLUSTER cluster
(
    log_time DateTime CODEC(NONE),
    machine_name LowCardinality(String) CODEC(NONE),
    machine_group LowCardinality(String) CODEC(NONE),
    cpu_idle Nullable(Float32) CODEC(NONE),
    cpu_nice Nullable(Float32) CODEC(NONE),
    cpu_system Nullable(Float32) CODEC(NONE),
    cpu_user Nullable(Float32) CODEC(NONE),
    cpu_wio Nullable(Float32) CODEC(NONE),
    disk_free Nullable(Float32) CODEC(NONE),
    disk_total Nullable(Float32) CODEC(NONE),
    part_max_used Nullable(Float32) CODEC(NONE),
    load_fifteen Nullable(Float32) CODEC(NONE),
    load_five Nullable(Float32) CODEC(NONE),
    load_one Nullable(Float32) CODEC(NONE),
    mem_buffers Nullable(Float32) CODEC(NONE),
    mem_cached Nullable(Float32) CODEC(NONE),
    mem_free Nullable(Float32) CODEC(NONE),
    mem_shared Nullable(Float32) CODEC(NONE),
    swap_free Nullable(Float32) CODEC(NONE),
    bytes_in Nullable(Float32) CODEC(NONE),
    bytes_out Nullable(Float32) CODEC(NONE)
) ENGINE = ReplicatedMergeTree()
ORDER BY log_time;

CREATE TABLE none_compression_distributed ON CLUSTER cluster AS none_compression_shard
ENGINE = Distributed(cluster, 'compresstiondb', 'none_compression_shard', rand());
```

### 默认压缩格式
```
分片表（默认压缩格式）

CREATE TABLE default_compression_shard ON CLUSTER cluster
(
    log_time DateTime,
    machine_name LowCardinality(String),
    machine_group LowCardinality(String),
    cpu_idle Nullable(Float32),
    cpu_nice Nullable(Float32),
    cpu_system Nullable(Float32),
    cpu_user Nullable(Float32),
    cpu_wio Nullable(Float32),
    disk_free Nullable(Float32),
    disk_total Nullable(Float32),
    part_max_used Nullable(Float32),
    load_fifteen Nullable(Float32),
    load_five Nullable(Float32),
    load_one Nullable(Float32),
    mem_buffers Nullable(Float32),
    mem_cached Nullable(Float32),
    mem_free Nullable(Float32),
    mem_shared Nullable(Float32),
    swap_free Nullable(Float32),
    bytes_in Nullable(Float32),
    bytes_out Nullable(Float32)
) ENGINE = ReplicatedMergeTree()
ORDER BY log_time;

CREATE TABLE default_compression_distributed ON CLUSTER cluster AS default_compression_shard
ENGINE = Distributed(cluster, 'compresstiondb', 'default_compression_shard', rand());
```

### ZSTD 压缩格式

```
CREATE TABLE zstd_compression_shard ON CLUSTER cluster
(
    log_time DateTime CODEC(ZSTD),
    machine_name LowCardinality(String) CODEC(ZSTD),
    machine_group LowCardinality(String) CODEC(ZSTD),
    cpu_idle Nullable(Float32) CODEC(ZSTD),
    cpu_nice Nullable(Float32) CODEC(ZSTD),
    cpu_system Nullable(Float32) CODEC(ZSTD),
    cpu_user Nullable(Float32) CODEC(ZSTD),
    cpu_wio Nullable(Float32) CODEC(ZSTD),
    disk_free Nullable(Float32) CODEC(ZSTD),
    disk_total Nullable(Float32) CODEC(ZSTD),
    part_max_used Nullable(Float32) CODEC(ZSTD),
    load_fifteen Nullable(Float32) CODEC(ZSTD),
    load_five Nullable(Float32) CODEC(ZSTD),
    load_one Nullable(Float32) CODEC(ZSTD),
    mem_buffers Nullable(Float32) CODEC(ZSTD),
    mem_cached Nullable(Float32) CODEC(ZSTD),
    mem_free Nullable(Float32) CODEC(ZSTD),
    mem_shared Nullable(Float32) CODEC(ZSTD),
    swap_free Nullable(Float32) CODEC(ZSTD),
    bytes_in Nullable(Float32) CODEC(ZSTD),
    bytes_out Nullable(Float32) CODEC(ZSTD)
) ENGINE = ReplicatedMergeTree()
ORDER BY log_time;

CREATE TABLE zstd_compression_distributed ON CLUSTER cluster AS zstd_compression_shard
ENGINE = Distributed(cluster, 'compresstiondb', 'zstd_compression_shard', rand());
```

### ZL4 压缩格式

```
CREATE TABLE lz4_compression_shard ON CLUSTER cluster
(
    log_time DateTime,
    machine_name LowCardinality(String),
    machine_group LowCardinality(String),
    cpu_idle Nullable(Float32),
    cpu_nice Nullable(Float32),
    cpu_system Nullable(Float32),
    cpu_user Nullable(Float32),
    cpu_wio Nullable(Float32),
    disk_free Nullable(Float32),
    disk_total Nullable(Float32),
    part_max_used Nullable(Float32),
    load_fifteen Nullable(Float32),
    load_five Nullable(Float32),
    load_one Nullable(Float32),
    mem_buffers Nullable(Float32),
    mem_cached Nullable(Float32),
    mem_free Nullable(Float32),
    mem_shared Nullable(Float32),
    swap_free Nullable(Float32),
    bytes_in Nullable(Float32),
    bytes_out Nullable(Float32)
) ENGINE = ReplicatedMergeTree()
ORDER BY log_time;

CREATE TABLE lz4_compression_distributed ON CLUSTER cluster AS lz4_compression_shard
ENGINE = Distributed(cluster, 'compresstiondb', 'lz4_compression_shard', rand());
```

### 插入样例数据

```
INSERT INTO none_compression_distributed
SELECT now(), 
       'machine_' || toString(number % 10), 
       'group_' || toString(number % 5),
       rand() % 100, rand() % 100, rand() % 100, rand() % 100, rand() % 100,
       rand() % 1000, rand() % 1000, rand() % 100, rand() % 100,
       rand() % 100, rand() % 100, rand() % 100, rand() % 100,
       rand() % 100, rand() % 100, rand() % 100, rand() % 100,
       rand() % 100
FROM numbers(10000000);

INSERT INTO default_compression_distributed
SELECT now(), 
       'machine_' || toString(number % 10), 
       'group_' || toString(number % 5),
       rand() % 100, rand() % 100, rand() % 100, rand() % 100, rand() % 100,
       rand() % 1000, rand() % 1000, rand() % 100, rand() % 100,
       rand() % 100, rand() % 100, rand() % 100, rand() % 100,
       rand() % 100, rand() % 100, rand() % 100, rand() % 100,
       rand() % 100
FROM numbers(10000000);


INSERT INTO lz4_compression_distributed
SELECT now(), 
       'machine_' || toString(number % 10), 
       'group_' || toString(number % 5),
       rand() % 100, rand() % 100, rand() % 100, rand() % 100, rand() % 100,
       rand() % 1000, rand() % 1000, rand() % 100, rand() % 100,
       rand() % 100, rand() % 100, rand() % 100, rand() % 100,
       rand() % 100, rand() % 100, rand() % 100, rand() % 100,
       rand() % 100
FROM numbers(10000000);

INSERT INTO zstd_compression_distributed
SELECT now(), 
       'machine_' || toString(number % 10), 
       'group_' || toString(number % 5),
       rand() % 100, rand() % 100, rand() % 100, rand() % 100, rand() % 100,
       rand() % 1000, rand() % 1000, rand() % 100, rand() % 100,
       rand() % 100, rand() % 100, rand() % 100, rand() % 100,
       rand() % 100, rand() % 100, rand() % 100, rand() % 100,
       rand() % 100
FROM numbers(10000000);
```

### 查看结果集

```
SELECT
    `table`,
    formatReadableSize(sum(bytes_on_disk)) AS total_size
FROM system.parts
WHERE (database = 'compresstiondb') AND (`table` LIKE '%compression%')
GROUP BY `table`
ORDER BY total_size DESC

Query id: 8f315da9-83f5-4fce-a201-9e653341ce48

   ┌─table─────────────────────┬─total_size─┐
1. │ none_compression_shard    │ 745.91 MiB │
2. │ default_compression_shard │ 417.31 MiB │
3. │ lz4_compression_shard     │ 417.24 MiB │
4. │ zstd_compression_shard    │ 197.74 MiB │
   └───────────────────────────┴────────────┘

```

## 压缩原理

影响压缩的因素

- ordering key
- data types
- codecs 

### 常见编码

#### Delta

特点: 适用于整数和日期时间类型的数据，尤其是连续值之间差异较小的情况。
应用场景: 单调递增或递减的序列，如时间戳、ID。
#### DoubleDelta

特点: 在 Delta 编码基础上进一步压缩，适用于连续的差异本身较小的数据。

应用场景: 二阶差分数据，如股票价格变化。
#### Gorilla

特点: 适用于浮点数数据，特别是具有随机峰值的度量数据。

应用场景: 传感器数据、指标读数。
#### 64

特点: 适用于稀疏数据或小范围数据。

应用场景: 稀疏矩阵、分类数据。


## 压缩算法
```
value	name	description
0x02	None	No compression, only checksums
0x82	LZ4	Extremely fast, good compression
0x90	ZSTD	Zstandard, pretty fast, best compression
```