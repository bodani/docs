# Grafana 监控可视化

## 概述

Grafana 是一个开源的度量分析和可视化套件，可以将各种时序数据库（如 Prometheus、InfluxDB、Elasticsearch 等）中的数据进行图形化展示。其强大的仪表板功能使得指标监控变得直观易懂。

## 安装和配置

### 1. 安装 Grafana

#### Ubuntu/Debian 系统：

```bash
# 使用APT仓库安装（推荐方式）
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana

# 启动 Grafana 服务
sudo systemctl daemon-reload
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

#### CentOS/RHEL 系统：

```bash
# 添加 YUM repository
sudo tee -a /etc/yum.repos.d/grafana.repo <<EOF
[grafana]
name=grafana
baseurl=https://packages.grafana.com/oss/rpm
repo_gpgcheck=1
enabled=1
gpgcheck=1
gpgkey=https://packages.grafana.com/gpg.key
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt
EOF

# 安装并启动
sudo dnf install grafana
sudo systemctl daemon-reload
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

#### Docker 安装方式：

```bash
# 运行最新版 Grafana
docker run -d -p 3000:3000 --name=grafana grafana/grafana-enterprise

# 持久化数据的运行方式
docker run -d \
  -p 3000:3000 \
  --name=grafana \
  -v grafana-storage:/var/lib/grafana \
  grafana/grafana-enterprise
```

### 2. 基础配置

#### 访问 Grafana Web 界面

默认访问地址: `http://localhost:3000`
默认用户名/密码: `admin/admin`

首次登录会被强制修改密码。

#### 常用配置选项

配置文件位于 `/etc/grafana/grafana.ini`：

```ini
[server]
# 基础配置
http_addr = 0.0.0.0
http_port = 3000
domain = localhost

[security]
# 管理员密码 (首次运行时)
admin_user = admin
admin_password = your_secure_password

[database]
# Grafana 自身数据库 (支持 SQLite3, MySQL, PostgreSQL)
type = sqlite3
path = grafana.db

[auth.anonymous]
# 启用匿名访问
enabled = false

[users]
# 新用户注册
allow_sign_up = false
auto_assign_org_role = Viewer
```

## 数据源配置

### 1. 配置 Prometheus 数据源

访问路径：Configuration → Data Sources → Add data source → Prometheus

基本配置项：

```json
{
  "name": "Prometheus",
  "type": "prometheus",
  "url": "http://localhost:9090",
  "access": "proxy",
  "basicAuth": false,
  "isDefault": true
}
```

高级配置：

- HTTP Access: proxy（代理模式，更安全）
- Scrape interval: 数据采集间隔
- Custom query params: 自定义查询参数

### 2. 其他数据源

Grafana 还支持许多其他数据源：

- InfluxDB
- Elasticsearch
- Graphite
- MySQL / PostgreSQL
- AWS CloudWatch
- Azure Monitor

## 仪表板创建与管理

### 1. 仪表板创建

创建新仪表板的方式：

1. 点击侧边栏 + 图标 → Dashboard
2. 通过导入预设面板：Dashboard → Import
3. 使用 Grafana 社区面板 ID 或 JSON 配置

### 2. 面板配置

每个面板的基本组成：

- Query Editor: 定义从数据源获取数据的方式
- Visualization: 面板显示样式（图表、数值、文本等）
- Panel Options: 样式和交互配置

#### 基础面板类型：

**Graph Panel (图表面板)**

- 时序曲线图
- 包含多系列数据对比
- 支持各种统计函数

**SingleStat Panel (数值面板)**

- 显示单个聚合数值
- 可配置阈值和颜色
- 展示当前状态

**Table Panel (表格面板)**

- 以表格形式展示数据
- 可排序和筛选
- 支持多种列格式

### 3. 查询编辑

使用 Prometheus 查询语法进行数据提取：

```promql
# 简单计数查询
prometheus_http_requests_total

# 使用聚合函数
sum by (method) (prometheus_http_requests_total)

# 计算增长率
increase(prometheus_http_requests_total[5m])

# 5分钟移动平均
rate(prometheus_http_requests_total[5m])
```

## 变量和模板化

### 1. 定义模板变量

路径：Dashboard Settings → Variables

常用变量类型：

```bash
# 查询变量（Query）: 从数据源动态获取选项
Label names
Label values

# 自定义变量 (Custom): 手动输入固定选项
us-east-1, us-west-1, us-west-2

# 文本框 (Text box): 手动输入值
```

### 2. 使用变量

在查询中使用变量：

```
# 使用变量替换
node_cpu_seconds_total{job="$job", instance="$instance"}
```

### 3. 变量配置示例

```
Name: "job"
Type: Query
Data Source: Prometheus
Query: label_values(job)
Regex: (?!node_exporter_service_discovery)()
Refresh: On Dashboard Load
```

## 告警配置

### 1. 创建告警规则

在 Grafana 8.0+ 中，告警通过 Alerting 菜单配置。

告警查询配置：

```promql
# CPU 使用率 > 80%
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
```

告警条件：

- Evaluate every: 评估频率
- For: 持续时间阈值
- Condition: 查询条件表达式

### 2. 通知渠道

通知渠道类型：

- Email
- Slack
- PagerDuty
- Webhook
- Discord

通知模板包含：

- Alert name
- Firing alerts
- Rule info
- Dashboard & panel links

## 最佳实践

### 1. 面板设计最佳实践

**层次结构**

- 高度概括在上方（系统状态）
- 详细指标在下方（组件细节）
- 告警信息显眼位置

**颜色使用**

- 告警色：红色 (错误)、黄色 (警告)、绿色 (正常)
- 保持颜色含义一致

### 2. 性能优化

- 限制时间范围避免加载过多数据
- 使用适当的采样频率
- 控制面板数量 (推荐单页少于 12 个面板)
- 启用缓存功能

### 3. 告警策略

- 避免过度告警，关注真正重要的指标
- 使用合适的评估间隔，避免频繁抖动
- 实现有效的告警分级 (Warning/Critical)
- 定义清晰的告警接收流程

## 高级功能

### 1. 管理和用户权限

Grafana 支持角色基础访问控制 (RBAC)：

- Admin: 完全权限
- Editor: 编辑权限
- Viewer: 只读权限

### 2. 快照功能

- 共享实时数据状态
- 设置到期时间
- 限制访问（受保护的快照）

### 3. 报告功能

定时发送 PNG 或 PDF 格式的仪表板报告

- 设置报告间隔
- 选择仪表板和时间范围
- 自定义收件人

Grafana 是目前主流的监控可视化解决方案之一，与其他监控系统组合使用可以实现完善的可观测性体系。在企业部署时，需要注意安全配置，包括认证、权限控制和网络访问限制等。
