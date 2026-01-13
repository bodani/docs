# pgbackrest 数据备份恢复管理

## 基本概念

- 全量备份 [Full backup]
- 差异备份 [Differential backup]
- 增量备份 [Incremental backup]

## 安装

### 编译安装

编译后将二进制文件分发到其他环境中即可，误在生产环境编译，有些依赖只编译过程中需要。

必要安装和配置

```
sudo apt-get install postgresql-client libxml2 libssh2-1

sudo mkdir -p -m 770 /var/log/pgbackrest
sudo chown postgres:postgres /var/log/pgbackrest
sudo mkdir -p /etc/pgbackrest
sudo mkdir -p /etc/pgbackrest/conf.d
sudo touch /etc/pgbackrest/pgbackrest.conf
sudo chmod 640 /etc/pgbackrest/pgbackrest.conf
sudo chown postgres:postgres /etc/pgbackrest/pgbackrest.conf
```

### 安装包方式

```
apt-get install pgbackrest
```

## 配置

vi /etc/pgbackrest/pgbackrest.conf 或 vi /etc/pgbackrest.conf

```
[demo]
pg1-path=/var/lib/postgresql/16/demo
```

设置存储路径

```
sudo mkdir -p /data/pgbackrest

sudo chmod 750 /data/pgbackrest

sudo chown postgres:postgres /var/lib/pgbackrest
```

测试检查配置

```
pgbackrest --stanza=demo --log-level-console=info check
```

## 快速上手

### 配置 wal 归档

postgresql.conf

```
archive_command = 'pgbackrest --stanza=demo archive-push %p'
archive_mode = on
max_wal_senders = 3
wal_level = replica
```

### 创建 Stanza

```
pgbackrest --stanza=demo --log-level-console=info stanza-create
```

### 验证 wal 归档

生成新的 wal 查看是否归档成功

```
select pg_create_restore_point('pgBackRest Archive Check');
select pg_switch_wal();
```

### 执行备份

```
pgbackrest --stanza=demo --log-level-console=info backup

pgbackrest --stanza=demo --log-level-console=info backup --type=diff

pgbackrest --stanza=demo --log-level-console=info backup --type=full

pgbackrest --stanza=demo --log-level-console=info backup --type=incr
```

### 定期备份

```
#m h   dom mon dow   command
30 06  *   *   0     pgbackrest --type=full --stanza=demo backup
30 06  *   *   1-6   pgbackrest --type=diff --stanza=demo backup
```

### 查看备份信息

```
pgbackrest info
```

### 数据恢复

```
pgbackrest --stanza=demo restore
```

## 配置管理

### 性能优化

考虑到版本兼容性或其他原因，多项可优化的选项默认没有开启

- compress-type (v2.27) gz -> zst
- repo-bundle (v2.39) repo1-bundle=y 。 将小文件打包，尤其在对象存储场景中将会带来极大的性能提升
- repo-block 文件级别到块基本的差异备份 在执行增量或查分备份的时候。

根据具体案例进行优化的参数

- process-max 每个命令所使用的最多进程数
- archive-async 异步归档 wal 需要 spool 用于缓冲
- backup-standby 在从库备份，减少主库压力
- start-fast=y 主动触发 checkpoint

配置项

```
compress-type=zst
repo1-bundle=y
repo1-block=y
archive-async=y
log-level-file=detail
repo1-host=repository
spool-path=/var/spool/pgbackrest

[global:archive-get]
process-max=2

[global:archive-push]
process-max=2
```

```
pgbackrest check
```

### 数据加密

```
repo1-cipher-pass=cJ77S7DAlAjZJMpLTNe/rTIBU2ak71L9uCWflrBaGahjvry2Y8z1DBtb7I1S22tF
repo1-cipher-type=aes-256-cbc
```

## 数据恢复中的高级应用

### 差异恢复

--delta ，在恢复的时候计算 SHA-1, mainfest 与本地数据进行对比。如果本地数据与恢复数据差异小， 这会很高效，与 pg_rewind 类似

### 加速恢复

增大 process-max=4， 不同于备份场景，因为恢复场景中数据库是关闭状态，不对外提供服务， 可以适当提高并发以加快恢复速度。

### 只恢复指定的 database test2

```
pgbackrest --stanza=demo --delta \
 --db-include=test2 --type=immediate --target-action=promote restore
```

如果要恢复多个 database

```
pgbackrest --stanza=demo --delta \
 --db-include=test1 --db-include=test2  --type=immediate --target-action=promote restore
```

恢复后删除其他的库

```
drop database testxxx;
```

### 恢复为从库

#### Hot Standby

数据库恢复后，仍保持恢复模式，即从库模式，而不升变为主库

```
pgbackrest --stanza=demo --delta --type=standby restore
```

使用 --=standby 后产生的恢复文件 `standby.signal` 而不是 `recover.signal`

#### Streaming Replication

配置 recovery-option

```
[demo]
pg1-path=/var/lib/postgresql/16/demo
recovery-option=primary_conninfo=host=172.17.0.6 port=5432 user=replicator

[global]
log-level-file=detail
repo1-host=repository
```

## 监控

从 info 中查看

https://github.com/woblerr/pgbackrest_exporter

## Point-in-Time Recovery

```
pgbackrest --stanza=demo --delta \
       --type=time "--target=2025-10-18 08:42:10.202702+00" \
       --target-action=promote restore
```

--type 通常会选择时间类型，注意设置时区， 在恢复的时候会自动选择合适的全备份。

## 备份到 s3

支持多个 repo 存储, s3 需要 https 协议

```
repo2-bundle=y
repo2-cipher-pass=cJ77S7DAlAjZJMpLTNe/rTIBU2ak71L9uCWflrBaGahjvry2Y8z1DBtb7I1S22tF
repo2-cipher-type=aes-256-cbc
repo2-path=/demo-repo
repo2-retention-full=4
repo2-s3-bucket=pgback
repo2-s3-endpoint=https://10.1.80.61:9000
repo2-s3-key=admin
repo2-s3-key-secret=admin123
repo2-s3-region=us-east-1
repo2-type=s3
repo2-s3-verify-tls=n
repo2-s3-uri-style=path
```

```
pgbackrest --stanza=demo --repo=2 \
       --log-level-console=info backup
```

## 日志

/var/log/pgbackrest/

## 异步 wal 日志备份

- archive-async=y 开启异步
- spool-path 临时存储目录，push 早期版本，先把 wal 复制到 spool 在传输，在 v1.13 版本中进行了改造，只存储 wal 的状态。
- process-max 多任务。 分别对于不同的过程。
- archive-get-queue-max . get 采用预取的方式。 size 182MiB。 与多任务配合使用

```
[demo]
pg1-path=/var/lib/postgresql/16/demo

[global]
archive-async=y
log-level-file=detail
repo1-host=repository
spool-path=/var/spool/pgbackrest

[global:archive-get]
process-max=2

[global:archive-push]
process-max=2
```

## 专属仓库

在某些场景下，你可能需要为特定的 PostgreSQL 实例创建一个**专属的备份仓库（dedicated repository）**。这可以提高安全性、隔离性，并便于管理不同实例的数据。

- 将数据库的全备份在专属仓库中执行
- 专属仓库与备份的数据之间需要彼此 ssh 免密或 TSL 通信，及对应访问权限
- 一个专属仓库管理多个数据库

## 在从库中执行备份

backup-standby=y

适合搭配专属仓库场景。 自动判断主从，选择在从库中备份大部分文件，主库主备份少部分文件。

不能独自运行在从库中，需要主库的信息。这一点对原有的数据库系统结构入侵比较大。

## 删除 stanza

官方推荐步骤：

1. 停止 PostgreSQL 服务
2. 停止 pgBackRest
3. 删除 stanza 配置

思考， 删除 stanza 必须要停数据库吗？ 这个影响太大了吧，关于删除 stanza 是否必须停数据库的问题，实际上**不需要停止整个 PostgreSQL 数据库集群**。

每次删除其中一个 repo

```
# 停止 pgBackRest
pgbackrest --stanza=demo --log-level-console=info stop

2025-11-28 01:28:54.689 P00   INFO: stop command begin 2.57.0: --exec-id=4181641-c8a319b8 --log-level-console=info --stanza=demo
2025-11-28 01:28:54.693 P00   INFO: stop command end: completed successfully (7ms)
# 删除 repo1
pgbackrest --stanza=demo --repo=1  --log-level-console=info stanza-delete
2025-11-28 01:29:15.436 P00   INFO: stanza-delete command begin 2.57.0: --exec-id=4181644-b8b6f0a6 --log-level-console=info --pg1-path=/var/lib/postgresql/17/main1 --pg1-port=5433 --repo=1 --repo1-cipher-pass=<redacted> --repo2-cipher-pass=<redacted> --repo1-cipher-type=aes-256-cbc --repo2-cipher-type=aes-256-cbc --repo1-path=/data/pgback --repo2-path=/demo-repo --repo2-s3-bucket=pgback --repo2-s3-endpoint=https://10.1.80.61:9000 --repo2-s3-key=<redacted> --repo2-s3-key-secret=<redacted> --repo2-s3-region=us-east-1 --repo2-s3-uri-style=path --no-repo2-storage-verify-tls --repo2-type=s3 --stanza=demo
2025-11-28 01:29:15.447 P00  ERROR: [038]: postmaster.pid exists - looks like PostgreSQL is running. To delete stanza 'demo' on repo1, shut down PostgreSQL for stanza 'demo' and try again, or use --force.
2025-11-28 01:29:15.447 P00   INFO: stanza-delete command end: aborted with exception [038]

# --force 删除
pgbackrest --stanza=demo --repo=1 --log-level-console=info stanza-delete --force
2025-11-28 01:29:51.722 P00   INFO: stanza-delete command begin 2.57.0: --exec-id=4181648-7769b634 --force --log-level-console=info --pg1-path=/var/lib/postgresql/17/main1 --pg1-port=5433 --repo=1 --repo1-cipher-pass=<redacted> --repo2-cipher-pass=<redacted> --repo1-cipher-type=aes-256-cbc --repo2-cipher-type=aes-256-cbc --repo1-path=/data/pgback --repo2-path=/demo-repo --repo2-s3-bucket=pgback --repo2-s3-endpoint=https://10.1.80.61:9000 --repo2-s3-key=<redacted> --repo2-s3-key-secret=<redacted> --repo2-s3-region=us-east-1 --repo2-s3-uri-style=path --no-repo2-storage-verify-tls --repo2-type=s3 --stanza=demo
2025-11-28 01:29:52.006 P00   INFO: stanza-delete command end: completed successfully (287ms)
```

## 启停

停止数据库的备份，包括 wal 和数据备份。
主要应用场景，用于临时测试的数据库。避免备份数据污染 repo

```
pgbackrest --stanza=demo --log-level-console=info stop
pgbackrest --stanza=demo --log-level-console=info start
```

## 总结

```
cat /etc/pgbackrest.conf
[global]
repo1-bundle=y
repo1-path=/data/pgback
repo1-retention-diff=1
repo1-retention-full=2
repo1-cipher-pass=xxxxxxxx
repo1-cipher-type=aes-256-cbc
repo2-bundle=y
repo2-cipher-pass=xxxx
repo2-cipher-type=aes-256-cbc
repo2-path=/demo
repo2-retention-full=4
repo2-s3-bucket=pgback
repo2-s3-endpoint=https://s3address:8888
repo2-s3-key=key
repo2-s3-key-secret=secrec
repo2-s3-region=us-east-1
repo2-type=s3
repo2-s3-verify-tls=n
repo2-s3-uri-style=path
start-fast=y
compress-type=zst
backup-standby=n
archive-async=y
spool-path=/var/spool/pgbackres
log-level-file=info

[global:archive-push]
compress-level=9
process-max=2

[global:archive-get]
process-max=2

[demo]
pg1-path=/var/lib/postgresql/17/main1
pg1-port=5433
process-max=4
```

cipher-pass

```
openssl rand -base64 48
```
