# 监控 Exporter

## 概述

Exporter 是用于将其他系统的指标转换为 Prometheus 格式的服务或脚本。它们提供一个 HTTP 端点（通常是 `/metrics`），Prometheus 可以从该端点抓取指标数据。Exporters 使 Prometheus 能够监控原本不支持 Prometheus 协议的系统。

## 常用 Exporter

### 1. Node Exporter

Node Exporter 提供了基本的硬件和操作系统指标。

#### 部署

**二进制方式：**

```bash
# 下载并解压
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
tar -xzf node_exporter-1.6.1.linux-amd64.tar.gz
cd node_exporter-1.6.1.linux-amd64

# 运行
./node_exporter
```

**Docker 方式：**

```bash
docker run -d \
  --name=node-exporter \
  --net="host" \
  --pid="host" \
  -v "/:/host:ro,rslave" \
  quay.io/prometheus/node-exporter:latest \
  --path.rootfs=/host
```

**Systemd 服务文件:**

```ini
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter \
    --collector.systemd \
    --collector.processes \
    --collector.filesystem.ignored-mount-points="^(/(sys|proc|dev|run)($|/))|^(.+\\.(txt|log|pid|sock|socket)$)"

[Install]
WantedBy=multi-user.target
```

#### 核心指标

- `node_cpu_seconds_total`：CPU 使用时间
- `node_memory_MemTotal_bytes`：总内存
- `node_memory_MemFree_bytes`：空闲内存
- `node_disk_reads_completed_total`：磁盘读取次数
- `node_filesystem_size_bytes`：文件系统大小

### 2. MySQL Exporter

MySQL Exporter 收集 MySQL 数据库服务器的指标。

#### 配置

**安装和启动：**

```bash
# 二进制安装
wget https://github.com/prometheus/mysqld_exporter/releases/download/v0.15.0/mysqld_exporter-0.15.0.linux-amd64.tar.gz
tar -xzf mysqld_exporter-0.15.0.linux-amd64.tar.gz
cd mysqld_exporter-0.15.0.linux-amd64
./mysqld_exporter --config.my-cnf=/etc/.my.cnf
```

**数据库配置 (`.my.cnf`):**

```ini
[client]
user = prometheus
password = prometheus_password
host = localhost
```

**Docker 方式:**

```bash
docker run -d \
  --name mysqld-exporter \
  -p 9104:9104 \
  -e DATA_SOURCE_NAME="user:password@(localhost:3306)/" \
  prom/mysqld-exporter
```

#### 重要指标

- `mysql_global_status_queries`：总查询次数
- `mysql_global_status_connections`：连接数
- `mysql_global_status_threads_connected`：当前连接数
- `mysql_global_variables_innodb_buffer_pool_size`：InnoDB 缓冲池大小

### 3. Redis Exporter

Redis Exporter 收集 Redis 服务器指标。

#### 部署

**直接运行:**

```bash
# 安装和启动
docker run -d \
  --name redis-exporter \
  -p 9121:9121 \
  --env REDIS_ADDR=redis://redis_host:6379 \
  oliver006/redis_exporter:latest
```

**系统服务:**

```bash
# 下载二进制文件
wget https://github.com/oliver006/redis_exporter/releases/download/v1.52.0/redis_exporter-v1.52.0.linux-amd64.tar.gz
tar -xzf redis_exporter-v1.52.0.linux-amd64.tar.gz
./redis_exporter --redis.addr=redis://redis_host:6379
```

### 4. Blackbox Exporter

用于黑盒探测，可以检查 HTTP、HTTPS、DNS、TCP、ICMP 等服务的可用性。

#### 配置

**基本配置 (`blackbox.yml`):**

```yaml
modules:
  http_2xx:
    prober: http
    timeout: 5s
    http:
      method: GET
      no_follow_redirects: false
      fail_if_ssl: false
      fail_if_not_ssl: false

  http_post_2xx:
    prober: http
    http:
      method: POST
      headers:
        Content-Type: application/json
      body: {}

  tcp_connect:
    prober: tcp
    timeout: 5s
```

**启动命令:**

```bash
docker run -d \
  --name blackbox-exporter \
  -p 9115:9115 \
  -v $(pwd)/blackbox.yml:/config/blackbox.yml \
  prom/blackbox-exporter:latest \
  --config.file=/config/blackbox.yml
```

### 5. JMX Exporter

用于收集 Java 应用的 JMX 指标，需要作为 Java agent 嵌入应用中。

**Java 启动参数:**

```bash
java -javaagent:/path/to/jmx_prometheus_httpserver.jar=9404:/path/to/config.yaml YourJavaApp
```

## 高级配置

### 认证和安全

```yaml
# 用于配置 exporter 的认证信息
scrape_configs:
  - job_name: "mysql"
    static_configs:
      - targets: ["localhost:9104"]
    basic_auth:
      username: "prometheus"
      password: "secret_password"
```

### 指标重命名和标签处理

```yaml
scrape_configs:
  - job_name: "node"
    static_configs:
      - targets: ["localhost:9100"]
    metric_relabel_configs:
      # 重命名指标
      - source_labels: [__name__]
        regex: "node_disk_(.+)"
        target_label: job
        replacement: "node:disk"
      # 过滤特定标签值
      - source_labels: [mountpoint]
        regex: "/(sys|proc|dev|run)"
        action: drop
```

## 开发自定义 Exporter

### Python Exporter 示例

```python
from prometheus_client import start_http_server, Counter
from prometheus_client.core import GaugeMetricFamily, REGISTRY
import time
import random

class CustomCollector(object):
    def collect(self):
        gauge = GaugeMetricFamily("custom_temperature_celsius", 'Temperature in Celsius', labels=['location'])
        gauge.add_metric(['server_room'], random.uniform(15, 30))
        gauge.add_metric(['outside'], random.uniform(0, 40))
        yield gauge

if __name__ == '__main__':
    REGISTRY.register(CustomCollector())
    start_http_server(8000)
    while True:
        time.sleep(1)
```

### 关键开发要点

1. 遵循 Prometheus 指标命名规范 (snake_case)
2. 添加适当的描述性标签
3. 提供有意义的指标描述
4. 为指标提供合适的类型 (Counter, Gauge, Histogram, Summary)
5. 正确实现指标的生命周期管理

## 最佳实践

1. **安全性**: 配置适当的认证和授权
2. **性能**: 合理设置抓取间隔，避免过度监控
3. **可扩展性**: 在高负载情况下使用服务发现
4. **稳定性**: 实施健康检查和告警
5. **文档**: 维护详细的指标字典和用途说明

Exporter 是整个监控生态的重要一环，它们使 Prometheus 能够监控广泛的系统。正确部署和配置 Exporter 是构建全面可观测性解决方案的关键步骤。
