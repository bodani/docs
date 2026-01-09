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
  dbPath: /var/lib/mongo
  journal:
    enabled: true

  # 存储引擎配置
  engine: wiredTiger
  wiredTiger:
    engineConfig:
      cacheSizeGB: 1
    collectionConfig:
      blockCompressor: snappy
```

### 3. 系统日志配置

```yaml
systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log
```

### 4. 进程管理配置

```yaml
processManagement:
  fork: true
  pidFilePath: /var/run/mongodb/mongod.pid
  timeZoneInfo: /usr/share/zoneinfo
```

### 5. 安全配置

```yaml
security:
  authorization: enabled # 启用认证
  keyFile: /etc/mongo-security/keyfile
  clusterAuthMode: keyFile

  # TLS/SSL 配置
  ssl:
    mode: requireSSL
    PEMKeyFile: /etc/ssl/mongodb.pem
```

## 配置参数说明

### 性能优化配置

- **cacheSizeGB**: WiredTiger 存储引擎的缓存大小，通常设置为主机内存的一半
- **journal**: 用于数据持久化的日记功能，推荐启用
- **syncdelay**: 系统数据刷新间隔（秒），默认 60 秒

### 集群配置示例

```yaml
replication:
  replSetName: rs0

sharding:
  clusterRole: shardsvr # 在分片中为 shardsvr，配置服务器为 configsvr
```

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
