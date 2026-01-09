# Prometheus 监控系统

## 概述

Prometheus 是一个开源的系统监控和报警工具包，最初由 SoundCloud 开发，现由 Cloud Native Computing Foundation(CNCF) 维护。它通过拉取（Pull）模型和时间序列数据库（TSDB）来收集和存储指标数据。

## 核心组件

### 1. Prometheus Server

- **Retrieval**：从各个目标收集指标
- **Storage**：存储时间序列数据
- **Query Language**：PromQL 查询语言
- **Rule evaluation**：评估警报规则

### 2. Exporters

将现有程序包装成支持 Prometheus 指标的格式，如：

- node_exporter：服务器指标
- mysqld_exporter：MySQL 指标
- redis_exporter：Redis 指标

### 3. Alertmanager

处理警报的分组、去重、静默和抑制，支持多种通知渠道。

### 4. Pushgateway

允许临时任务推送其指标，这些任务通常不会持续暴露给 Prometheus 拉取。

## 安装和配置

### 1. 安装 Prometheus

```bash
# 创建 prometheus 用户
sudo useradd --no-create-home --shell /bin/false prometheus

# 创建必要目录
sudo mkdir -p /etc/prometheus
sudo mkdir -p /var/lib/prometheus

# 设置所有权
sudo chown prometheus:prometheus /etc/prometheus
sudo chown prometheus:prometheus /var/lib/prometheus

# 下载并解压 Prometheus
cd /tmp
wget https://github.com/prometheus/prometheus/releases/download/v2.40.0/prometheus-2.40.0.linux-amd64.tar.gz
tar -xvf prometheus-2.40.0.linux-amd64.tar.gz

# 进入解压后的目录
cd prometheus-2.40.0.linux-amd64

# 移动二进制文件
sudo cp prometheus /usr/local/bin/
sudo cp promtool /usr/local/bin/

# 设置所有者为 prometheus 用户
sudo chown prometheus:prometheus /usr/local/bin/prometheus
sudo chown prometheus:prometheus /usr/local/bin/promtool

# 复制配置文件和配置目录
sudo cp -r consoles /etc/prometheus
sudo cp -r console_libraries /etc/prometheus
sudo chown -R prometheus:prometheus /etc/prometheus/consoles
sudo chown -R prometheus:prometheus /etc/prometheus/console_libraries
```

### 2. Prometheus 配置文件

创建主配置文件 `/etc/prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s # 设置全局默认抓取间隔
  evaluation_interval: 15s # 规则评估间隔

# 规则文件路径
rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

# 目标列表
scrape_configs:
  # 监控 prometheus 本身
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

  # 监控节点
  - job_name: "node"
    static_configs:
      - targets: ["localhost:9100"]

  # 监控服务
  - job_name: "service"
    static_configs:
      - targets: ["localhost:8080", "localhost:8081"]

  # 动态服务发现
  - job_name: "services-kubernetes"
    kubernetes_sd_configs:
      - api_server: null
        role: pod
        kubeconfig_file: ""
        tls_config:
          ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
          insecure_skip_verify: true
        bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels:
          [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          # - "alertmanager:9093"
```

### 3. 创建 Systemd 服务

创建文件 `/etc/systemd/system/prometheus.service`:

```ini
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

StartLimitIntervalSec=500
StartLimitBurst=5

[Service]
Type=simple
Restart=on-failure
RestartSec=5s

User=prometheus
Group=prometheus
ExecStart=/usr/local/bin/prometheus \
    --config.file=/etc/prometheus/prometheus.yml \
    --storage.tsdb.path=/var/lib/prometheus/ \
    --web.console.templates=/etc/prometheus/consoles \
    --web.console.libraries=/etc/prometheus/console_libraries \
    --web.listen-address=0.0.0.0:9090 \
    --storage.tsdb.retention.time=200h \
    --web.enable-lifecycle

[Install]
WantedBy=multi-user.target
```

### 4. 启动 Prometheus

```bash
# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启动 Prometheus 服务
sudo systemctl start prometheus

# 验证 Prometheus 是否正在运行
sudo systemctl status prometheus

# 设置 Prometheus 在启动时自动运行
sudo systemctl enable prometheus
```

## 常用 Exporters

### Node Exporter（服务器指标）

```bash
# 创建用户
sudo useradd --no-create-home --shell /bin/false node_exporter

# 下载 node_exporter
cd /tmp
wget https://github.com/prometheus/node_exporter/releases/download/v1.4.0/node_exporter-1.4.0.linux-amd64.tar.gz
tar -xzf node_exporter-1.40.0.linux-amd64.tar.gz

# 复制二进制文件
sudo cp node_exporter-1.4.0.linux-amd64/node_exporter /usr/local/bin
sudo chown node_exporter:node_exporter /usr/local/bin/node_exporter

# 创建 systemd 服务文件
sudo nano /etc/systemd/system/node_exporter.service
```

```ini
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl start node_exporter
sudo systemctl enable node_exporter
```

## 告警规则配置

### 示例告警规则（`rules.yml`）

```yaml
groups:
  - name: example
    rules:
      # 指标超过阈值
      - alert: HighCpuUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected on {{ $labels.instance }}"
          description: "{{ $labels.instance }} has had high CPU usage (> 80%) for the last 2 minutes."

      # 服务宕机
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.instance }} is down"
          description: "{{ $labels.job }} job {{ $labels.instance }} has been down for more than 1 minute."

      # 内存使用率过高
      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemFree_bytes) / node_memory_MemTotal_bytes * 100 > 90
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "{{ $labels.instance }} has had high memory usage (> 90%) for the last 2 minutes."
```

## Prometheus 查询语言（PromQL）

### 基本查询示例

```promql
# 瞬时向量选择器
up                           # 检查所有被监控的目标的up状态

# 区间向量选择器
rate(http_requests_total[5m]) # 计算过去5分钟内的请求速率

# 聚合操作
sum(cpu_usage_percent)        # 所有CPU使用百分比的总和
avg(cpu_usage_percent)        # 所有CPU使用百分比的平均值
max_over_time(up[1h])         # 过去1小时内UP的最大值
```

## 最佳实践

### 配置最佳实践

1. 合理设置抓取间隔以减少服务器压力
2. 正确设置标签来标识实例和作业
3. 对于短暂任务使用 Pushgateway
4. 适当地配置规则和告警
5. 使用 relabeling 功能过滤或转换标签

### 性能优化建议

1. 合理配置保留策略避免存储过度增长
2. 使用高效的标签模式避免标签爆炸
3. 在告警规则中使用 `for` 子句减少抖动
4. 谨慎设置聚合函数的使用，特别是在高基数数据上

## 监控可视化

Prometheus 通常与其他工具配合使用进行可视化，如 Grafana，可以用来展示收集的指标。Prometheus 还自带一个简单的内置表达式浏览器，可以通过 http://YOUR_SERVER_IP:9090/graph 访问。
