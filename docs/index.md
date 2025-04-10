# TeaLabs

> “知之者不如好之者，好之者不如乐之者。” - 孔子

## 目录

- [Linux](linux)
- [Mysql 笔记](mysql)
- [PostgreSQL 笔记](postgres)
- [常见问题](#常见问题)
- [资源推荐](#资源推荐)
- [贡献指南](#贡献指南)
- [许可](#许可)

## MySQL 笔记

在这里，你将找到关于 MySQL 数据库的详细笔记和教程：

- [MySQL 安装与配置](docs/mysql/installation.md)
- [MySQL 基本操作](docs/mysql/basic_operations.md)
- [MySQL 高级特性](docs/mysql/advanced_features.md)
- [MySQL 性能优化](docs/mysql/performance_tuning.md)

## PostgreSQL 笔记

以下是关于 PostgreSQL 数据库的详细笔记和教程：

- [PostgreSQL 安装与配置](docs/postgresql/installation.md)
- [PostgreSQL 基本操作](docs/postgresql/basic_operations.md)
- [PostgreSQL 高级特性](docs/postgresql/advanced_features.md)
- [PostgreSQL 性能优化](docs/postgresql/performance_tuning.md)

## 常见问题

一些在使用过程中可能会遇到的常见问题及其解决方案：

- [MySQL 常见问题](docs/mysql/faq.md)
- [PostgreSQL 常见问题](docs/postgresql/faq.md)

## 资源推荐

一些推荐的学习资源和工具：

- [官方文档 - MySQL](https://dev.mysql.com/doc/)
- [官方文档 - PostgreSQL](https://www.postgresql.org/docs/)
- [在线 SQL 教程](https://www.w3schools.com/sql/)
- [数据库设计工具](https://www.dbdesigner.net/)
- [数据结构动态图](https://www.cs.usfca.edu/~galles/visualization/)
## 贡献指南

欢迎任何形式的贡献！请阅读 [贡献指南](CONTRIBUTING.md) 以了解如何参与其中。

## 许可

本项目采用 [MIT 许可证](LICENSE)。

## 所有文章

### 测试
- [测试](test.md)

### 书籍
- [书籍](books/)

### ClickHouse
- [基准测试](clickhouse/benchmark.md)
- [最佳实践](clickhouse/bestpractices.md)
- [C1](clickhouse/c1.md)
- [Keeper](clickhouse/ch-keeper.md)
- [压缩](clickhouse/compresstion.md)
- [演示](clickhouse/demo.md)
- [用户](clickhouse/user.md)

#### ClickHouse 安装
- [安装集群](clickhouse/install/install_cluster.md)
- [安装 S3](clickhouse/install/install_s3.md)
- [安装单机版](clickhouse/install/install_single.md)

### 数据湖
- [Iceberg](datalake/iceberg.md)
- [Nessie](datalake/nessie.md)

### 英文词汇
- [英文词汇](en/words.md)

### Fluent Bit
- [问题](fluentbit/problems.md)

### Grafana
- [警报](grafana/alert.md)

### Kubernetes
- [StatefulSet 更新](kubernetes/sts_update.md)

### Linux
- [ELF 工具](linux/elfutil.md)
- [IPMI 工具](linux/ipmitool.md)
- [Kubectl](linux/kuberctl.md)
- [KVM](linux/kvm01.md)
- [补丁](linux/patch.md)
- [工具](linux/tools.md)
- [Web 管理](linux/webmanage.md)

### 中间件
- [Etcd](middleware/etcd.md)
- [Nginx](middleware/nginx.md)

### MongoDB
- [索引](mongodb/index.md)

### 监控
- [监控](monitor/index.md)
- [监控 VM](monitor/vm/index.md)

### MySQL
- [活跃](mysql/active.md)
- [管理](mysql/admin.md)
- [备份](mysql/backup.md)
- [二进制日志](mysql/binary.md)
- [克隆](mysql/clone.md)
- [配置](mysql/config.md)
- [双写](mysql/doublewrite.md)
- [导出器](mysql/exporter.md)
- [锁](mysql/lock.md)
- [内存](mysql/memory.md)
- [MGR](mysql/MGR.md)
- [监控](mysql/monitor.md)
- [Shell MGR](mysql/myshellMGR.md)
- [内存管理](mysql/mysqlmem.md)
- [MySQLslap](mysql/mysqlslap.md)
- [导航树](mysql/navtree.md)
- [权限管理](mysql/PrivilegeManagement.md)
- [代理](mysql/proxy.md)
- [Pt 工具](mysql/pt.md)
- [复制](mysql/replication.md)
- [表大小](mysql/table_size.md)
- [用户管理](mysql/users.md)

#### mysql 变更日志
- [Pro1](mysql/changelog/pro1.md)

### PostgreSQL
- [AD 锁](postgres/adlock.md)
- [归档](postgres/archive.md)
- [自动真空触发](postgres/auto_vacuum_trigger.md)
- [性能优化](postgres/awsome-postgres.md)
- [后台写入](postgres/bgwriter.md)
- [Citus 01](postgres/citus01.md)
- [Citus 11](postgres/citus11.md)
- [集群](postgres/cluster.md)
- [日常管理](postgres/daily_management.md)
- [DBA](postgres/dba.md)
- [Debezium](postgres/debezium.md)
- [删除](postgres/delete.md)
- [DTS](postgres/dts.md)
- [解释](postgres/explain.md)
- [扩展](postgres/extention.md)
- [填充因子](postgres/fillfactor.md)
- [函数与操作符](postgres/FunctionsandOperators.md)
- [高级 SQL](postgres/high_level_sql.md)
- [HLL](postgres/hll.md)
- [热更新](postgres/hotupdate.md)
- [HypoPG 索引](postgres/hypopg-index.md)
- [Bloom 索引](postgres/index-bloom.md)
- [索引失效](postgres/index-invalid.md)
- [索引类型及使用场景](postgres/index01.md)
- [插入](postgres/insert01.md)
- [安装](postgres/install.md)
- [安装 01](postgres/install01.md)
- [安装 02](postgres/install02.md)
- [LibPG](postgres/libpg.md)
- [锁等待](postgres/lock_wait.md)
- [日志](postgres/log.md)
- [逻辑备份](postgres/logical-backup.md)
- [逻辑复制故障转移](postgres/logical-replication_failover.md)
- [逻辑复制](postgres/logical-replication.md)
- [无密码登录](postgres/login_nopasswd.md)
- [物化视图](postgres/materialized.md)
- [监控解释](postgres/monitor_explain.md)
- [监控 SQL](postgres/monitor-sql.md)
- [监控](postgres/monitor.md)
- [正规化](postgres/normal-form.md)
- [OOM](postgres/oom.md)
- [参数](postgres/params.md)
- [分区](postgres/partition.md)
- [Partman](postgres/partman.md)
- [Patroni](postgres/patroni.md)
- [Patroni 02](postgres/patroni02.md)
- [Pg Activity](postgres/pg_activity.md)
- [Pg Buffercache](postgres/pg_buffercache.md)
- [Pg Citus](postgres/pg_citus.md)
- [Pg ELK](postgres/pg_elk.md)
- [Pg FDW](postgres/pg_fdw.md)
- [Pg JSON](postgres/pg_json.md)
- [Pg Lock](postgres/pg_lock.md)
- [Pg Pathman](postgres/pg_pathman.md)
- [Pg Prewarm](postgres/pg_prewarm.md)
- [Pg Rewind](postgres/pg_rewind.md)
- [Pg Rewrite](postgres/pg_rewrite.md)
- [Pg Rman](postgres/pg_rman.md)
- [Pg Trgm](postgres/pg_trgm.md)
- [Pg Age](postgres/pgage.md)
- [Pg Auto Failover](postgres/pgautofailover.md)
- [Pg Bench](postgres/pgbench.md)
- [Pg Bouncer](postgres/pgbouncer.md)
- [Pg Fincore](postgres/pgfincore.md)
- [Pg Pool2](postgres/pgpool2.md)
- [Pg Stat Tuple](postgres/pgstattuple.md)
- [Pg Watch2](postgres/pgwatch2.md)
- [物理备份](postgres/physical-backup.md)
- [PipelineDB 01](postgres/pipelinedb01.md)
- [PipelineDB 02](postgres/pipelinedb02.md)
- [PITR](postgres/pitr.md)
- [12](postgres/postgres12.md)
- [准备](postgres/prepare.md)
- [只读](postgres/readonly.md)
- [重新备份超级用户](postgres/reback_supper_user.md)
- [重新备份](postgres/reback.md)
- [复制 01](postgres/replication01.md)
- [复制 02](postgres/replication02.md)
- [角色管理](postgres/role-manager.md)
- [SSL](postgres/ssl.md)
- [统计](postgres/stat.md)
- [表空间](postgres/tablespace.md)
- [模板](postgres/template.md)
- [数据库设计思考](postgres/thinking_in_db_fd.md)
- [性能优化思考](postgres/thinking_in_db_performance.md)
- [调优思考](postgres/thinking_in_db_tune.md)
- [TimescaleDB](postgres/timescaledb.md)
- [TOAST](postgres/toast.md)
- [TPC-H](postgres/tpch.md)
- [非日志表](postgres/unlogged_table.md)
- [Upsert](postgres/upset.md)
- [Vacuum Limit](postgres/vacuum_limit.md)
- [Vacuum](postgres/vacuum.md)
- [查看活动](postgres/view_pg_stat_activity.md)
- [查看后台写入](postgres/view_pg_stat_bgwriter.md)
- [WAL LSN](postgres/wal_lsn.md)
- [WAL 大小](postgres/wal_size.md)

---

感谢您的访问！希望这些文档对你有所帮助。如果你有任何问题或建议，请通过 [issues](https://github.com/bodani/docs/issues) 提出。
