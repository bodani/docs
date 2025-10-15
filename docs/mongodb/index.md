## 登录
```
mongosh -u root -p 1bg8NTU9k8 --host 127.0.0.1
```

## rs 副本集查看

```
rs.conf()
rs.status()
// 查看复制延迟
db.printSecondaryReplicationInfo();

// 检查 Oplog 窗口
rs.printReplicationInfo();

// 监控节点负载
db.serverStatus().locks;
db.serverStatus().globalLock;
```

## 用户管理

```
use admin
db.system.users.find()
创建用户
db.createUser({user: test, pwd: 123456Aa, roles:[{role: read, db: admin}]})
更新用户
db.updateUser('test', {
  roles: [{ role: 'readWrite', db: 'db002' }]  // 直接覆盖原有角色
});
查看用户
db.getUser('test');
```

## oplog
```
// 查看oplog
// 执行在任意副本集成员
rs.printReplicationInfo()
// 验证
// 切换到 local 数据库
use local

// 查看 oplog.rs 集合的物理大小（单位：字节）
db.oplog.rs.stats().maxSize
// 设置 oplog
db.adminCommand({ replSetResizeOplog: 1, size: 8192 });  // 设置为 8GB
```


INSERT INTO s_parking_exit_record VALUES('c9c267b8232f11f0b5c3bafceaf8868f','b830260af38711eca94aae2504c624f7','{210504, 210500}','1','tmp','辽ENF189','2025-04-27 16:21:35.983150+08:00','2025-04-27 16:50:14.762448+08:00')

