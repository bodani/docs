# ClickHouse 集群版安装

## 概述

ClickHouse 集群版提供高可用性和水平扩展能力，适用于大规模数据分析场景。本指南介绍如何搭建一个多节点 ClickHouse 集群。

## 集群架构

### 组件构成

- **ClickHouse Server**：存储数据并执行查询
- **ZooKeeper**：提供分布式协调服务，维护集群状态一致性
- **负载均衡器**：如 Nginx 或 HAProxy，处理写入请求分发

### 分片和副本

- **分片(Sharding)**：将数据分布到多个节点，提高存储和查询能力
- **副本(Replication)**：在同一分片中创建多个副本，保证高可用性

## 环境准备

### 1. 服务器要求

准备 3-6 台服务器（可根据需求调整）:

```
ch-node1 : 192.168.1.10 (shard1, replica1)
ch-node2 : 192.168.1.11 (shard1, replica2)
ch-node3 : 192.168.1.12 (shard2, replica1)
ch-node4 : 192.168.1.13 (shard2, replica2)
zk-node1 : 192.168.1.20
zk-node2 : 192.168.1.21
zk-node3 : 192.168.1.22
```

### 2. 网络和防火墙配置

```bash
# 所有节点开启必要端口
sudo ufw allow 9000    # TCP client interface
sudo ufw allow 8123    # HTTP interface
sudo ufw allow 9009    # Inter-server communication
sudo ufw allow 2181    # ZooKeeper client port
```

## ZooKeeper 安装与配置

### 1. 在每台 ZooKeeper 服务器上安装

```bash
# 在每个 zk 节点上安装 ZooKeeper
sudo apt-get install -y zookeeperd

# 或者手动安装 ZooKeeper
wget https://archive.apache.org/dist/zookeeper/zookeeper-3.8.1/apache-zookeeper-3.8.1-bin.tar.gz
tar -xzvf apache-zookeeper-3.8.1-bin.tar.gz
mv apache-zookeeper-3.8.1-bin /opt/zookeeper
```

### 2. 配置 ZooKeeper 集群

修改 `/etc/zookeeper/conf/zoo.cfg`:

```properties
tickTime=2000
initLimit=5
syncLimit=2
clientPort=2181

server.1=zk-node1:2888:3888
server.2=zk-node2:2888:3888
server.3=zk-node3:2888:3888
```

每个服务器上分别创建 `myid` 文件:

```bash
# zk-node1: echo 1 > /etc/zookeeper/conf/myid
# zk-node2: echo 2 > /etc/zookeeper/conf/myid
# zk-node3: echo 3 > /etc/zookeeper/conf/myid
```

### 3. 启动 ZooKeeper

```bash
sudo systemctl restart zookeeper
sudo systemctl enable zookeeper

# 验证集群状态
echo stat | nc zk-node1 2181 | grep Mode
```

## ClickHouse 集群配置

### 1. 在所有节点安装 ClickHouse

```bash
# 所有节点执行相同安装命令
curl -s https://packagecloud.io/install/repositories/altinity/clickhouse/script.deb.sh | sudo bash
sudo apt-get install -y clickhouse-server clickhouse-client
```

### 2. 配置 ZooKeeper 集成

修改所有 ClickHouse 节点的 `/etc/clickhouse-server/config.xml`:

```xml
<zookeeper>
    <node index="1">
        <host>zk-node1</host>
        <port>2181</port>
    </node>
    <node index="2">
        <host>zk-node2</host>
        <port>2181</port>
    </node>
    <node index="3">
        <host>zk-node3</host>
        <port>2181</port>
    </node>
</zookeeper>

<distributed_ddl>
    <!-- 配置分布式 DDL 执行策略 -->
    <path>/clickhouse/task_queue/ddl</path>
</distributed_ddl>
```

### 3. 配置集群宏变量

在每台服务器上的 `/etc/clickhouse-server/config.d/macros.xml`:

```xml
<!-- ch-node1: -->
<yandex>
    <macros>
        <shard>01</shard>
        <replica>ch-node1</replica>
    </macros>
</yandex>
```

```xml
<!-- ch-node2: -->
<yandex>
    <macros>
        <shard>01</shard>
        <replica>ch-node2</replica>
    </macros>
</yandex>
```

```xml
<!-- ch-node3: -->
<yandex>
    <macros>
        <shard>02</shard>
        <replica>ch-node3</replica>
    </macros>
</yandex>
```

```xml
<!-- ch-node4: -->
<yandex>
    <macros>
        <shard>02</shard>
        <replica>ch-node4</replica>
    </macros>
</yandex>
```

### 4. 配置集群信息

在所有节点的 `/etc/clickhouse-server/config.d/cluster.xml`:

```xml
<yandex>
    <remote_servers>
        <production_cluster>
            <shard>
                <internal_replication>true</internal_replication>
                <replica>
                    <host>ch-node1</host>
                    <port>9000</port>
                    <user>default</user>
                    <password></password>
                </replica>
                <replica>
                    <host>ch-node2</host>
                    <port>9000</port>
                    <user>default</user>
                    <password></password>
                </replica>
            </shard>
            <shard>
                <internal_replication>true</internal_replication>
                <replica>
                    <host>ch-node3</host>
                    <port>9000</port>
                    <user>default</user>
                    <password></password>
                </replica>
                <replica>
                    <host>ch-node4</host>
                    <port>9000</port>
                    <user>default</user>
                    <password></password>
                </replica>
            </shard>
        </production_cluster>
    </remote_servers>
</yandex>
```

## 部署与启动

### 1. 启动 ClickHouse 服务

在所有 ClickHouse 节点执行:

```bash
sudo systemctl start clickhouse-server
sudo systemctl enable clickhouse-server

# 验证启动状态
sudo systemctl status clickhouse-server
```

### 2. 验证集群配置

```sql
-- 在任意节点连接测试
clickhouse-client

-- 检查集群配置
SELECT * FROM system.clusters;

-- 检查复制状态
SELECT * FROM system.replicas;

-- 查看副本同步状态
SELECT database, table, is_leader, is_readonly, future_parts, parts_to_check
FROM system.replicas;
```

## 创建集群表

### 1. 创建复制表

在每个分片节点上执行相同的建表语句:

```sql
-- 创建本地复制表
CREATE TABLE events_local ON CLUSTER production_cluster
(
    event_date Date,
    event_time DateTime,
    user_id UInt64,
    event_type String,
    duration UInt32
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/events_local', '{replica}')
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, event_time, user_id);
```

### 2. 创建分布式表

```sql
-- 创建分布式表，用于跨分片查询
CREATE TABLE events_all ON CLUSTER production_cluster
AS events_local
ENGINE = Distributed('production_cluster', default, events_local, rand());
```

### 3. 插入和查询测试

```sql
-- 写入测试数据（可任选节点执行，会自动分发）
INSERT INTO events_all VALUES ('2023-01-01', '2023-01-01 10:00:00', 101, 'click', 50);

-- 查询测试（可在任意节点执行）
SELECT count() FROM events_all WHERE event_date = '2023-01-01';

-- 检查各分片数据分布
SELECT shard_num, host_name, database, table, total_rows
FROM cluster('production_cluster', system, tables)
WHERE name = 'events_local'
SETTINGS skip_unavailable_shards=1;
```

## 监控与维护

### 1. 检查集群健康状况

```bash
# 使用 clickhouse 工具
clickhouse client --host ch-node1 --query "SELECT cluster, shard_num, replica_num, host_name, is_leader, is_readonly FROM system.clusters JOIN system.replicas USING(database, table);"
```

### 2. 故障恢复

如果某个副本发生故障:

```sql
-- 检查副本状态
SELECT * FROM system.replication_queue;

-- 启动副本恢复
SYSTEM SYNC REPLICA default.events_local;
```

### 3. 添加新的副本或分片

可通过添加配置并执行:

```sql
-- 刷新分布式 DDL 队列
SYSTEM RELOAD CONFIG;

-- 重新分布已有数据（如需）
INSERT INTO events_all SELECT * FROM events_local AS OF 1;
```

## 最佳实践

### 部署最佳实践

1. 保持 ZooKeeper 奇数节点，最少 3 个
2. 合理分配分片数，通常为副本数的倍数
3. 启用 internal_replication=true 以利用表级副本
4. 定期监控磁盘空间和内存使用情况

### 性能优化

1. 使用适合的分区策略
2. 调整内存和磁盘缓存设置
3. 适当增加同步副本线程数
4. 配置备份和快照策略

## 注意事项

1. 集群初始化完成后尽量避免改变拓扑
2. 修改集群配置时要逐步应用，逐个重启服务
3. 定期备份 ZooKeeper 中的关键元数据
4. 配置监控告警机制确保及时发现异常

集群版提供更高的可靠性和扩展性，但相比单机版也有更多的运维复杂性。请根据实际业务需求合理选择部署方案。
