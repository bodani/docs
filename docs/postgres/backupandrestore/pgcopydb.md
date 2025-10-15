# 利用pgcopydb 进行数据迁移

## 背景

pgcopydb 主要是解决pg_dump | pg_restore 不落盘数据迁移的并行话问题。并支持单表的并行执行。

## 数据迁移

### 数据联通验证
```
$ pgcopydb ping --source="dbname=pagila" --target="postgres://user@target:5432/pagila"
```
### 离线数据迁移
```
pgcopydb clone
  --source                      Postgres URI to the source database
  --target                      Postgres URI to the target database
  --dir                         Work directory to use
  --table-jobs                  Number of concurrent COPY jobs to run
  --index-jobs                  Number of concurrent CREATE INDEX jobs to run
  --restore-jobs 
  --snapshot                    Use snapshot obtained with pg_export_snapshot
  --follow                      Implement logical decoding to replay changes
  --plugin                      Output plugin to use (test_decoding, wal2json)
  --verbose
```
####  用户，拓展同步

```
需要数据库超级用户部分, 也可以手动在target 库中执行。
# 
$ coproc ( pgcopydb snapshot --source)
# first two commands would use a superuser role to connect
$ pgcopydb copy roles --source ... --target ...
$ pgcopydb copy extensions --source ... --target ...
$ kill -TERM ${COPROC_PID}
$ wait ${COPROC_PID}
```
#### 数据迁移
```
普通用户即可
# 进行数据迁移
$ pgcopydb clone --dir=/tmp/pgcopydb-1 --table-jobs=10 --index-jobs=8 --restore-jobs=10 --skip-extensions --snapshot --source ... --target ...
# 删除快照
$ kill -TERM ${COPROC_PID}
$ wait ${COPROC_PID}
```

### CDC数据迁移

```
$ coproc ( pgcopydb snapshot )

$ pgcopydb stream setup

$ pgcopydb clone --follow --dir=/tmp/pgcopydb-1 --table-jobs=10 --index-jobs=8 --restore-jobs=10 --skip-extensions --snapshot --source ... --target ...&

# 查看主从延迟，当主从达到同步后可准备进行应用切换 

# 停应用
# 用于控制流式复制停止位置，使复制进程在处理完当前所有已接收的数据后自动停止
$ pgcopydb stream sentinel set endpos --current

# 同步序列
$ pgcopydb copy sequences

# 清理逻辑复制过程中所创建的资源，比如复制槽，订阅发布等
$ pgcopydb stream cleanup

 # 清理快照
$ kill -TERM ${COPROC_PID}
$ wait ${COPROC_PID}

应用接入新数据库
```

## 数据校验
```
$ pgcopydb compare schema
$ pgcopydb compare data
```

## 配置filter表过滤

https://pgcopydb.readthedocs.io/en/latest/ref/pgcopydb_config.html


## 数据迁移步骤说明

- 列出普通表，分区表，索引，序列
- 然后调用pg_dump 进入pre-data
- 利用pg_restore --use-list 进行过滤
- 并行copy data
- 大对象处理
- 并行创建索引，主键索引，现阶段为唯一索引
- 主键索引恢复
- vacuum analyze
- 循环同步序列

## 一个具体的迁移过程

apt-get install pgcopydb

测试结果 不能满足拓展不同版本的兼容性，在迁移function 的时候报错。改用原始的逻辑复制