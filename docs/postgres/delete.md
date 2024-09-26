# 删除数据

#### 删除数据 DELETE|UPDATE LIMIT

对数据进行归档完毕后，对数据进行清理。

postgres 暂不支持 delete limit 用法 。根据条件删除大量数据时。

使用with模拟必须有PK或者非空UK

```
with t1 as (select id from t where create_time < '2020-01-01 00:00:00' limit 10) 
                  delete from t where id in (select * from t1);
```


#### 表之间依赖顺序

```
with recursive fk_tree as (
  -- All tables not referencing anything else
  select t.oid as reloid, 
         t.relname as table_name, 
         s.nspname as schema_name,
         null::text as referenced_table_name,
         null::text as referenced_schema_name,
         1 as level
  from pg_class t
    join pg_namespace s on s.oid = t.relnamespace
  where relkind = 'r'
    and not exists (select *
                    from pg_constraint
                    where contype = 'f'
                      and conrelid = t.oid)
    and s.nspname = 'public' -- limit to one schema 

  union all 

  select ref.oid, 
         ref.relname, 
         rs.nspname,
         p.table_name,
         p.schema_name,
         p.level + 1
  from pg_class ref
    join pg_namespace rs on rs.oid = ref.relnamespace
    join pg_constraint c on c.contype = 'f' and c.conrelid = ref.oid
    join fk_tree p on p.reloid = c.confrelid
  where ref.oid != p.reloid  -- do not enter to tables referencing theirselves.
), all_tables as (
  -- this picks the highest level for each table
  select schema_name, table_name,
         level, 
         row_number() over (partition by schema_name, table_name order by level desc) as last_table_row
  from fk_tree
)
select schema_name, table_name, level
from all_tables at
where last_table_row = 1
order by level;
```

#### 删除后磁盘空间释放

删除大量数据后`analyze`及时更新数据统计信息 

如需回收删除数据所占用的空间 `vacuum full` , 注意事项，`·会锁·`，影响线上业务


无锁方式，参考

- pg_repack
