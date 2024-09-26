# mysqlslap


## 自定义sql
```
# cat create.sql
CREATE TABLE IF NOT EXISTS simple_table (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    age INT, 
    email VARCHAR(100)
);

INSERT INTO simple_table (name, age, email) VALUES ('张三', 25, 'zhangsan@example.com');
INSERT INTO simple_table (name, age, email) VALUES ('李四', 28, 'lisi@example.com');
INSERT INTO simple_table (name, age, email) VALUES ('王五', 22, 'wangwu@example.com');
```

```
# cat query.sql
select * from simple_table;
```

## 压测
```
mysqlslap --delimiter=";" --concurrency=50 --iterations=10 --engine=innodb --create-schema=mydb \
--create=create.sql --query=query.sql ENGINE=INNODB  -uroot -pxxxx -h xxx
```
