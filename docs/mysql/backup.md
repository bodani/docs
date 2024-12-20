# 数据备份与恢复

## 物理备份

xtrabackup

## 逻辑备份

mysqldump

mydumper

mysqlsh

SELECT car_id, timestamp
INTO OUTFILE '/tmp/mx_task_data.csv'
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n'
FROM mx_task_picture_info;