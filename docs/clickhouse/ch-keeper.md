

## clickhouse-keeper相比zookeeper的优点

#### 为什么要引入clickhouse-keeper呢？主要是ck使用zookeeper有着众多痛点，

- 使用java开发
- 运维不便
- 要求独立部署
- zxid overflow问题
- snapshot和log没有经过压缩
- 不支持读的线性一致性 

#### 而keeper存在着以下优点：

- 使用c++开发，技术栈与ck统一
- 即可独立部署，又可集成到ck中
- 没有zxid overflow问题
- 读性能更好，写性能相当
- 支持对snapshot和log的压缩和校验
- 支持读写的线性一致性

## 配置参数

```
<keeper_server>
    <tcp_port>2181</tcp_port>
    <server_id>1</server_id>
    <log_storage_path>/var/lib/clickhouse/coordination/log</log_storage_path>
    <snapshot_storage_path>/var/lib/clickhouse/coordination/snapshots</snapshot_storage_path>

    <coordination_settings>
        <operation_timeout_ms>10000</operation_timeout_ms>
        <session_timeout_ms>30000</session_timeout_ms>
        <async_replication>true</async_replication>
        <raft_logs_level>trace</raft_logs_level>
    </coordination_settings>

    <raft_configuration>
        <server>
            <id>1</id>
            <hostname>zoo1</hostname>
            <port>9234</port>
        </server>
        <server>
            <id>2</id>
            <hostname>zoo2</hostname>
            <port>9234</port>
        </server>
        <server>
            <id>3</id>
            <hostname>zoo3</hostname>
            <port>9234</port>
        </server>
    </raft_configuration>
</keeper_server>
```
keeper 参数: https://clickhouse.com/docs/en/guides/sre/keeper/clickhouse-keeper#configuration

多节点集群通信参数:

- heart_beat_interval_ms 
- election_timeout_lower_bound_ms
- election_timeout_upper_bound_ms
- can_become_leader/priority/quorum_reads，

 具体含义参考：https://clickhouse.com/docs/zh/operations/clickhouse-keeper/

- async_replication 启用异步复制。所有写入和读取的保证都得以保留，同时实现更好的性能。默认情况下，该设置是禁用的，以避免破坏向后兼容性

## 转换

clickhouse-keeper-converter