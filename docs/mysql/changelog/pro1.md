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
DROP TABLE IF EXISTS `te_activate_info`;
CREATE TABLE `te_activate_info` (
  `new_id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `id` varchar(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `product_id` varchar(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  `device_no` varchar(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  `soft_ver` varchar(64) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  `act_code` varchar(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  `timeStamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `brd_source` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL COMMENT '来源'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 ROW_FORMAT=DYNAMIC;
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

        insert_sql = """
        INSERT INTO te_activate_info (id, product_id, device_no, soft_ver, act_code, brd_source)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_sql, (id, product_id, device_no, soft_ver, act_code, brd_source))
        cnx.commit()
        cursor.close()
        cnx.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

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

print(f"Data insertion completed in {total_time:.2f} seconds.")
```

```
apiVersion: v1
kind: Pod
metadata:
  name: mypod1
  namespace: mxdrt

spec:
  containers:
    - name: myfrontend
      image: busybox
      args:
        - sleep infinity
      command:
        - /bin/sh
        - -c
      volumeMounts:
      - mountPath: "/data"
        name: mypd
  volumes:
    - name: mypd
      persistentVolumeClaim:
        claimName: data-helmbroker-mysql-zj-3
```

fio --name=write_test --directory=/data/mysql1/mysql/ --ioengine=libaio --iodepth=32 --rw=write --bs=4k --direct=1 --size=10G --numjobs=4 --runtime=600 --group_reporting


随机读写

fio --name=write_test --directory=/data/mysql1/mysql/ --ioengine=libaio --iodepth=32 --rw=randrw --rwmixread=70 --bs=4k --direct=1 --size=1G --numjobs=4 --runtime=60 --group_reporting


本机ssd 9分
read: IOPS=23.0k, BW=89.8MiB/s (94.2MB/s)(2864MiB/31882msec)
write: IOPS=9889, BW=38.6MiB/s (40.5MB/s)(1232MiB/31882msec); 0 zone resets

本机nvme 4：30
read: IOPS=72.8k, BW=284MiB/s (298MB/s)(2864MiB/10075msec)
write: IOPS=31.3k, BW=122MiB/s (128MB/s)(1232MiB/10075msec); 0 zone resets

服务器nvme 1：30
read: IOPS=115k, BW=450MiB/s (472MB/s)(2864MiB/6365msec)
write: IOPS=49.5k, BW=194MiB/s (203MB/s)(1232MiB/6365msec); 0 zone resets

read: IOPS=388k, BW=1516MiB/s (1590MB/s)(2864MiB/1889msec)
write: IOPS=167k, BW=652MiB/s (684MB/s)(1232MiB/1889msec); 0 zone resets

服务器 bcache
read: IOPS=126k, BW=492MiB/s (516MB/s)(2864MiB/5821msec)
write: IOPS=54.2k, BW=212MiB/s (222MB/s)(1232MiB/5821msec); 0 zone resets
write: IOPS=26.3k, BW=103MiB/s (108MB/s)(40.0GiB/399073msec); 0 zone resets
```
podman run \
    -e MYSQL_ROOT_PASSWORD=123456 \
    -p 3307:3306 \
    -v /data/mysql1/mysql2:/drycc/mysql/data \
    registry.drycc.cc/drycc-addons/mysql:8.0


podman run \
    -e MYSQL_ROOT_PASSWORD=123456 \
    -p 3307:3306 \
    -v /data/mysql/data:/drycc/mysql/data \
    registry.drycc.cc/drycc-addons/mysql:8.0
```

bcache
```
fio --name=write_test --directory=/data/mysql/ --ioengine=libaio --iodepth=32 --rw=randrw --rwmixread=70 --bs=4k --direct=1 --size=10G --numjobs=4 --runtime=600 --group_reporting
write_test: (g=0): rw=randrw, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=32
...
fio-3.28
Starting 4 processes
write_test: Laying out IO file (1 file / 10240MiB)
write_test: Laying out IO file (1 file / 10240MiB)
write_test: Laying out IO file (1 file / 10240MiB)
write_test: Laying out IO file (1 file / 10240MiB)
Jobs: 2 (f=2): [_(1),m(1),_(1),m(1)][100.0%][r=386MiB/s,w=165MiB/s][r=98.8k,w=42.2k IOPS][eta 00m:00s]
write_test: (groupid=0, jobs=4): err= 0: pid=2641279: Tue Dec 17 09:58:31 2024
  read: IOPS=117k, BW=459MiB/s (481MB/s)(28.0GiB/62472msec)
    slat (usec): min=5, max=15209, avg=14.32, stdev=44.64
    clat (usec): min=48, max=16050, avg=747.07, stdev=229.33
     lat (usec): min=65, max=16065, avg=763.22, stdev=233.75
    clat percentiles (usec):
     |  1.00th=[  635],  5.00th=[  676], 10.00th=[  685], 20.00th=[  701],
     | 30.00th=[  709], 40.00th=[  717], 50.00th=[  725], 60.00th=[  734],
     | 70.00th=[  742], 80.00th=[  750], 90.00th=[  775], 95.00th=[  799],
     | 99.00th=[ 1090], 99.50th=[ 2737], 99.90th=[ 3326], 99.95th=[ 3458],
     | 99.99th=[ 5604]
   bw (  KiB/s): min=403576, max=514065, per=100.00%, avg=473673.89, stdev=3957.30, samples=493
   iops        : min=100894, max=128515, avg=118418.20, stdev=989.30, samples=493
  write: IOPS=50.4k, BW=197MiB/s (206MB/s)(12.0GiB/62472msec); 0 zone resets
    slat (usec): min=5, max=14307, avg=14.64, stdev=26.45
    clat (usec): min=54, max=15974, avg=705.24, stdev=234.11
     lat (usec): min=86, max=15990, avg=721.70, stdev=235.65
    clat percentiles (usec):
     |  1.00th=[  611],  5.00th=[  635], 10.00th=[  644], 20.00th=[  660],
     | 30.00th=[  668], 40.00th=[  676], 50.00th=[  685], 60.00th=[  693],
     | 70.00th=[  701], 80.00th=[  709], 90.00th=[  725], 95.00th=[  734],
     | 99.00th=[ 1254], 99.50th=[ 2704], 99.90th=[ 3294], 99.95th=[ 3425],
     | 99.99th=[ 5866]
   bw (  KiB/s): min=174848, max=220966, per=100.00%, avg=203077.05, stdev=1764.52, samples=493
   iops        : min=43712, max=55241, avg=50769.01, stdev=441.11, samples=493
  lat (usec)   : 50=0.01%, 100=0.01%, 250=0.01%, 500=0.14%, 750=83.51%
  lat (usec)   : 1000=15.12%
  lat (msec)   : 2=0.38%, 4=0.82%, 10=0.01%, 20=0.01%
  cpu          : usr=5.02%, sys=92.34%, ctx=32921, majf=0, minf=398
  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=100.0%, >=64=0.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.1%, 64=0.0%, >=64=0.0%
     issued rwts: total=7339210,3146550,0,0 short=0,0,0,0 dropped=0,0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=32

Run status group 0 (all jobs):
   READ: bw=459MiB/s (481MB/s), 459MiB/s-459MiB/s (481MB/s-481MB/s), io=28.0GiB (30.1GB), run=62472-62472msec
  WRITE: bw=197MiB/s (206MB/s), 197MiB/s-197MiB/s (206MB/s-206MB/s), io=12.0GiB (12.9GB), run=62472-62472msec

Disk stats (read/write):
    dm-1: ios=7332727/3143693, merge=0/0, ticks=648824/107632, in_queue=756456, util=99.84%, aggrios=7339210/3146568, aggrmerge=0/0, aggrticks=637440/102672, aggrin_queue=740112, aggrutil=99.74%
    bcache0: ios=7339210/3146568, merge=0/0, ticks=637440/102672, in_queue=740112, util=99.74%, aggrios=3784388/1641244, aggrmerge=0/1, aggrticks=316862/24631, aggrin_queue=341506, aggrutil=99.73%
  sdb: ios=0/124, merge=0/0, ticks=0/142, in_queue=168, util=0.21%
  nvme0n1: ios=7568776/3282365, merge=0/3, ticks=633725/49120, in_queue=682845, util=99.73%
```
```
fio --name=write_test --directory=/var/lib/rancher/mysql/data/ --ioengine=libaio --iodepth=32 --rw=randrw --rwmixread=70 --bs=4k --direct=1 --size=10G --numjobs=4 --runtime=600 --group_reporting
write_test: (g=0): rw=randrw, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=32
...
fio-3.28
Starting 4 processes
write_test: Laying out IO file (1 file / 10240MiB)
write_test: Laying out IO file (1 file / 10240MiB)
write_test: Laying out IO file (1 file / 10240MiB)
write_test: Laying out IO file (1 file / 10240MiB)
Jobs: 2 (f=2): [m(2),_(2)][98.5%][r=298MiB/s,w=128MiB/s][r=76.3k,w=32.7k IOPS][eta 00m:01s]
write_test: (groupid=0, jobs=4): err= 0: pid=2648208: Tue Dec 17 10:54:29 2024
  read: IOPS=115k, BW=449MiB/s (471MB/s)(28.0GiB/63845msec)
    slat (usec): min=4, max=243, avg=11.21, stdev= 2.15
    clat (usec): min=45, max=2692, avg=756.13, stdev=49.80
     lat (usec): min=59, max=2703, avg=769.29, stdev=50.03
    clat percentiles (usec):
     |  1.00th=[  652],  5.00th=[  693], 10.00th=[  709], 20.00th=[  725],
     | 30.00th=[  734], 40.00th=[  742], 50.00th=[  758], 60.00th=[  766],
     | 70.00th=[  775], 80.00th=[  791], 90.00th=[  807], 95.00th=[  824],
     | 99.00th=[  914], 99.50th=[  971], 99.90th=[ 1074], 99.95th=[ 1123],
     | 99.99th=[ 1401]
   bw (  KiB/s): min=439152, max=530953, per=100.00%, avg=467663.35, stdev=2808.74, samples=500
   iops        : min=109788, max=132738, avg=116915.83, stdev=702.15, samples=500
  write: IOPS=49.3k, BW=193MiB/s (202MB/s)(12.0GiB/63845msec); 0 zone resets
    slat (usec): min=8, max=706, avg=18.21, stdev= 3.54
    clat (usec): min=42, max=19318, avg=722.49, stdev=100.29
     lat (usec): min=66, max=19342, avg=743.42, stdev=100.70
    clat percentiles (usec):
     |  1.00th=[  627],  5.00th=[  660], 10.00th=[  676], 20.00th=[  693],
     | 30.00th=[  701], 40.00th=[  709], 50.00th=[  725], 60.00th=[  734],
     | 70.00th=[  742], 80.00th=[  750], 90.00th=[  766], 95.00th=[  783],
     | 99.00th=[  807], 99.50th=[  816], 99.90th=[  857], 99.95th=[ 1205],
     | 99.99th=[ 5997]
   bw (  KiB/s): min=187824, max=228640, per=100.00%, avg=200507.13, stdev=1235.11, samples=500
   iops        : min=46956, max=57159, avg=50126.74, stdev=308.74, samples=500
  lat (usec)   : 50=0.01%, 100=0.01%, 250=0.01%, 500=0.21%, 750=55.15%
  lat (usec)   : 1000=44.39%
  lat (msec)   : 2=0.24%, 4=0.01%, 10=0.01%, 20=0.01%
  cpu          : usr=5.29%, sys=94.51%, ctx=106321, majf=0, minf=234
  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=100.0%, >=64=0.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.1%, 64=0.0%, >=64=0.0%
     issued rwts: total=7339210,3146550,0,0 short=0,0,0,0 dropped=0,0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=32

Run status group 0 (all jobs):
   READ: bw=449MiB/s (471MB/s), 449MiB/s-449MiB/s (471MB/s-471MB/s), io=28.0GiB (30.1GB), run=63845-63845msec
  WRITE: bw=193MiB/s (202MB/s), 193MiB/s-193MiB/s (202MB/s-202MB/s), io=12.0GiB (12.9GB), run=63845-63845msec

Disk stats (read/write):
    md0: ios=7333426/3144184, merge=0/0, ticks=527320/66216, in_queue=593536, util=100.00%, aggrios=3669670/3147030, aggrmerge=0/12, aggrticks=259827/47713, aggrin_queue=307540, aggrutil=99.92%
  nvme0n1: ios=3713234/3147031, merge=0/12, ticks=268556/61897, in_queue=330452, util=99.92%
  nvme1n1: ios=3626106/3147029, merge=0/12, ticks=251099/33530, in_queue=284629, util=99.92%
```

bcache IO stat
```
Device            r/s     rMB/s   rrqm/s  %rrqm r_await rareq-sz     w/s     wMB/s   wrqm/s  %wrqm w_await wareq-sz     d/s     dMB/s   drqm/s  %drqm d_await dareq-sz     f/s f_await  aqu-sz  %util
dm-1             0.00      0.00     0.00   0.00    0.00     0.00 1323.00      4.67     0.00   0.00    0.76     3.61    0.00      0.00     0.00   0.00    0.00     0.00    0.00    0.00    1.00 100.00


Device            r/s     rMB/s   rrqm/s  %rrqm r_await rareq-sz     w/s     wMB/s   wrqm/s  %wrqm w_await wareq-sz     d/s     dMB/s   drqm/s  %drqm d_await dareq-sz     f/s f_await  aqu-sz  %util
dm-1             0.00      0.00     0.00   0.00    0.00     0.00 1313.00      4.56     0.00   0.00    0.75     3.56    0.00      0.00     0.00   0.00    0.00     0.00    0.00    0.00    0.98  97.20


Device            r/s     rMB/s   rrqm/s  %rrqm r_await rareq-sz     w/s     wMB/s   wrqm/s  %wrqm w_await wareq-sz     d/s     dMB/s   drqm/s  %drqm d_await dareq-sz     f/s f_await  aqu-sz  %util
dm-1             0.00      0.00     0.00   0.00    0.00     0.00 1325.00      4.62     0.00   0.00    0.76     3.57    0.00      0.00     0.00   0.00    0.00     0.00    0.00    0.00    1.01 100.00


```

```
Device            r/s     rMB/s   rrqm/s  %rrqm r_await rareq-sz     w/s     wMB/s   wrqm/s  %wrqm w_await wareq-sz     d/s     dMB/s   drqm/s  %drqm d_await dareq-sz     f/s f_await  aqu-sz  %util
bcache0          0.00      0.00     0.00   0.00    0.00     0.00 34241.00    133.75     0.00   0.00    0.03     4.00    0.00      0.00     0.00   0.00    0.00     0.00    0.00    0.00    1.17 100.00
```

https://lore.kernel.org/all/9d59af25-d648-4777-a5c0-c38c246a9610@ewheeler.net/T/

https://juju.is/blog/using-bcache-for-performance-gains-on-the-launchpad-database-servers