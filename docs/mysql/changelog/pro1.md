## 问题1
客户端错误
Error: 2005 (HY000): Unknown MySQL server host 'localhost' (-11)
Error: 2005 (HY000): Unknown MySQL server host 'localhost' (-11)
Error: 2005 (HY000): Unknown MySQL server host 'localhost' (-11)
mysql服务 
|4508 | unauthenticated user | localhost:38414 | NULL | Connect |    1 | login                  | NULL             |
|24509 | unauthenticated user | localhost:38418 | NULL | Connect |    1 | login                  | NULL            |

mysql配置
max_connections
back_log=2000
服务器
ulimit -n
net.ipv4.tcp_max_syn_backlog

## 问题2
router 连接数


### ssl version
Error: 2026 (HY000): connecting to destination failed with TLS error: error:0A00010B:SSL routines::wrong version number
Error: 2026 (HY000): connecting to destination failed with TLS error: error:0A00010B:SSL routines::wrong version number

```
sudo apt-get update
sudo apt-get install --only-upgrade openssl
```

## mysql 安装 换存储目录

```
sudo ln -s /etc/apparmor.d/usr.sbin.mysqld /etc/apparmor.d/disable/
sudo apparmor_parser -R /etc/apparmor.d/usr.sbin.mysqld
```


innodb_log_writer_threads	ON
innodb_lru_scan_depth	1024
innodb_sort_buffer_size	1048576
innodb_write_io_threads	16
max_insert_delayed_threads	20
thread_cache_size	200
thread_handling	one-thread-per-connection
thread_stack	1048576
innodb_thread_concurrency	0
innodb_buffer_pool_chunk_size	134217728
innodb_buffer_pool_dump_at_shutdown	ON
innodb_buffer_pool_dump_now	OFF
innodb_buffer_pool_dump_pct	25
innodb_buffer_pool_filename	ib_buffer_pool
innodb_buffer_pool_in_core_file	ON
innodb_buffer_pool_instances	8
innodb_buffer_pool_load_abort	OFF
innodb_buffer_pool_load_at_startup	ON
innodb_buffer_pool_load_now	OFF
innodb_buffer_pool_size	22548578304

```
create database mx1;
create user 'user1'@'%' identified by '123456';
grant all on mx1.* to 'user1'@'%';
flush PRIVILEGES;
```


```
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for te_activate_info
-- ----------------------------
DROP TABLE IF EXISTS `te_activate_info`;
CREATE TABLE `te_activate_info` (
  `id` varchar(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `product_id` varchar(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  `device_no` varchar(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  `soft_ver` varchar(64) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  `act_code` varchar(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  `timeStamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `brd_source` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL COMMENT '来源',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 ROW_FORMAT=DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;
```


```
echo `date` && mysql -uroot -p123456 mx1 < /tmp/insert_te_activate_info.sql && echo `date`;
```

```
pip install mysql-connector-python
```

```
import mysql.connector
from mysql.connector import errorcode
import uuid
import random
import string
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from mysql.connector import pooling

# 数据库连接配置
config = {
  'user': 'mysql',
  'password': '123456',
  'host': '10.43.243.140',
  'database': 'mx1',
  'pool_name': 'mypool',
  'pool_size': 32
}

# 生成随机字符串
def random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


cnxpool = mysql.connector.pooling.MySQLConnectionPool(**config)
# 生成随机字符串
def random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


cnxpool = mysql.connector.pooling.MySQLConnectionPool(**config)

# 插入一条数据
def insert_data():
    try:
#        cnx = mysql.connector.connect(**config, ssl_disabled=False)
        cnx = cnxpool.get_connection()
        cursor = cnx.cursor()
        id = str(uuid.uuid4()).replace('-', '')
        product_id = random_string(32)
        device_no = random_string(32)
        soft_ver = random_string(64)
        act_code = random_string(32)
        brd_source = random_string(255)

        insert_sql = 
        INSERT INTO te_activate_info (id, product_id, device_no, soft_ver, act_code, brd_source)
        VALUES (%s, %s, %s, %s, %s, %s)
        
        cursor.execute(insert_sql, (id, product_id, device_no, soft_ver, act_code, brd_source))
        cnx.commit()
        cursor.close()
        cnx.close()
    except mysql.connector.Error as err:
        print(fError: {err})

# 记录开始时间
start_time = time.time()

# 并发插入数据
num_records = 1000
log_interval = 100
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(insert_data) for _ in range(num_records)]
    for i, future in enumerate(as_completed(futures)):
        if (i + 1) % log_interval == 0:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f'Inserted {(i + 1)} records at {current_time}')

# 记录结束时间
end_time = time.time()
total_time = end_time - start_time

print(fData insertion completed in {total_time:.2f} seconds.)
```

https://lore.kernel.org/all/9d59af25-d648-4777-a5c0-c38c246a9610@ewheeler.net/T/

https://juju.is/blog/using-bcache-for-performance-gains-on-the-launchpad-database-servers

