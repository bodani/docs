# MongoDB 配置

## 配置文件结构

MongoDB 的配置主要通过 `mongod.conf` 文件进行设置，默认位置通常在 `/etc/mongod.conf`。

## 主要配置选项

### 1. 网络配置

```yaml
net:
  port: 27017
  bindIp: 127.0.0.1
  bindIpAll: true # 绑定到所有IP地址（生产环境需要谨慎考虑）
```

### 2. 存储配置

```yaml
storage:
  # 存储目录
  dbPath: /var/lib/mongo
  directoryPerDB: 每个集合是否独立存储目录
  # 存储引擎配置
  engine: wiredTiger
  wiredTiger:
    engineConfig:
      cacheSizeGB: 内存绝对值
      cacheSizePct: 内存占比百分比
      journalCompressor: 压缩类型 none 、snappy 、zlib 、zstd
      zstdCompressionLevel: 压缩等级，当journalCompressor或 blockCompressor 设置为zlib时适用
      directoryForIndexes: 索引和数据是否分开独立存放, 索引 index 目录， 数据 collection 目录
    collectionConfig:
      blockCompressor: 数据集合压缩类型 默认 snappy
    indexConfig:
      prefixCompression: 开启前缀压缩 默认 true
```

内存根据总体内存计算默认设置。容器中会根据 limits.memory 进行设置

| 系统总内存 | 计算公式                           | 默认缓存大小 |
| ---------- | ---------------------------------- | ------------ |
| 2 GB       | Math.max(0.5×(2-1)=0.5, 0.256)     | 0.5 GB       |
| 4 GB       | Math.max(0.5×(4-1)=1.5, 0.256)     | 1.5 GB       |
| 8 GB       | Math.max(0.5×(8-1)=3.5, 0.256)     | 3.5 GB       |
| 16 GB      | Math.max(0.5×(16-1)=7.5, 0.256)    | 7.5 GB       |
| 64 GB      | Math.max(0.5×(64-1)=31.5, 0.256)   | 31.5 GB      |
| 128 GB     | Math.max(0.5×(128-1)=63.5, 0.256)  | 63.5 GB      |
| 256 GB     | Math.max(0.5×(256-1)=127.5, 0.256) | 127.5 GB     |

压缩选取说明：

设置的是集合的默认压缩，可在创建集合的时候定义压缩类型。

| 特性维度             | **Snappy**                    | **zlib**                         | **Zstandard (zstd)**                          | **无压缩**               |
| :------------------- | :---------------------------- | :------------------------------- | :-------------------------------------------- | :----------------------- |
| **压缩率**           | 中等 (约 50-60%)              | 高 (约 70-80%)                   | 高 (约 70-80%，可调)                          | 无                       |
| **CPU 开销**         | 低                            | 高                               | 中等 (可随级别调整)                           | 无                       |
| **写入吞吐量影响**   | 最小                          | 显著                             | 中等                                          | 无                       |
| **读取（解压）速度** | 极快                          | 较慢                             | 快                                            | 不适用                   |
| **存储空间节省**     | 良好                          | 优秀                             | 优秀 (可调)                                   | 无                       |
| **MongoDB 默认状态** | **默认启用**                  | 可选                             | 可选 (v4.2+)                                  | 可选                     |
| **典型适用场景**     | 通用 OLTP，读写频繁，CPU 敏感 | 归档数据，存储成本敏感，读少写少 | 追求平衡的新项目，或替换 zlib 以降低 CPU 负载 | 性能极致优先，或测试基准 |

### 3. 系统日志配置

```yaml
systemLog:
  destination: file
  path: /var/log/mongodb/mongod.log
  logAppend: true
  quiet: false
  logRotate: reopen
  verbosity: 0 日志等级
```

### 4. 进程管理配置

```yaml
processManagement:
  fork: false # 是否为守护进程，容器或system方式管理设置为false
  pidFilePath: /var/run/mongodb/mongod.pid
  timeZoneInfo: /usr/share/zoneinfo
```

### 5. 安全配置

```yaml
security:
  authorization: enabled # 启用认证

  # TLS/SSL 配置
  ssl:
    mode: requireSSL
    PEMKeyFile: /etc/ssl/mongodb.pem
```

## 配置参数说明

### 性能优化配置

- **cacheSizeGB**: WiredTiger 存储引擎的缓存大小，通常设置为主机内存的一半
- **syncdelay**: 系统数据刷新间隔（秒），默认 60 秒

## 配置验证

修改配置文件后，可以通过以下命令验证配置：

```bash
# 验证配置文件格式
mongod --config /etc/mongod.conf --configtest

# 重启MongoDB服务使配置生效
sudo systemctl restart mongod
```

## 生产环境最佳实践

1. 禁用 bindIpAll 并指定具体的监听 IP
2. 启用身份验证和访问控制
3. 定期轮换密钥文件
4. 配置适当的日志级别和归档策略

## 系统配置

- 版本8.0 前 关闭透明大页
- ulimit 文件限制
