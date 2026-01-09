# MongoDB 复制集

## 概述

MongoDB 复制集 (Replica Set) 是一组维护相同数据集合的 mongod 实例。复制集提供了冗余和高可用性，是生产环境中推荐的数据存储方式。

## 复制集架构

### 节点角色

- **Primary（主节点）**：接收所有写操作
- **Secondary（从节点）**：从 Primary 节点复制数据
- **Arbiter（仲裁节点）**：参与选举但不保存数据

## 创建复制集

### 1. 配置文件准备

每个节点都需要相应配置：

```yaml
# mongod.conf
net:
  port: 27017
  bindIp: 0.0.0.0

replication:
  replSetName: rs0
```

### 2. 初始化复制集

```bash
# 连接到其中一个节点
mongo --port 27017

# 初始化复制集
rs.initiate()
```

### 3. 添加成员

```bash
# 添加复制集成员
rs.add("hostname2:27017")
rs.add("hostname3:27017")

# 或添加仲裁节点
rs.addArb("arbiter-hostname:27017")
```

## 成员配置

### 配置模板

```javascript
cfg = rs.conf();
cfg.members[0].priority = 2; // 设置优先级
cfg.members[1].priority = 1; // 设置优先级
cfg.members[2].priority = 0; // 非选举成员
rs.reconfig(cfg);
```

### 成员属性

- `priority`: 0-1000，影响选举，0 表示不可选举
- `votes`: 0 或 1，影响投票权
- `hidden`: true 为隐藏节点，对客户端不可见
- `slaveDelay`: 延迟复制（秒）

## 管理操作

### 查看复制集状态

```bash
# 查看复制集状态
rs.status()

# 查看复制集配置
rs.conf()

# 查看复制延迟
db.printSlaveReplicationInfo()
```

### 故障转移

MongoDB 会在 Primary 节点失效时自动进行故障转移：

- 至少需要两个节点能相互通信
- 选举过程通常在 10-30 秒内完成
- 旧的 Primary 节点在恢复后会成为 Secondary 节点

## 读写关注级别

### 写关注 (Write Concern)

```javascript
// 默认写入，返回acknowledged
db.collection.insertOne({ x: 1 }, { writeConcern: { w: 1 } });

// 等待多数节点确认
db.collection.insertOne({ x: 1 }, { writeConcern: { w: "majority" } });

// 设置超时时间
db.collection.insertOne(
  { x: 1 },
  { writeConcern: { w: "majority", wtimeout: 5000 } }
);
```

### 读关注 (Read Concern)

```javascript
// 最近数据
db.collection.find().readConcern("local");

// 已提交数据
db.collection.find().readConcern("available");

// 线性一致读
db.collection.find().readConcern("linearizable");
```

## 复制延迟

### 监控延迟

```bash
# 查看延迟
db.printSlaveReplicationInfo()

# 获取延迟统计
db.adminCommand("replSetGetStatus")
```

### 优化复制

- 启用 WiredTiger 存储引擎
- 调整 oplog 大小
- 避免大体积更新

## 运维最佳实践

### 监控指标

- 复制延迟
- oplog 使用情况
- 节点健康状态
- 写操作性能

### 部署策略

- 将复制集节点部署在不同的可用区
- 使用专用网络进行复制通信
- 正确设置节点优先级以确保合适的节点成为 Primary
- 定期测试故障转移过程
