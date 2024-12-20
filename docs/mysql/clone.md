# Clone Plugin

introduced in MySQL 8.0.17

- donor 上游数据源 
- recipient 下游接收端
## 安装

```
mysql> show variables like 'plugin_dir';
+---------------+------------------------+
| Variable_name | Value                  |
+---------------+------------------------+
| plugin_dir    | /usr/lib/mysql/plugin/ |
+---------------+------------------------+
1 row in set (0.00 sec)

```

### 启动时安装
```
[mysqld]
plugin-load-add=mysql_clone.so
```

### 运行时安装
```
mysql> INSTALL PLUGIN clone SONAME 'mysql_clone.so';
```

验证
```
mysql>  SELECT PLUGIN_NAME, PLUGIN_STATUS
    ->        FROM INFORMATION_SCHEMA.PLUGINS
    ->        WHERE PLUGIN_NAME = 'clone';
+-------------+---------------+
| PLUGIN_NAME | PLUGIN_STATUS |
+-------------+---------------+
| clone       | ACTIVE        |
+-------------+---------------+
```

用户权限
```
GRANT BACKUP_ADMIN ON *.* TO 'clone_user';
```

## Local clone

### 模拟数据

```
CREATE DATABASE example_db;
USE example_db;

CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    position VARCHAR(100),
    salary DECIMAL(10, 2)
);

INSERT INTO employees (name, position, salary) VALUES
('Alice', 'Developer', 90000.00),
('Bob', 'Manager', 120000.00),
('Charlie', 'Analyst', 70000.00);
```

### clone 

```
sudo mkdir /path/to/clone_directory
sudo chown mysql:mysql /path/to/clone_directory
```

```
CLONE LOCAL DATA DIRECTORY = '/path/to/clone_directory/mysql';
```

###  验证克隆操作
克隆操作完成后，可以通过以下命令检查克隆状态和进度：

```
sql
-- 检查克隆状态
SELECT * FROM performance_schema.clone_status;

-- 检查克隆进度
SELECT * FROM performance_schema.clone_progress;
```
### 使用克隆的数据

假设需要使用克隆的数据，可以停止 MySQL 服务器并将克隆的数据目录替换为当前数据目录：
```
$> mysqld_safe --datadir=clone_dir
```

## Remote clone

#### donor 

用户需要 `BACKUP_ADMIN` 权限
```
mysql> CREATE USER 'donor_clone_user'@'example.donor.host.com' IDENTIFIED BY 'password';
mysql> GRANT BACKUP_ADMIN on *.* to 'donor_clone_user'@'example.donor.host.com';
```
安装clone插件
```
INSTALL PLUGIN clone SONAME 'mysql_clone.so';
```

#### recipient

用户需要 `CLONE_ADMIN` 权限 , `CLONE_ADMIN` 权限包括 `BACKUP_ADMIN` 和 `SHUTDOWN`

```
mysql> CREATE USER 'recipient_clone_user'@'example.recipient.host.com' IDENTIFIED BY 'password';
mysql> GRANT CLONE_ADMIN on *.* to 'recipient_clone_user'@'example.recipient.host.com';
```
在clone完成后，接受端会执行shutdown

安装clone插件
```
mysql> INSTALL PLUGIN clone SONAME 'mysql_clone.so';
```
配置donor 地址
```
mysql> SET GLOBAL clone_valid_donor_list = 'example.donor.host.com:3306';
```
#### clone语法
```
CLONE INSTANCE FROM 'user'@'host':port
IDENTIFIED BY 'password'
[DATA DIRECTORY [=] 'clone_dir']
[REQUIRE [NO] SSL];
```
clone操作会首先清理本地数据，包括(schemas, tables, tablespaces) 和 binary logs。

```
CLONE INSTANCE FROM 'myuser'@'10.1.40.84':3306 IDENTIFIED BY 'mypassword';
```

### 注意事项 
#### DDL

MySQL 8.0.27 版本之前会堵塞。 `clone_ddl_timeout=300` 秒

MySQL 8.0.27 版本之后支持并行执行，`clone_block_ddl=OFF` 

#### 数据库版本

 8.0.17 版本开始支持 clone ,8.0.37 前版本必须一致。

```
mysql> SHOW VARIABLES LIKE 'version';
```

####  system block sizes 

保持一致
```
stat -f -c '%s' /
或
sudo blockdev --getbsz /dev/sda1
```

### 状态查看

```
mysql> SELECT STATE FROM performance_schema.clone_status;
```

```
SELECT *  FROM performance_schema.clone_progress;
```

```
SELECT NAME,ENABLED FROM performance_schema.setup_instruments
       WHERE NAME LIKE '%clone%';
```
