You are having performance issues with MySQL instances monitored by MySQL Enterprise Monitor. Using Query Analyzer, where do you begin to look for problem queries?

A) Look for queries with big prolonged spikes in row activity/access graph in the time series graph.
B) Sort the "Exec" column and check for SQL queries with high Query Response Time index (QRTi) values.
C) Look for queries with low total latency times in the Latency section in the time series graph.
   D) Sort the "Exec" column and check for SQL queries with low Query Response Time index (QRTi) values.

Examine the full path name of the backup image from MySQL Enterprise Backup with the --compress option:
/backup/full/mybackup/myimage.img

mysqlbackup.cnf contains:

[mysqlbackup]  
backup-dir=/backup/full/myrestore  
backup-image=/backup/full/mybackup/myimage.img uncompress

You must perform a database restore to a new machine. The data directory is /data/MEB.
Which command can provision the new database in datadir as /data/MEB?

A) mysqlbackup --defaults-file=mysqlbackup.cnf --datadir=/data/MEB restore-and-apply-log
B) mysqlbackup --defaults-file=mysqlbackup.cnf --datadir=/data/MEB image-to-dir-and-apply-log
C) mysqlbackup --defaults-file=mysqlbackup.cnf --datadir=/data/MEB apply-log-and-copy-back
  D) mysqlbackup --defaults-file=mysqlbackup.cnf --datadir=/data/MEB copy-back-and-apply-log
E) mysqlbackup --defaults-file=mysqlbackup.cnf --datadir=/data/MEB image-to-dir