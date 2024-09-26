# 物理备份

```
pg_basebackup -h 10.2.0.14 -U postgres -F p -P  -D /var/lib/pgsql/xx/data/ --checkpoint=fast -l postgresback2018
```