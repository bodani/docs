# 监控指标

## 概述

监控指标 (Metrics) 是对系统性能、运行状态、业务活动等方面的量化度量。通过收集、分析和展示这些指标，可以实现对系统的可观测性，帮助快速发现和解决问题。

## 指标类型

### 1. Counter（计数器）

Counter 是单调递增的指标，其值只能递增或重置为零，不能减少。

**适用场景:**

- 请求总数
- 错误数
- 已处理的任务数

**Prometheus 示例:**

```
# 累计请求总数
http_requests_total{method="GET", path="/users", status="200"} 500
http_requests_total{method="GET", path="/users", status="404"} 12
http_requests_total{method="POST", path="/users", status="201"} 55

# 累计处理的事件数
processed_events_total 834213
```

**使用建议:**

- 记录累积值而不是当前值
- 不适用于可能减小的数值（如当前活跃用户数）

### 2. Gauge（仪表盘）

Gauge 是可以任意增减的指标，反映当前瞬时状态。

**适用场景:**

- 内存使用量
- 当前连接数
- 温度值
- 系统负载

**Prometheus 示例:**

```
# 当前内存使用量（字节）
process_memory_rss_bytes 52428800

# 当前并发连接数
http_connections_current{direction="in"} 23

# 主机负载
node_load1 1.54

# 磁盘使用率（百分比）
disk_usage_percent{device="/dev/sda1", mountpoint="/"} 64.3
```

### 3. Histogram（直方图）

Histogram 记录观测值的分布情况，包含多个 buckets 来统计不同范围内的观测次数。

**适用场景:**

- 请求延迟分布
- 响应时间
- 查询处理时间

**Prometheus 示例:**

```
# API 请求延迟分布（秒）
api_request_duration_seconds_bucket{le="0.005", method="GET", path="/users"} 0
api_request_duration_seconds_bucket{le="0.01", method="GET", path="/users"} 3
api_request_duration_seconds_bucket{le="0.025", method="GET", path="/users"} 7
api_request_duration_seconds_bucket{le="0.05", method="GET", path="/users"} 9
api_request_duration_seconds_bucket{le="0.1", method="GET", path="/users"} 10
api_request_duration_seconds_bucket{le="0.25", method="GET", path="/users"} 10
api_request_duration_seconds_bucket{le="0.5", method="GET", path="/users"} 10
api_request_duration_seconds_bucket{le="1.0", method="GET", path="/users"} 10
api_request_duration_seconds_bucket{le="+Inf", method="GET", path="/users"} 10
api_request_duration_seconds_sum{method="GET", path="/users"} 0.158
api_request_duration_seconds_count{method="GET", path="/users"} 10
```

### 4. Summary（摘要）

Summary 类似 Histogram，提供观测值的统计摘要，如分位数。

**适用场景:**

- 计算 P95/P99 延迟
- 业务指标统计
- 阈值告警

## 系统指标

### CPU 指标

```
# CPU 使用率
node_cpu_usage_percent 73.4
node_cpu_user_seconds_total 23450.32
node_cpu_system_seconds_total 4531.12

# CPU 频率
node_cpu_frequency_hertz 2.4e+09
```

### 内存指标

```
# 内存使用情况
node_memory_MemTotal_bytes 8.589934592e+09
node_memory_MemFree_bytes 1.23865088e+09
node_memory_MemAvailable_bytes 2.567430144e+09
node_memory_MemUsed_percent 70.1
```

### 磁盘指标

```
# 磁盘 I/O
node_disk_read_bytes_total{device="sda"} 1.23e+10
node_disk_written_bytes_total{device="sda"} 2.45e+09
node_disk_io_time_seconds_total{device="sda"} 345.6

# 磁盘空间
node_filesystem_size_bytes{mountpoint="/"} 5.36870912e+10
node_filesystem_avail_bytes{mountpoint="/"} 1.073741824e+10
node_filesystem_usage_percent{mountpoint="/"} 80.0
```

### 网络指标

```
# 网络流量
node_network_receive_bytes_total{device="eth0"} 1.844674407370955e+19
node_network_transmit_bytes_total{device="eth0"} 1.844674407370955e+19

# 网络连接
node_network_tcp_connections 42
node_network_tcp_listen{port="8080"} 1
```

## 应用指标

### HTTP 服务指标

**请求计数器:**

```
# 请求总数，带标签区分方法、路径和状态
http_requests_total{method="GET", path="/api/v1/users", status="200"} 4500
http_requests_total{method="POST", path="/api/v1/users", status="201"} 23
http_requests_total{method="PUT", path="/api/v1/users/123", status="404"} 5
http_requests_total{method="GET", path="/api/v1/users", status="500"} 3
```

**请求时延:**

```
# 延迟直方图
http_request_duration_seconds_bucket{method="GET", le="0.1"} 845
http_request_duration_seconds_bucket{method="GET", le="0.5"} 945
http_request_duration_seconds_bucket{method="GET", le="1.0"} 985
http_request_duration_seconds_sum{method="GET"} 345.67
http_request_duration_seconds_count{method="GET"} 995
```

### 业务指标

**订单处理:**

```
# 订单相关计数器
orders_processed_total 2345
orders_canceled_total 45
orders_failed_total 12

# 订单处理时间
order_processing_duration_seconds_sum 3456.78
order_processing_duration_seconds_count 2345
```

**支付指标:**

```
# 支付成功率
payments_successful_total 1234
payments_failed_total 8
payments_success_rate 0.9936

# 金额相关
payment_amount_total_usd 123456.78
```

## 数据库指标

### MySQL

```
# 连接指标
mysql_global_status_threads_connected 15
mysql_global_status_threads_running 3

# 查询指标
mysql_global_status_queries 2857142
mysql_global_status_com_select 157890
mysql_global_status_com_insert 108234
mysql_global_status_com_update 15678
mysql_global_status_com_delete 4231

# 缓冲池
mysql_global_status_innodb_buffer_pool_pages_total 8192
mysql_global_status_innodb_buffer_pool_pages_free 123
mysql_global_status_innodb_buffer_pool_read_requests 543210
mysql_global_status_innodb_buffer_pool_reads 1234
```

### Redis

```
# 连接指标
redis_connected_clients 23
redis_connected_slaves 2

# 命令执行
redis_commands_processed_total 1234567
redis_commands_total_by_command{command="get"} 789012
redis_commands_total_by_command{command="set"} 345678

# 内存使用
redis_memory_used_bytes 1.2e+07
redis_memory_used_rss_bytes 1.8e+07
redis_memory_peak_bytes 2.1e+07

# 持久化
redis_rdb_changes_since_last_save 1234
redis_rdb_last_save_timestamp_seconds 1633008000
```

## 指标命名规范

### Prometheus 命名约定

1. **命名模式**: `namespace_subsystem_name_unit`
2. **使用下划线分隔**: `http_request_duration_seconds`
3. **明确单位**: `_seconds`, `_bytes`, `_total`
4. **使用英文**: `request_duration_seconds` 而不是 `请求耗时`

### 常用后缀

```
# 计数器常用后缀
_requests_total
_errors_total
_processed_total
_processed_seconds_total  # 对于累积耗时

# 汇总指标
_duration_seconds_sum
_duration_seconds_count
_duration_seconds_bucket

# 仪表盘常用后缀
_current
_in_progress
_usage_percent
_available_bytes
```

## 指标收集最佳实践

### 1. 选择合适的指标类型

- 使用 `Counter` 记录累积值（如请求总数、错误数）
- 使用 `Gauge` 记录当前值（如内存使用、连接数）
- 使用 `Histogram` 或 `Summary` 记录分布（如响应时间）

### 2. 合理设置标签

**好的标签设计:**

```
# 可以用于分组和聚合的有用标签
http_requests_total{method="GET", status="200", handler="/api/users"} 123
```

**需要谨慎使用的标签:**

```
# 可能导致时间序列爆炸的高基数标签
http_requests_total{request_id="uuid123"} # 避免使用
http_requests_total{user_id="123456"} # 可能不必要
```

### 3. 指标粒度控制

- 避免不必要的细节层级
- 平衡监控细节和性能影响
- 定期评审不再使用的指标

## 常用监控指标字典

| 指标名称                        | 类型      | 说明           | 单位                |
| ------------------------------- | --------- | -------------- | ------------------- |
| `http_requests_total`           | Counter   | HTTP 请求总数  | 无                  |
| `http_request_duration_seconds` | Histogram | HTTP 请求耗时  | seconds             |
| `process_cpu_seconds_total`     | Counter   | 进程 CPU 时间  | seconds             |
| `process_resident_memory_bytes` | Gauge     | 进程常驻内存   | bytes               |
| `process_start_time_seconds`    | Gauge     | 进程启动时间   | seconds since epoch |
| `go_goroutines`                 | Gauge     | Goroutine 数量 | 无                  |
| `go_gc_duration_seconds`        | Summary   | GC 停顿时间    | seconds             |

合理的指标体系可以帮助快速定位问题，提高系统可观测性水平。在设计监控指标时，应根据具体场景选择适当的指标类型，并遵循统一的命名规范。
