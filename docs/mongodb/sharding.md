# MongoDB 分片集群

## 概述

MongoDB 分片 (Sharding) 是一种跨多台机器分布数据的方法。 MongoDB 使用分片将大型数据集分布在多个服务器或服务器群集上，以提高数据处理能力和存储容量。

- 存储瓶颈： 单机磁盘容量无法容纳持续增长的数据。
- 性能瓶颈： 活跃数据集超过物理内存容量，导致大量磁盘IO，读写性能下降。
- 吞吐瓶颈： 单一服务器的网络和CPU处理能力无法承受高并发的读写请求

## 架构组件

- 配置服务器（Config Servers）

配置服务器存储集群元数据（如片键值和块映射），以及锁以同步元数据更改。

- 分片（Shard）

集群的“数据存储节点”，是实际承载数据的单元。

- mongos 查询路由器

应用连接到 `mongos` 进程而不是直接连接到分片，它充当中间层，代表应用程序处理查询和分发操作。

### 数据流图

```mermaid
graph LR
    A[客户端] -->|请求| B(① mongos接收)
    B -->|② 查询：<br/>“数据在哪？”| C[Config Servers]
    C -->|③ 回复位置| B
    B -->|④ 转发请求到正确分片| D{目标分片}
    D -->|Shard 1| E[分片1]
    D -->|Shard 2| F[分片2]
    E & F -->|⑤ 返回数据| B
    B -->|⑥ 最终结果| A

```

## 构建分片集群

- 1个配置服务器副本集（3个成员）
- 2个分片副本集（每个3个成员）
- 1个mongos实例（可以多个，无状态)

### 单机构建最小实验环境

### 端口规划

- 配置服务器副本集 (configsvr): 29901, 29902, 29903
- 分片1副本集 (shardsvr): 29911, 29912, 29913
- 分片2副本集 (shardsvr): 29921, 29922, 29923
- mongos: 29900

### 配置文件

#### 配置服务器配置文件

在用于配置服务器时，副本集的配置有以下限制：

- 不能有仲裁节点。
- 不得包含延迟节点。
- 必须构建索引（即任何成员的 members[n].buildIndexes 设置都应为 true,默认就可以） 。

创建第一个配置服务器配置文件 mongod-config-29901.conf：

```
# 配置文件1 - 配置服务器成员1
systemLog:
  destination: file
  path: /data/mongodb/config1/mongod.log
  logAppend: true
storage:
  dbPath: /data/mongodb/config1/db
  journal:
    enabled: true
net:
  bindIp: 0.0.0.0
  port: 29901
replication:
  replSetName: configReplSet  # 副本集名称
sharding:
  clusterRole: configsvr  # 关键！声明为配置服务器
security:
  authorization: enabled
  keyFile: /data/mongodb/shared/keyfile  # 集群内认证文件
processManagement:
  fork: true
  pidFilePath: /data/mongodb/config1/mongod.pid

```

其他两个配置服务器类似，只需修改：
path, dbPath, port, pidFilePath 中的端口号

#### 分片副本集 (shardsvr) 配置文件

创建分片1第一个成员配置文件 mongod-shard1-29911.conf：

```
# 分片1成员1配置文件
systemLog:
  destination: file
  path: /data/mongodb/shard1_1/mongod.log
  logAppend: true
storage:
  dbPath: /data/mongodb/shard1_1/db
  journal:
    enabled: true
net:
  bindIp: 0.0.0.0
  port: 29911
replication:
  replSetName: shard1ReplSet  # 分片1副本集名称
sharding:
  clusterRole: shardsvr  # 关键！声明为分片服务器
security:
  authorization: enabled
  keyFile: /data/mongodb/shared/keyfile
processManagement:
  fork: true
  pidFilePath: /data/mongodb/shard1_1/mongod.pid

```

注意：分片2的配置文件类似，但 replication.replSetName 改为 shard2ReplSet，端口改为2992x系列。

### 目录规划

```
mkdir -p /data/mongodb/{config1,config2,config3,shard1_1,shard1_2,shard1_3,shard2_1,shard2_2,shard2_3,mongos}/db
```

### 通信认证文件

```
# 生成keyfile
mkdir -p /data/mongodb/shared
openssl rand -base64 756 > /data/mongodb/shared/keyfile
chmod 400 /data/mongodb/shared/keyfile
# 确保所有mongod进程用户有读取权限
```

### 启动服务并初始化

配置服务器

```
# 启动三个配置服务器
mongod -f mongod-config-29901.conf
mongod -f mongod-config-29902.conf
mongod -f mongod-config-29903.conf

# 连接任意一个初始化副本集
mongosh --port 29901
// 初始化配置服务器副本集
rs.initiate(
  {
    _id: "configReplSet",
    configsvr: true,  // 这里也要指定configsvr
    members: [
      { _id: 0, host: "localhost:29901" },
      { _id: 1, host: "localhost:29902" },
      { _id: 2, host: "localhost:29903" }
    ]
  }
)

// 等待选举完成
rs.status()
```

创建一个超级用户

```
// 切换到admin数据库
use admin
// 创建超级管理员用户（这里用户名/密码简单，生产环境要用强密码）
db.createUser({
  user: "admin",
  pwd: "admin123",
  roles: [
    { role: "root", db: "admin" },
    { role: "clusterAdmin", db: "admin" },
    { role: "userAdminAnyDatabase", db: "admin" }
  ]
})
```

分片副本集1服务器

```
# 启动分片1的三个成员
mongod -f mongod-shard1-29911.conf
mongod -f mongod-shard1-29912.conf
mongod -f mongod-shard1-29913.conf

# 连接初始化
mongosh --port 29911
// 初始化分片1副本集
rs.initiate(
  {
    _id: "shard1ReplSet",
    members: [
      { _id: 0, host: "localhost:29911" },
      { _id: 1, host: "localhost:29912" },
      { _id: 2, host: "localhost:29913" }
    ]
  }
)

rs.status()
```

分片副本集2服务器

```
# 启动分片1的三个成员
mongod -f mongod-shard2-29921.conf
mongod -f mongod-shard2-29922.conf
mongod -f mongod-shard2-29923.conf

# 连接初始化
mongosh --port 29921
// 初始化分片1副本集
rs.initiate(
  {
    _id: "shard2ReplSet",
    members: [
      { _id: 0, host: "localhost:29921" },
      { _id: 1, host: "localhost:29922" },
      { _id: 2, host: "localhost:29923" }
    ]
  }
)

rs.status()
```

到此副本集已经全部准备完毕!

### mongos

#### 配置

创建mongos配置文件 mongos-29900.conf：

```
# mongos配置文件
systemLog:
  destination: file
  path: /data/mongodb/mongos/mongos.log  # 注意是mongos.log，不是mongod.log
  logAppend: true
net:
  bindIp: 0.0.0.0
  port: 29900
sharding:
  configDB: configReplSet/localhost:29901,localhost:29902,localhost:29903
security:
  keyFile: /data/mongodb/shared/keyfile
processManagement:
  fork: true
  pidFilePath: /data/mongodb/mongos/mongos.pid
```

#### 启动

```
mongos -f mongos-29900.conf
```

### 通过mongos配置集群

#### 配置分片集群

```
// 连接到mongosh
mongosh --port 29900 -u admin -p admin123 --authenticationDatabase admin
或
mongosh --port 29900
use admin
db.auth("admin", "admin123")
// 添加分片1
sh.addShard("shard1ReplSet/localhost:29911,localhost:29912,localhost:29913")
// 添加分片2
sh.addShard("shard2ReplSet/localhost:29921,localhost:29922,localhost:29923")
// 查看分片信息
db.shards.find()
// 查看分片状态
sh.status()
```

#### 启用数据库分片

假设我们要对数据库myapp分片）：

```
// 切换到目标数据库或指定数据库名
use myapp
// 启用该数据库的分片功能
// 创建索引（必须先在分片键上创建索引）
db.users.createIndex({ "user_id": 1 })
// 对集合进行分片 , 支持两种分片方式 范围分片和hash分片
基于范围的分片可以使用多个字段作为分片键，并将数据划分为由分片键值确定的连续范围。
sh.shardCollection("myapp.users", { "user_id": 1 })
// 哈希分片使用单个字段的哈希索引作为分片键，在分片集群中对数据进行分区。
// sh.shardCollection("myapp.users", { "user_id": "hashed" })
```

分片键注意事项

您选择的分片键会影响分片效率，以及您利用某些分片功能（例如区域）的能力。

mongosh 提供了方法 `convertShardKeyToHashed()`。此方法使用与哈希索引相同的哈希函数，且可用于查看某一键的哈希值。

#### 验证

```
// 查看详细集群状态
sh.status()  // 显示所有分片、数据库、集合、块分布等信息

// 查看集合的分片分布
db.users.getShardDistribution()

// 查看配置信息
db.getSiblingDB("config").shards.find()
db.getSiblingDB("config").databases.find()
db.getSiblingDB("config").collections.find()
```

### 应用连接分片集群

```
const uri = "mongodb://localhost:29900/myapp?replicaSet=不是必需的&directConnection=false";
// 注意：连接的是mongos，多个mongos可以用逗号分隔
const uri = "mongodb://admin:admin123@mongos1:29900,mongos2:29900/myapp?authSource=admin&replicaSet=notRequired";
```

## 分片策略

### 块范围分片

- 数据根据分片键值的范围分割
- 使用 `_id`、数字或时间戳字段时常用
- 分布不均可能导致热点问题

### Hash 分片

- 对片键进行 Hash 运算，实现更均匀分布
- 更适合随机分发数据
- 不支持范围查询优化

### Zone 分片

- 将数据分发到定义的区域(zone)
- 每个 zone 包含一或多一分片
- 提高读写操作性能

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

### 检查分片状态

```javascript
// 显示集群状态
sh.status();

// 显示分片信息
db.printShardingStatus();

// 查看集合分片统计
db.collection.stats();
```

### 增加分片

```bash
# 添加新分片
sh.addShard("new-shard-host:27018")

# 检查分片列表
sh.getShardList()
```

## 监控与调优

### 关键指标

- 集群 CPU 使用率
- 内存使用情况
- 磁盘 I/O
- 网络延迟
- 平衡状态

### 分片操作查询

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
