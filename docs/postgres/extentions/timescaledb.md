# 时序数据库

## 安装与配置
https://docs.timescale.com/self-hosted/latest/install/installation-linux/#supported-platforms

### 利用 timescaledb-tune 进行优化

需要额外安装

### 手动修改配置

可参考 https://pgtune.leopard.in.ua/

#### Memory
- shared_buffers
- effective_cache_size
- work_mem
- maintenance_work_mem
- max_connections

#### Works
- timescaledb.max_background_workers
- max_parallel_workers
- max_worker_processes

#### disk-writes

- synchronous_commit = off
- fsync = on

## 超表

### 创建超表

基础表
```
CREATE TABLE conditions (
   time        TIMESTAMPTZ       NOT NULL,
   location    TEXT              NOT NULL,
   device      TEXT              NOT NULL,
   temperature DOUBLE PRECISION  NULL,
   humidity    DOUBLE PRECISION  NULL
);
```
加入数据
```
INSERT INTO conditions (time, location, device, temperature, humidity)
SELECT
  NOW() - interval '1 hour' * random(),
  'LOC-' || (1 + floor(random() * 5))::text,
  'DEV-' || (1 + floor(random() * 3))::text,
  (random() * 40 + 10)::numeric(5,2),
  (random() * 70 + 30)::numeric(5,2)
FROM generate_series(1, 10)
\watch
```
创建超表
```
-- 默认，conditions 无数据, 分区范围l 1 week
SELECT create_hypertable('conditions', by_range('time'));
-- 已有历史数据
SELECT create_hypertable('conditions', by_range('time'), migrate_data=>true);

-- 在创建超表时指定 分区范围
SELECT create_hypertable('conditions', by_range('time', INTERVAL '1 day'));
-- 更改现有分区范围
SELECT set_chunk_time_interval('conditions', INTERVAL '24 hours');
-- 查看分区范围
SELECT *   FROM timescaledb_information.dimensions  WHERE hypertable_name = 'conditions';
```
分区表的时间跨度， chunk_time_interval 。建议每个分区表大小为总内存的25%。

### Chunk Skipping 

加速查询性能
```
-- 查看当前值
SHOW timescaledb.enable_chunk_skipping;

-- 临时启用（会话级）
SET timescaledb.enable_chunk_skipping = on;

-- 永久启用（需修改 postgresql.conf）
ALTER SYSTEM SET timescaledb.enable_chunk_skipping = on;
SELECT pg_reload_conf();

SELECT enable_chunk_skipping('conditions', 'time')
```
```
-- 启用压缩，并指定分段（SEGMENTED）和排序（ORDER BY）规则
ALTER TABLE conditions SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'device, location',  -- 按设备、位置分组压缩
    timescaledb.compress_orderby = 'time DESC'            -- 按时间倒序排列
);
-- 添加压缩策略
SELECT add_compression_policy('conditions', compress_after => INTERVAL '12 hours');
-- 查看压缩
SELECT * FROM timescaledb_information.compression_settings WHERE hypertable_name = 'conditions';
```

## Hypercore
Hypercore 是 Hypertable 使用的 TimescaleDB 混合行列式存储引擎

热数据行存，随着数据的冷却变为列存。行存有利于数据的修改。列存更有利于数据的分析。

```
-- 在超表中启用列存 segmentby 常用于筛选数据的列
ALTER TABLE conditions SET (
   timescaledb.enable_columnstore = true, 
   timescaledb.segmentby = 'device');
-- 持续聚合
ALTER MATERIALIZED VIEW assets_candlestick_daily set (
   timescaledb.enable_columnstore = true, 
   timescaledb.segmentby = 'symbol' );
-- 加入策略
CALL add_columnstore_policy('conditions', after => INTERVAL '1d');
-- 查看策略
SELECT * FROM timescaledb_information.jobs WHERE proc_name='policy_compression';
-- 查看压缩结果
SELECT pg_size_pretty(before_compression_total_bytes) as before, pg_size_pretty(after_compression_total_bytes) as after FROM hypertable_compression_stats('conditions');
-- 暂停策略
SELECT alter_job(JOB_ID, scheduled => false);
-- 恢复策略
SELECT alter_job(JOB_ID, scheduled => true);
-- 删除策略
CALL remove_columnstore_policy('conditions');
-- 禁用策略
ALTER TABLE conditions ticks SET (timescaledb.enable_columnstore = false);
```
## 持续集成

```
-- 创建持续集成,持续集成是构建在hypertable之上的, time_bucket 必须为hypertable的dimension列。
CREATE MATERIALIZED VIEW conditions_summary_daily
WITH (timescaledb.continuous) AS
SELECT device,
   time_bucket(INTERVAL '1 day', time) AS bucket,
   AVG(temperature),
   MAX(temperature),
   MIN(temperature)
FROM conditions
GROUP BY device, bucket;

-- 创建持续集成策略
SELECT add_continuous_aggregate_policy('conditions_summary_daily',
  start_offset => INTERVAL '1 month',
  end_offset => INTERVAL '1 day',
  schedule_interval => INTERVAL '1 hour');
```

选择分步，创建持续集成。 超表如何历史数据量较大。在创建持续集成视图的时候可能很耗时。可以先创建一张空的持续集成表。之后手动触发更新视图
```
-- 用 WITH NO DATA 创建没有数据的视图
CREATE MATERIALIZED VIEW cagg_rides_view
WITH (timescaledb.continuous) AS
SELECT vendor_id,
time_bucket('1h', pickup_datetime) AS hour,
  count(*) total_rides,
  avg(fare_amount) avg_fare,
  max(trip_distance) as max_trip_distance,
  min(trip_distance) as min_trip_distance
FROM rides
GROUP BY vendor_id, time_bucket('1h', pickup_datetime)
WITH NO DATA;

-- 手动更新历史数据
CALL refresh_continuous_aggregate('cagg_rides_view', NULL, localtimestamp - INTERVAL '1 week');

-- 加入策略
SELECT add_continuous_aggregate_policy('cagg_rides_view',
  start_offset => INTERVAL '1 week',
  end_offset   => INTERVAL '1 hour',
  schedule_interval => INTERVAL '30 minutes');
```

## 分层持续聚合

层级设计
```
-- 小时级持续聚合（启用实时）
CREATE MATERIALIZED VIEW cagg_hourly
WITH (timescaledb.continuous, timescaledb.materialized_only = false) AS
SELECT time_bucket('1 hour', time) AS bucket, avg(value) 
FROM sensor_data 
GROUP BY bucket;
-- 天级持续聚合（启用实时）
CREATE MATERIALIZED VIEW cagg_daily
WITH (timescaledb.continuous, timescaledb.materialized_only = false) AS
SELECT time_bucket('1 day', bucket) AS bucket, avg(avg) 
FROM cagg_hourly 
GROUP BY bucket;
-- 月级持续聚合（禁用实时）
CREATE MATERIALIZED VIEW cagg_monthly
WITH (timescaledb.continuous, timescaledb.materialized_only = true) AS
SELECT time_bucket('1 month', bucket) AS bucket, avg(avg) 
FROM cagg_daily 
GROUP BY bucket;
-- 年级持续聚合（禁用实时）
CREATE MATERIALIZED VIEW cagg_yearly
WITH (timescaledb.continuous, timescaledb.materialized_only = true) AS
SELECT time_bucket('1 year', bucket) AS bucket, avg(avg) 
FROM cagg_monthly 
GROUP BY bucket;
-- 小时级持续聚合：每10分钟刷新最新数据
SELECT add_continuous_aggregate_policy('cagg_hourly', 
  start_offset => INTERVAL '7 days', 
  end_offset => INTERVAL '10 minutes',
  schedule_interval => INTERVAL '10 minutes');
-- 天级持续聚合：每天刷新一次
SELECT add_continuous_aggregate_policy('cagg_daily', 
  start_offset => INTERVAL '3 months', 
  end_offset => INTERVAL '1 day',
  schedule_interval => INTERVAL '1 day');
-- 月级持续聚合：每月初刷新
SELECT add_continuous_aggregate_policy('cagg_monthly', 
  start_offset => INTERVAL '1000 years', -- 覆盖所有历史数据
  end_offset => INTERVAL '1 month',
  schedule_interval => INTERVAL '1 month');
-- 年级持续聚合：每年初刷新
SELECT add_continuous_aggregate_policy('cagg_yearly', 
  start_offset => INTERVAL '1000 years', 
  end_offset => INTERVAL '1 year',
  schedule_interval => INTERVAL '1 year');
```

###  查询自动路由
```
- 查询最近1小时（使用小时级持续聚合 + 实时数据）
SELECT * FROM cagg_hourly WHERE bucket > NOW() - INTERVAL '1 hour';
-- 查询最近1年（使用年级持续聚合，仅物化数据）
SELECT * FROM cagg_yearly WHERE bucket > '2022-01-01';
```
### 跨层实时查询
```
-- 结合年级物化数据与月级实时数据（假设月级启用实时）
SELECT bucket, avg FROM cagg_yearly
WHERE bucket < '2023-01-01'
UNION ALL
SELECT time_bucket('1 year', bucket) AS bucket, avg(avg)
FROM cagg_monthly 
WHERE bucket >= '2023-01-01'
GROUP BY bucket;
```
### 实时聚合
```
实时聚合结果包括 持续聚合和最新数据两部分。
-- 关闭实时聚合
ALTER MATERIALIZED VIEW table_name set (timescaledb.materialized_only = true);
-- 开启实时聚合
ALTER MATERIALIZED VIEW table_name set (timescaledb.materialized_only = false);
```
实时聚合注意事项： wathermark 概念。

https://docs.timescale.com/use-timescale/latest/continuous-aggregates/troubleshooting/
### 聚合压缩
如何聚合中的数据不在变化。可通过压缩进一步优化
```
-- 开启压缩
ALTER MATERIALIZED VIEW cagg_name set (timescaledb.compress = true);
结合策略进行压缩处理
-- 策略
SELECT add_continuous_aggregate_policy('cagg_name',
  start_offset => INTERVAL '30 days',
  end_offset => INTERVAL '1 day',
  schedule_interval => INTERVAL '1 hour');
-- 压缩历史数据
SELECT add_compression_policy('cagg_name', compress_after=>'45 days'::interval);
```

## 数据保留策略
```
-- 添加数据保留策略
SELECT add_retention_policy('conditions', INTERVAL '24 hours');

-- 删除数据保留策略
SELECT remove_retention_policy('conditions');

-- 查看数据保留策略
SELECT j.hypertable_name,
       j.job_id,
       config,
       schedule_interval,
       job_status,
       last_run_status,
       last_run_started_at,
       js.next_start,
       total_runs,
       total_successes,
       total_failures
  FROM timescaledb_information.jobs j
  JOIN timescaledb_information.job_stats js
    ON j.job_id = js.job_id
  WHERE j.proc_name = 'policy_retention';
```
## 注意事项

实时聚合是实时结果与持续聚合的结果集，划分数据是实时还是持续聚合的分界线为水位线。

水位线为每次刷新持续聚合的时候向前推进，当手动刷新持续聚合视图的时候避免将水位线更新到未来的时间。 否则实时聚合失去实时性。直到当前时间到达水位线。

```
CALL refresh_continuous_aggregate('your_view', '时间窗口开始时间', '时间窗口结束时间'，'boolean 是否重新计算');
```
boolean 是否重新计算为true, 如果超表数据被删除，或根据策略已过期。视图数据也将被清空。
### 查看水位线
```
SELECT id FROM _timescaledb_catalog.hypertable
    WHERE table_name=(
        SELECT materialization_hypertable_name
            FROM timescaledb_information.continuous_aggregates
            WHERE view_name='<continuous_aggregate_name>'
    );

SELECT COALESCE(
    _timescaledb_functions.to_timestamp(_timescaledb_functions.cagg_watermark(<ID>)),
    '-infinity'::timestamp with time zone
);
```
### 

刷新历史数据。

## 维护

### 查看超表大小
```
SELECT hypertable_name, hypertable_size(format('%I.%I', hypertable_schema, hypertable_name)::regclass)
  FROM timescaledb_information.hypertables;
```

### 查看超表大小,包括索引等
```
SELECT 
    hypertable_name,
    (hypertable_detailed_size(format('%I.%I', hypertable_schema, hypertable_name)::regclass)).*
FROM 
    timescaledb_information.hypertables;
```