## 当前所有MDL锁等待状态
```
SELECT 
  ml.OBJECT_SCHEMA, 
  ml.OBJECT_NAME, 
  ml.LOCK_TYPE, 
  ml.LOCK_STATUS,
  t.PROCESSLIST_ID AS 'ClientID',
  t.PROCESSLIST_USER AS 'User',
  t.PROCESSLIST_HOST AS 'Host',
  t.THREAD_ID AS 'InternalThreadID'  
FROM performance_schema.metadata_locks ml
JOIN performance_schema.threads t 
  ON ml.OWNER_THREAD_ID = t.THREAD_ID
WHERE ml.LOCK_STATUS = 'PENDING';
```

## 阻塞关系的完整链条
```
SELECT 
  CONCAT('连接', blocked.PROCESSLIST_ID) AS '被阻塞连接',
  CONCAT(blocked.PROCESSLIST_USER, '@', blocked.PROCESSLIST_HOST) AS '用户',
  blocked.PROCESSLIST_DB AS '数据库',
  blocked.PROCESSLIST_INFO AS '被阻塞SQL',
  CONCAT('阻塞者', blocking.PROCESSLIST_ID) AS '阻塞连接',
  blocking.PROCESSLIST_INFO AS '阻塞SQL',
  TIMEDIFF(NOW(), FROM_UNIXTIME(blocked.PROCESSLIST_TIME)) AS '阻塞时长'
FROM performance_schema.metadata_locks blocked_ml
JOIN performance_schema.threads blocked 
  ON blocked_ml.OWNER_THREAD_ID = blocked.THREAD_ID
JOIN performance_schema.metadata_locks blocking_ml 
  ON blocked_ml.OBJECT_SCHEMA = blocking_ml.OBJECT_SCHEMA
  AND blocked_ml.OBJECT_NAME = blocking_ml.OBJECT_NAME
  AND blocking_ml.LOCK_STATUS = 'GRANTED'
JOIN performance_schema.threads blocking 
  ON blocking_ml.OWNER_THREAD_ID = blocking.THREAD_ID
WHERE blocked_ml.LOCK_STATUS = 'PENDING';
```

## 快速处理
```
SELECT 
  t.PROCESSLIST_ID AS '连接ID',
  CONCAT(t.PROCESSLIST_USER, '@', t.PROCESSLIST_HOST) AS '用户',
  ml.OBJECT_SCHEMA AS '数据库',
  ml.OBJECT_NAME AS '表名',
  ml.LOCK_TYPE AS '锁类型',
  TIMEDIFF(NOW(), FROM_UNIXTIME(t.PROCESSLIST_TIME)) AS '等待时间',
  t.PROCESSLIST_INFO AS '被阻塞SQL',
  CONCAT('KILL ', t.PROCESSLIST_ID, ';') AS '终止命令'
FROM performance_schema.metadata_locks ml
JOIN performance_schema.threads t 
  ON ml.OWNER_THREAD_ID = t.THREAD_ID
WHERE ml.LOCK_STATUS = 'PENDING'
ORDER BY t.PROCESSLIST_TIME DESC;
```
