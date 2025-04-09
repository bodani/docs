# victoriametrics

```markdown
# VictoriaMetrics

VictoriaMetrics is a high-performance, cost-effective monitoring solution and time series database. It is designed to collect, store, and visualize metrics from various sources such as Prometheus exporters, logs, and traces. Here are some key features of VictoriaMetrics:

## 组件

vmagent - lightweight agent for receiving metrics via pull-based and push-based protocols, transforming and sending them to the configured Prometheus-compatible remote storage systems such as VictoriaMetrics.
vmalert - a service for processing Prometheus-compatible alerting and recording rules.
vmalert-tool - a tool for validating alerting and recording rules.
vmauth - authorization proxy and load balancer optimized for VictoriaMetrics products.
vmgateway - authorization proxy with per-tenant rate limiting capabilities.
vmctl - a tool for migrating and copying data between different storage systems for metrics.
vmbackup, vmrestore and vmbackupmanager - tools for creating backups and restoring from backups for VictoriaMetrics data.
vminsert, vmselect and vmstorage - components of VictoriaMetrics cluster.
VictoriaLogs - user-friendly cost-efficient database for logs.

## 结合 prometheus
prometheus 版本 v2.12.0+ 内存增加 ~25%

```
remote_write:
  - url: http://<victoriametrics-addr>:8428/api/v1/write
    queue_config:
      max_samples_per_send: 10000
      capacity: 20000
      max_shards: 30
```yaml

## 部署集群

insert replicationFactor=2

select -dedup.minScrapeInterval

storage -dedup.minScrapeInterval

storage
--promscrape.config=/etc/victoriametrics-promscrape.yml
		--retentionPeriod=30d
		--storageDataPath=/srv/victoriametrics/data
		--httpListenAddr=127.0.0.1:9090
		--search.disableCache=true
		--search.maxQueryLen=1MB
		--search.latencyOffset=5s
		--search.maxUniqueTimeseries=100000000
		--search.maxSamplesPerQuery=1500000000
		--search.maxQueueDuration=30s
		--search.logSlowQueryDuration=30s
		--search.maxQueryDuration=90s
		--promscrape.streamParse=true
		--prometheusDataPath=/srv/prometheus/data
		--http.pathPrefix=/prometheus
		--envflag.enable
		--envflag.prefix=VM_

vmagent 

-remoteWrite.tmpDataPath
集群
http://10.1.72:8429/insert/0/prometheus/api/v1/write
单机
http://10.1.72:8429/api/v1/write

## 权限验证

## 验证集群

## 查看集群状态，监控
http://10.1.40.72:8429/select/0/vmui
# 端口

vmstorage	8482	HTTP	管理API端口（/health、/metrics）
8400	TCP	接收来自vminsert的写入数据
8401	UDP	接收来自vminsert的写入数据（可选）
8480	TCP	集群节点间通信端口
vminsert	8480	HTTP	管理API端口
8400	TCP	接收写入请求（Prometheus remote_write）
vmselect	8481	HTTP	管理API端口
8401	TCP	接收查询请求（Prometheus query）
vmagent	8429	HTTP	默认抓取/metrics端口
单机版	8428	HTTP	默认数据接收/查询端口

### vmagent 是否替代 Prometheus 进行抓取和写入

### vmauth 
进行访问验证，负载均衡. 替代前面的nginx 
port 8427


openssl rand -hex 32


-httpAuth.username
-httpAuth.password
```markdown
### VMCluster Architecture Overview

The provided configuration and details describe the setup of a VictoriaMetrics (VM) cluster, which is a high-performance, cost-effective monitoring solution. Below is an organized breakdown of the key components, configurations, and functionalities.

---

#### **1. Configuration Parameters**```markdown
