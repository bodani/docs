# howto 系列

## explain analyze buffers 理解

hit buffers 的具体含义。 不是表面上理解的命中缓存块的数量，而是次数。

## 影响数据库关闭的事件

当数据库执行关闭操作时，需要长时间的处理问题分析

- 长事务
- 内存脏数据
- 未完成的归档，从库延迟wal日志


三种 关闭模式
- Smart  禁止新连接，然后等待所有现有客户端断开连接
- Fast （默认） 不会等待客户端断开连接。所有活动事务都会回滚，客户端会被强制断开连接，然后服务器就会关闭
- Immediate 立即关闭。不执行checkpoint , 在下次重启的时候执行恢复。

## 数据库启动等待过程分析

当数据库启动时间过长，如何分析数据库正在执行情况，在做什么，哪个阶段，还有多久等

日志内容通常如下
```
FATAL: the database system is starting up
```

1 通过进程分析 当前恢复进度
```
ps ax | grep 'startup recovering'
98786   ??  Us     0:15.81 postgres: startup recovering 000000010000004100000018
```

2 pg_controldata -D $PGDATA 查看数据库元数据进行分析

结合数据库恢复量开始、当前已恢复、目标、分析进度
```
select pg_size_pretty(pg_lsn '4A/E0FFE518' - pg_lsn '45/58000000');
```

3 PG15 中引入的 log_startup_progress_interval

## ctid 页地址

了解数据页物理分布，数据稀疏对性能的影响`
```
explain select ctid, * from t1 where  ctid = '(1, 12)';
```

## 利用pg_stat_statements进行宏观优化

- 时间做微分，QPS 宏观优化旨在减少资源消耗 
- 次数做微分，延迟 宏观优化旨在改善用户体验 
- 百分比，Top-N  宏观优化旨在平衡工作量 

## pg_dump pg_restore
以前的通用做法
```
备份：pg_dump -U postgres -v -F c -Z 4 -f ***.backup dbname  9压缩率最狠
恢复：pg_restore -U postgres -v -j 8 -d dbname ***.backup   8是采用8个线程
```

但是 -F c 保存在一个文件中，不能并发执行。 -F d 为一个目录文件，可以并行 
```
time pg_dump -Fd -j8 -f ./test_dump test
```

不落盘数据迁移 pg_dump |  pg_restore , 这种不能并行。 pgcopydb 工具就是为了解决这个问题，包括一个大表的并行处理。

## 索引创建进度
PG12+ , 依赖 pg_stat_progress_create_index

```
select
   now(),
   query_start as started_at,
   now() - query_start as query_duration,
   format('[%s] %s', a.pid, a.query) as pid_and_query,
   index_relid::regclass as index_name,
   relid::regclass as table_name,
   (pg_size_pretty(pg_relation_size(relid))) as table_size,
   nullif(wait_event_type, '') || ': ' || wait_event as wait_type_and_event,
   phase,
   format(
           '%s (%s of %s)',
           coalesce((round(100 * blocks_done::numeric / nullif(blocks_total, 0), 2))::text || '%', 'N/A'),
           coalesce(blocks_done::text, '?'),
           coalesce(blocks_total::text, '?')
   ) as blocks_progress,
   format(
           '%s (%s of %s)',
           coalesce((round(100 * tuples_done::numeric / nullif(tuples_total, 0), 2))::text || '%', 'N/A'),
           coalesce(tuples_done::text, '?'),
           coalesce(tuples_total::text, '?')
   ) as tuples_progress,
   current_locker_pid,
   (select nullif(left(query, 150), '') || '...' from pg_stat_activity a where a.pid = current_locker_pid) as current_locker_query,
   format(
           '%s (%s of %s)',
           coalesce((round(100 * lockers_done::numeric / nullif(lockers_total, 0), 2))::text || '%', 'N/A'),
           coalesce(lockers_done::text, '?'),
           coalesce(lockers_total::text, '?')
   ) as lockers_progress,
   format(
           '%s (%s of %s)',
           coalesce((round(100 * partitions_done::numeric / nullif(partitions_total, 0), 2))::text || '%', 'N/A'),
           coalesce(partitions_done::text, '?'),
           coalesce(partitions_total::text, '?')
   ) as partitions_progress,
   (
      select
         format(
                 '%s (%s of %s)',
                 coalesce((round(100 * n_dead_tup::numeric / nullif(reltuples::numeric, 0), 2))::text || '%', 'N/A'),
                 coalesce(n_dead_tup::text, '?'),
                 coalesce(reltuples::int8::text, '?')
         )
      from pg_stat_all_tables t, pg_class tc
      where t.relid = p.relid and tc.oid = p.relid
   ) as table_dead_tuples
from pg_stat_progress_create_index p
        left join pg_stat_activity a on a.pid = p.pid
order by p.index_relid
; -- in psql, use "\watch 5" instead of semicolon
```

## 避坑

### NULLs
不要使用 WHERE NOT IN (SELECT ...) — 使用 NOT EXISTS 代替
```
CREATE TABLE test (
    id INT PRIMARY KEY,
    col INT
);

INSERT INTO test (id, col) VALUES
(1, 2),  
(2, 1),  
(3, NULL),
(4, 3);

SELECT * FROM test WHERE col NOT IN (1, NULL);
 id | col 
----+-----
(0 行记录)
```

## int4 主键

###  CPU 内存对齐与 PostgreSQL 对齐填充详解
#### 1. 对齐填充的核心规则
- **字长（Word Size）对齐**：CPU 访问内存时，通常以字长（例如 8 字节）为单位。数据未对齐时可能导致多次内存操作，性能下降。
- **字段起始地址规则**：字段的起始地址必须是其自身大小的整数倍。
  - `INT4`（4 字节） → 起始地址为 `4` 的倍数（如 `0x00`, `0x04`, `0x08`）。
  - `TIMESTAMPTZ`（8 字节） → 起始地址为 `8` 的倍数（如 `0x00`, `0x08`, `0x10`）。
---
#### 2. 表结构 `(id INT4, created_at TIMESTAMPTZ)` 的存储布局
| 字段名       | 类型          | 实际占用 | 对齐填充 | 总占用 |
|--------------|---------------|----------|----------|--------|
| `id`         | `INT4`        | 4 字节   | **4 字节** | 8 字节 |
| `created_at` | `TIMESTAMPTZ` | 8 字节   | 0 字节   | 8 字节 |
**对齐填充原因**：
- `created_at` 需要从 `8 字节对齐地址` 开始。
- `id` 仅占用 4 字节，需在末尾填充 **4 字节空白**，使 `created_at` 的起始地址满足 `0x08`（假设 `id` 起始于 `0x00`）。
---
####  3. 转换为 `(id INT8, created_at TIMESTAMPTZ)` 后的存储布局
| 字段名       | 类型          | 实际占用 | 对齐填充 | 总占用 |
|--------------|---------------|----------|----------|--------|
| `id`         | `INT8`        | 8 字节   | 0 字节   | 8 字节 |
| `created_at` | `TIMESTAMPTZ` | 8 字节   | 0 字节   | 8 字节 |
**关键变化**：
- `id` 升级为 `INT8`（8 字节），直接满足 `8 字节对齐`，无需填充。
- `created_at` 起始地址自动对齐到 `0x08`（紧跟 `id` 的结束地址 `0x08`）。
- **总磁盘空间不变**：每行仍占用 **16 字节**（`8 + 8`）。
---
####  4. 对齐填充的意义
- **性能优化**：通过牺牲少量空间，避免 CPU 多次访问内存，提升数据读写效率。
- **空间权衡**：在示例中，`INT4 → INT8` 的字段升级并未增加总空间，因为原有填充已被预留。

