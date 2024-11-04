


pt-query-digest 

https://docs.percona.com/percona-toolkit

| 工具类别 | 工具命令                 | 工具作用                                   | 备注         |
|----------|--------------------------|--------------------------------------------|--------------|
| 开发类   | pt-duplicate-key-checker | 列出并删除重复的索引和外键                 | –            |
|          | pt-online-schema-change  | 在线修改表结构                             | –            |
|          | pt-query-advisor         | 分析查询语句，并给出建议，有bug            | 已废弃       |
|          | pt-show-grants           | 规范化和打印权限                           | –            |
|          | pt-upgrade               | 在多个服务器上执行查询，并比较不同         | –            |
| 性能类   | pt-index-usage           | 分析日志中索引使用情况，并出报告           | –            |
|          | pt-pmp                   | 为查询结果跟踪，并汇总跟踪结果             | –            |
|          | pt-visual-explain        | 格式化执行计划                             | –            |
|          | pt-table-usage           | 分析日志中查询并分析表使用情况             | pt 2.2新增命令 |
| 配置类   | pt-config-diff           | 比较配置文件和参数                         | –            |
|          | pt-mysql-summary         | 对mysql配置和status进行汇总                | –            |
|          | pt-variable-advisor      | 分析参数，并提出建议                       | –            |
| 监控类   | pt-deadlock-logger       | 提取和记录mysql死锁信息                    | –            |
|          | pt-fk-error-logger       | 提取和记录外键信息                         | –            |
|          | pt-mext                  | 并行查看status样本信息                     | –            |
|          | pt-query-digest          | 分析查询日志，并产生报告                   | 常用命令     |
|          | pt-trend                 | 按照时间段读取slow日志信息                 | 已废弃       |
| 复制类   | pt-heartbeat             | 监控mysql复制延迟                          | –            |
|          | pt-slave-delay           | 设定从落后主的时间                         | –            |
|          | pt-slave-find            | 查找和打印所有mysql复制层级关系            | –            |
|          | pt-slave-restart         | 监控salve错误，并尝试重启salve             | –            |
|          | pt-table-checksum        | 校验主从复制一致性                         | –            |
|          | pt-table-sync            | 高效同步表数据                             | –            |
| 系统类   | pt-diskstats             | 查看系统磁盘状态                           | –            |
|          | pt-fifo-split            | 模拟切割文件并输出                         | –            |
|          | pt-summary               | 收集和显示系统概况                         | –            |
|          | pt-stalk                 | 出现问题时，收集诊断数据                   | –            |
|          | pt-sift                  | 浏览由pt-stalk创建的文件                   | pt 2.2新增命令 |
|          | pt-ioprofile             | 查询进程IO并打印一个IO活动表               | pt 2.2新增命令 |
| 实用类   | pt-archiver              | 将表数据归档到另一个表或文件中             | –            |
|          | pt-find                  | 查找表并执行命令                           | –            |
|          | pt-kill                  | Kill掉符合条件的sql                        | 常用命令     |
|          | pt-align                 | 对齐其他工具的输出                         | pt 2.2新增命令 |
|          | pt-fingerprint           | 将查询转成密文                             | pt 2.2新增命令 |


## pt-align 列对齐


## pt-archiver 归档表数据 
注意事项， --source 后面的key=value，直接不要有空格
```
pt-archiver --source u=xxx,p=xxx,h=xx,P=3306,D=mysql,t=t  \
 --dest t=t1 \
 --file '/tmp/archive/%Y-%m-%d-%D.%t'                         \
 --where "id>64615 and id < 70000" --limit 1000 --commit-each --progress 1000 --sleep 1 --statistics
```

## pt-config-diff 配置文件比较
主从之间，或新旧之间
```
pt-config-diff  u=xxx,p=xxx,h=xx,P=3306 u=xxx,p=xxx,h=xx,P=3307
```

## pt-deadlock-logger 死锁检测

CREATE TABLE `wjqtab1` (
   `id` int(11) NOT NULL AUTO_INCREMENT,
   `a` int(11) DEFAULT NULL,
   `b` int(11) DEFAULT NULL,
   PRIMARY KEY (`id`),
   KEY `idxa` (`a`)
) ENGINE=InnoDB;

pt-diskstats 类似iostat

需要安装在服务端

## pt-duplicate-key-checker 统计重复索引

生成索引统计表，并给出删除重复索引建议的sql

## pt-index-usage 通过(慢)查询日志分析索引使用情况

