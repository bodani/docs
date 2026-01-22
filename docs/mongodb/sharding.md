# MongoDB 分片集群

## 概述

MongoDB 分片 (Sharding) 是一种跨多台机器分布数据的方法。 MongoDB 使用分片将大型数据集分布在多个服务器或服务器群集上，以提高数据处理能力和存储容量。

- 存储瓶颈： 单机磁盘容量无法容纳持续增长的数据。
- 性能瓶颈： 活跃数据集超过物理内存容量，导致大量磁盘IO，读写性能下降。
- 吞吐瓶颈： 单一服务器的网络和CPU处理能力无法承受高并发的读写请求

## 架构组件

### 1. 分片 (Shards)

分片包含数据子集，MongoDB 会在这些分片之间均衡分配数据。

### 2. mongos 查询路由器

应用连接到 `mongos` 进程而不是直接连接到分片，它充当中间层，代表应用程序处理查询和分发操作。

### 3. 配置服务器

配置服务器存储集群元数据（如片键值和块映射），以及锁以同步元数据更改。

## 分片策略

### 1. 块范围分片

- 数据根据分片键值的范围分割
- 使用 `_id`、数字或时间戳字段时常用
- 分布不均可能导致热点问题

### 2. Hash 分片

- 对片键进行 Hash 运算，实现更均匀分布
- 更适合随机分发数据
- 不支持范围查询优化

### 3. Zone 分片

- 将数据分发到定义的区域(zone)
- 每个 zone 包含一或多一分片
- 提高读写操作性能

## 启用分片

### 1. 开启集群

```bash
# 启动配置服务器
mongod --configsvr --replSet configs --port 27019 --dbpath /data/configdb

# 启动路由服务器
mongos --configdb configs/<config_srv1>:27019,<config_srv2>:27019,<config_srv3>:27019 --port 27017

# 启动分片服务器
mongod --shardsvr --replSet shard1 --port 27018 --dbpath /data/shard1
```

### 2. 添加分片

```bash
# 连接到路由服务器
mongo localhost:27017

# 添加分片
sh.addShard("shard1/host1:27018,host2:27018")
sh.addShard("shard2/host3:27018,host4:27018")
```

### 3. 启用数据库分片

```javascript
// 启用数据库分片
sh.enableSharding("databaseName");

// 设置分片键
sh.shardCollection("databaseName.collectionName", { fieldName: 1 });
```

## 分片键选择

### 好的分片键特征

- 足够基数以支持数据分发
- 排除低基数字段（如性别）
- 避免单调字段（时间戳）防止热点
- 查询模式匹配

### 复合分片键

```javascript
// 创建复合分片键
sh.shardCollection("users", { userId: 1, region: 1 });

// 顺序很重要，第一个键决定块边界
```

## 管理分片集群

### 1. 检查分片状态

```javascript
// 显示集群状态
sh.status();

// 显示分片信息
db.printShardingStatus();

// 查看集合分片统计
db.collection.stats();
```

### 2. 迁移块数据

```javascript
// 检查块信息
db.getSiblingDB("config").chunks.findOne();

// 平衡器状态
sh.setBalancerState(false); // 关闭平衡器
sh.setBalancerState(true); // 启用平衡器
```

### 3. 增加容量

```bash
# 添加新分片
sh.addShard("new-shard-host:27018")

# 检查分片列表
sh.getShardList()
```

## 监控与调优

### 1. 关键指标

- 集群 CPU 使用率
- 内存使用情况
- 磁盘 I/O
- 网络延迟
- 平衡状态

### 2. 分片操作查询

```javascript
// 查询命中单一分片（最优）
db.orders.find({ userId: ObjectId("...") });

// 查询需要路由到多个分片
db.orders.find({ category: "Electronics" });
```

## 注意事项

### 分区倾斜解决方法

1. 检查分片键分布
2. 考虑重新分片策略
3. 使用 Zone Sharding

### 限制说明

- 分片键一旦设置无法修改
- 不能在已分片的集合上设置分片键
- 分片仅支持单个集合的唯一索引

## 最佳实践

1. 启动分片前进行压力测试
2. 监控块分配情况
3. 计划停机窗口维护平衡
4. 正确选择分片键减少数据迁移
5. 使用复制集作为分片确保高可用
