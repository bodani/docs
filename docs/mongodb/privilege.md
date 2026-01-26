# MongoDB 权限管理

## 权限模型

MongoDB 采用基于角色的权限管理 (RBAC - Role-Based Access Control) 模型，用户必须经过身份验证才能执行操作。

## 内置角色

### 数据库用户角色

- **read**: 读取权限，可以查看数据库中的数据
- **readWrite**: 读写权限，可以读写数据

### 数据库管理角色

- **dbAdmin**: 数据库管理员权限，执行管理任务
- **dbOwner**: 数据库所有者权限，结合 readWrite、dbAdmin 和 userAdmin 角色
- **userAdmin**: 用户管理员权限，负责管理用户和角色

### 集群管理角色

- **clusterAdmin**: 集群管理员，拥有最高级别的管理权限
- **clusterManager**: 集群管理权限
- **clusterMonitor**: 集群监控权限
- **hostManager**: 主机管理权限

### 备份与恢复角色

- **backup**: 备份权限
- **restore**: 恢复权限

### 全局角色

- **root**: 超级管理员角色，拥有所有数据库所有权限

## 用户管理

### 创建管理员账户

```javascript
// 切换到 admin 数据库
use admin

// 创建超级用户
db.createUser({
    user: "admin",
    pwd: "securePassword",
    roles: [{ role: "userAdminAnyDatabase", db: "admin" }]
})
```

### 为特定数据库创建用户

```javascript
创建用户示例
use admin
db.createUser({user: 'test', pwd: '123456Aa', roles:[{role: 'readWrite', db: 'mydb'}]})
```

### 身份验证

```bash
# 连接时认证
mongo -u username -p --authenticationDatabase databaseName

# 或者在数据库内部进行认证
db.auth("username", "password")
```

## 自定义角色

### 创建自定义角色

```javascript
// 在特定数据库中创建角色
use myDatabase

db.createRole({
    role: "customRole",
    privileges: [
        {
            resource: { db: "myDatabase", collection: "employees" },
            actions: [
                "find",
                "insert",
                "remove",
                "update"
            ]
        },
        {
            resource: { db: "myDatabase", collection: "" }, // 所有集合
            actions: [
                "listCollections",
                "collStats"
            ]
        }
    ],
    roles: []  // 可以继承其他角色
})
```

### 角色资源限定

```javascript
// 可以在不同级别指定权限资源
{
    resource: {
        db: "databaseName",         // 数据库名
        collection: "collectionName" // 集合名，空字符串表示整个数据库
    },
    actions: ["action1", "action2"] // 允许的操作列表
}
```

## 授权操作示例

### 授予角色

```javascript
// 为用户添加角色
db.grantRolesToUser("userName", [
  { role: "readWrite", db: "applicationDB" },
  { role: "read", db: "reportingDB" },
]);
```

### 回收角色

```javascript
// 从用户移除角色
db.revokeRolesFromUser("userName", [{ role: "readWrite", db: "oldDB" }]);
```

### 查看用户权限

```javascript
// 查看当前用户的权限
db.runCommand({ connectionStatus: 1 });

// 查看指定用户信息
db.getUser("userName");

// 查看所有用户
db.getUsers();

// 查看所有角色
db.getRoles({ rolesInfo: 1 });
```

## 安全最佳实践

### 网络安全

1. 启用认证
2. 使用 TLS/SSL 加密连接
3. 配置防火墙规则
4. 限制 bindIP 只接受必要来源

### 账户安全

1. 创建最小权限原则的用户账户
2. 定期轮换密码
3. 审计用户活动
4. 使用专用管理账户

### 操作安全

1. 定期审计授权变更
2. 监控未授权访问尝试
3. 使用只读用户进行查询操作
4. 定期审核账户和角色分配

## 常用管理命令

### 列出所有内置角色

```javascript
db.runCommand({ rolesInfo: 1, showBuiltinRoles: true });
```

### 查看角色详情

```javascript
db.getRole({ role: "roleName", db: "databaseName" }, { showPrivileges: true });
```

### 会话安全配置

在生产环境中强烈建议：

- 启用认证并使用强密码策略
- 使用角色而非特权用户进行日常操作
- 定期进行权限审查
- 审核和记录所有的授权更改
