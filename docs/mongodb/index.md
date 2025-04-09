## 登录
```
mongosh -u root -p 1bg8NTU9k8 --host 127.0.0.1
```

## rs 副本集查看

```
rs.conf()
rs.status()
```

## 用户管理

```
use admin
db.system.users.find()

db.createUser({user: "test", pwd: "123456Aa", roles:[{role: "read", db: "admin"}]})
```