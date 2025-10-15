# 关于时序数据库的一个示例-用户访问统计分析

## 需求分析

- 用户访问信息表包括：  访问时间,用户ID ,年龄 ,设备类型 ('手机', '电脑'),访问来源 (如：'搜索引擎', '直接访问')， 用户所在省份， 用户类型 (如: '新用户', '老用户')
- 超表粒度： 每小时
- 统计分析： 五分钟， 小时， 天，周
- 分析类型： 五分钟 ，小时为实时分析 。 天，周，持续聚合
- 更新策略： 五分钟-跨度 5-30 分钟，频率5分钟。 小时-跨度 1 - 2 小时，频率1小时 。 天 - 每天凌晨一点统计，周每周一凌晨两点统计。
- 数据保留： 超表 一天， 视图一个月

## SQL

### 表结构
```
-- 启用TimescaleDB扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 创建用户访问记录表
CREATE TABLE user_visits (
    time TIMESTAMPTZ NOT NULL,      -- 访问时间
    user_id INT,                    -- 用户ID
    age INT CHECK (age BETWEEN 1 AND 100),  -- 年龄
    device VARCHAR(10) CHECK (device IN ('手机', '电脑')),  -- 设备类型
    source VARCHAR(20),             -- 访问来源 (如: '搜索引擎', '直接访问')
    province VARCHAR(20),           -- 用户所在省份
    user_type VARCHAR(10)           -- 用户类型 (如: '新用户', '老用户')
);
-- 转换为超表，按小时分块
SELECT create_hypertable(
    'user_visits',
    'time',
    chunk_time_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);
```
### 视图
```
-- 创建视图
-- 五分钟聚合
CREATE MATERIALIZED VIEW visits_5min
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('5 minutes', time) AS bucket,
    province,
    device,
    COUNT(*) AS visit_count
FROM user_visits
GROUP BY bucket, province, device;

-- 开启实时聚合
ALTER MATERIALIZED VIEW visits_5min set (timescaledb.materialized_only = false);

-- 小时聚合
CREATE MATERIALIZED VIEW visits_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour'::interval, bucket) as bucket,
    province,
    device,
    SUM(visit_count) AS visit_count 
FROM visits_5min
GROUP BY 1, 2, 3;


-- 开启实时聚合
ALTER MATERIALIZED VIEW visits_hourly set (timescaledb.materialized_only = false);

-- 天聚合
CREATE MATERIALIZED VIEW visits_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', bucket) AS bucket,
    province,
    device,
    SUM(visit_count) AS visit_count
FROM visits_hourly
GROUP BY 1, 2, 3;

-- 周聚合
CREATE MATERIALIZED VIEW visits_weekly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 week', bucket) AS bucket,
    province,
    device,
    SUM(visit_count) AS visit_count
FROM visits_daily
GROUP BY 1, 2, 3;
```
### 刷新策略
```
-- 5分钟聚合：延迟5分钟刷新
SELECT add_continuous_aggregate_policy(
    'visits_5min',
    start_offset => INTERVAL '15 minutes',
    end_offset => INTERVAL '5 minutes',
    schedule_interval => INTERVAL '5 minutes'
);

-- 小时聚合：延迟1小时刷新
SELECT add_continuous_aggregate_policy(
    'visits_hourly',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour'
);

-- 天/周聚合：每天凌晨刷新
SELECT add_continuous_aggregate_policy(
    'visits_daily',
    start_offset => INTERVAL '25 days',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '24 hours',
    initial_start => '2023-01-01 01:00:00'
);

SELECT add_continuous_aggregate_policy(
    'visits_weekly',
    start_offset => INTERVAL '8 days',     -- 确保覆盖完整周+1天缓冲
    end_offset => INTERVAL '1 day',        -- 当前时间-1天=周日午夜
    schedule_interval => INTERVAL '1 week', -- 每周执行一次
    initial_start => '2023-01-02 01:00:00+08' -- 指定周日凌晨1点执行（带时区）
);
```
### 压缩策略
```
-- 压缩策略：1天前的数据转为列存
ALTER TABLE user_visits SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'province, device',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy(
    'user_visits',
    compress_after => INTERVAL '1 day'
);

-- 数据保留策略：超表保留7天，物化视图保留30天
SELECT add_retention_policy('user_visits', INTERVAL '7 days');
SELECT add_retention_policy('visits_5min', INTERVAL '30 days');
SELECT add_retention_policy('visits_hourly', INTERVAL '30 days');
SELECT add_retention_policy('visits_daily', INTERVAL '30 days');
SELECT add_retention_policy('visits_weekly', INTERVAL '30 days');
```

手动刷新策略
```
call refresh_continuous_aggregate('visits_5min',);

SELECT refresh_continuous_aggregate('visits_hourly');

SELECT refresh_continuous_aggregate('visits_daily','2025-03-30 17:00:00+08','2025-04-30 17:00:00+08'); 
```