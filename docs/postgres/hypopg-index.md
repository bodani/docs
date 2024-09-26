 
# PostgreSQL 中的假设索引 
[github](https://github.com/HypoPG/hypopg)

## 背景
数据库中索引对性能的影响至关重要。往往采用创建新的索引的方式来优化现有数据库。

测试环境通常与正式环境的数据量数据分布不同，在测试环境中索引效果不能完全代表真实的运行环境索引的效果。
但是创建一个索引会占用系统的资源并且需要一定的时间。对正在运行的系统会带来额外的压力。
如果新的索引并不理想或不生，再把索引删除效岂不是既费时有费力，对线上运行的数据库也不友好。

创建假设索引几乎不需要占用系统的资源，本质上是利用数据库的统计信息来模拟索引使用的效果。

创建完成后可通过explain 来验证索引，预先了解新索引的使用效果。


### 安装

- RHEL/Rocky Linux
```
yum install hypopg
```
- Debian / Ubuntu
```
#  XY is the major version
apt install postgresql-XY-hypopg
```
- 源码安装
```
wget https://github.com/HypoPG/hypopg/archive/master.zip

unzip master.zip
cd hypopg-master

make
sudo make install

make install
```

## 介绍
HypoPG 创建的索引 只存在当前连接的私有内存中，不会影响到任何其他运行中的连接。



## 支持
- btree
- brin
- hash (requires PostgreSQL 10 or above)
- bloom (requires the bloom extension to be installed)

## 使用

#### 创建
```
CREATE EXTENSION hypopg ;
\dx
                     List of installed extensions
  Name   | Version |   Schema   |             Description
---------+---------+------------+-------------------------------------
 hypopg  | 1.1.0   | public     | Hypothetical indexes for PostgreSQL
```

#### 示例

##### 创建测试数据表
```
CREATE TABLE hypo (id integer, val text) ;
INSERT INTO hypo SELECT i, 'line ' || i FROM generate_series(1, 100000) i ;
VACUUM ANALYZE hypo ;
```

##### 执行计划
```
EXPLAIN SELECT val FROM hypo WHERE id = 1;
                       QUERY PLAN
--------------------------------------------------------
 Seq Scan on hypo  (cost=0.00..1791.00 rows=1 width=14)
   Filter: (id = 1)
(2 rows)
```
##### 创建假设索引
```
SELECT * FROM hypopg_create_index('CREATE INDEX ON hypo (id)') ;
 indexrelid |      indexname
------------+----------------------
      18284 | <18284>btree_hypo_id
(1 row)

```
##### 执行计划
```
EXPLAIN SELECT val FROM hypo WHERE id = 1;
                                    QUERY PLAN
----------------------------------------------------------------------------------
 Index Scan using <18284>btree_hypo_id on hypo  (cost=0.04..8.06 rows=1 width=10)
   Index Cond: (id = 1)
(2 rows)
```

```
EXPLAIN ANALYZE SELECT val FROM hypo WHERE id = 1;
                                            QUERY PLAN
---------------------------------------------------------------------------------------------------
 Seq Scan on hypo  (cost=0.00..1791.00 rows=1 width=10) (actual time=0.046..46.390 rows=1 loops=1)
   Filter: (id = 1)
   Rows Removed by Filter: 99999
 Planning time: 0.160 ms
 Execution time: 46.460 ms
(5 rows)
```

## 管理假设索引
- hypopg_list_indexes: 查看索引列表
```
SELECT * FROM hypopg_list_indexes ;
 indexrelid |      index_name       | schema_name | table_name | am_name
------------+-----------------------+-------------+------------+---------
      18284 | <18284>btree_hypo_id  | public      | hypo       | btree
(1 row)
```
- hypopg_get_indexdef: 查看索引定义
```
SELECT index_name, hypopg_get_indexdef(indexrelid) FROM hypopg_list_indexes ;
      index_name       |             hypopg_get_indexdef
-----------------------+----------------------------------------------
 <18284>btree_hypo_id  | CREATE INDEX ON public.hypo USING btree (id)
(1 row)
```
- hypopg_relation_size: 查看大小
```
SELECT index_name, pg_size_pretty(hypopg_relation_size(indexrelid))
  FROM hypopg_list_indexes ;
```
- hypopg_drop_index: 删除一个索引
- hypopg_reset: 清空所有索引

## 隐藏索引（同样很有用）

##### 创建真实索引
```
SELECT hypopg_reset();
CREATE INDEX ON hypo(id);
CREATE INDEX ON hypo(id, val);
```

##### 隐藏索引
```
EXPLAIN SELECT * FROM hypo WHERE id = 1;
                                    QUERY PLAN
----------------------------------------------------------------------------------
Index Only Scan using hypo_id_val_idx on hypo  (cost=0.29..8.30 rows=1 width=13)
Index Cond: (id = 1)
(2 rows)

```

```
SELECT hypopg_hide_index('hypo_id_val_idx'::REGCLASS);
 hypopg_hide_index
-------------------
t
(1 row)

EXPLAIN SELECT * FROM hypo WHERE id = 1;
                            QUERY PLAN
-------------------------------------------------------------------------
Index Scan using hypo_id_idx on hypo  (cost=0.29..8.30 rows=1 width=13)
Index Cond: (id = 1)
(2 rows)
```

##### 隐藏索引
```
SELECT hypopg_hide_index('hypo_id_idx'::REGCLASS);
 hypopg_hide_index
-------------------
t
(1 row)

EXPLAIN SELECT * FROM hypo WHERE id = 1;
                    QUERY PLAN
-------------------------------------------------------
Seq Scan on hypo  (cost=0.00..180.00 rows=1 width=13)
Filter: (id = 1)
(2 rows)
```
##### 取消隐藏索引
```
SELECT hypopg_unhide_index('hypo_id_idx'::regclass);
 hypopg_unhide_index
-------------------
t
(1 row)

EXPLAIN SELECT * FROM hypo WHERE id = 1;
                            QUERY PLAN
-------------------------------------------------------------------------
Index Scan using hypo_id_idx on hypo  (cost=0.29..8.30 rows=1 width=13)
Index Cond: (id = 1)
(2 rows)
```

##### 查看被隐藏的索引
```
SELECT * FROM hypopg_hidden_indexes();
 indexid
---------
526604
(1 rows)
```
##### 取消所有被隐藏的索引
```
hypopg_unhide_all_index()
```