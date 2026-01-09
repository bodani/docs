# 利用 wal-g 管理数据库备份和恢复

## 存储服务 minio

设置用户名和密码

```
docker run -d -p 9000:9000 -e MINIO_ACCESS_KEY=xxxxx(changeme) -e MINIO_SECRET_KEY=kkkkk(changeme)  -v /data/minio/:/data  minio/minio server /data
```

创建 bucket

```
mc mb local/buecket003
```

## wal-g 下载

```
wget https://github.com/wal-g/wal-g/releases/download/v0.2.9/wal-g.linux-amd64.tar.gz

tar -zxvf wal-g.linux-amd64.tar.gz
```

## 设置环境变量

minio

cat wal-g.env

```
export PGDATA=/var/lib/pgsql/10/data/
export WALG_S3_PREFIX=s3://bucket003/
export PGPORT=5432
export PGUSER=postgres
export AWS_SECRET_ACCESS_KEY=xxxxx(changeme)
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=kkkkk(changeme)
export AWS_ENDPOINT=http://localhost:9000
export AWS_S3_FORCE_PATH_STYLE=true
```

swift

```
export PGDATA=
export WALG_SWIFT_PREFIX=swift://buckt003/
export PGPORT=
export PGUSER=
export OS_USERNAME=
export OS_PASSWORD=
export OS_AUTH_URL=http://ip:port/auth/v1.0
```

## 数据备份

### 全量备份

定时任务，周期备份全量数据

```
source mydir/wal-g.env &&  wal-g  backup-push $PGDATA
```

### wal 日志备份

设置数据库配置文件，备份 wal 日志文件

```
archive_mode = on ## 从库 always
archive_command = 'source mydir/wal-g.env &&  wal-g wal-push %p'
archive_timeout = 60
```

## 恢复数据

### 查看所有全备份

```
wal-g backup-list
name                          last_modified        wal_segment_backup_start
base_000000020000001E000000CB 2019-11-07T01:34:08Z 000000020000001E000000CB
base_000000020000001E000000CD 2019-11-07T01:37:03Z 000000020000001E000000CD
base_000000020000001E000000CF 2019-11-07T02:23:34Z 000000020000001E000000CF
base_000000020000001E000000D1 2019-11-07T02:31:00Z 000000020000001E000000D1
base_000000020000001E000000D3 2019-11-07T02:38:29Z 000000020000001E000000D3
base_000000020000001E000000DA 2019-11-07T06:08:19Z 000000020000001E000000DA
base_000000020000001E000000DD 2019-11-07T06:30:24Z 000000020000001E000000DD
base_000000020000001E000000DF 2019-11-07T08:45:30Z 000000020000001E000000DF
```

### 下载一个全备份

最近的一个全备份可用 LATEST 表示

```
wal-g backup-fetch /var/lib/pgsql/10/data-restore/ base_000000020000001E000000CB
```

实时恢复

cat recover.conf

```
restore_command = 'source mydir/wal-g.env && wal-g wal-fetch %f %p'
recovery_target_time='2019-09-10 09:51:55.794813+08'
recovery_target_timeline='latest'
```

关闭数据库 pause 状态

```
select pg_wal_replay_resume();
```

## 管理存储

### 清理存储

保留最近的 10 个备份及 wal

```
wal-g delete  retain  FULL  10 (试删)

wal-g delete  retain  FULL  10  --confirm （真删）
```

删除某个备份前的备份

```
wal-g delete before backup_name
```

## 将现有的所有 wal 上传

cat wal-push-all.sh

```
#!/bin/bash
#print the directory and file

for file in $PGDATA/pg_wal/*
do
if [ -f "$file" ]
then
  wal-g wal-push $file
fi
done
```

## 定期全备份及清理

cat /etc/cron.weekly/pg_backup_retain.sh 例如每周一个全备份，保留近半年数据

```
source mydir/wal-g.env &&  wal-g  backup-push $PGDATA
source mydir/wal-g.env &&  wal-g delete retain FULL 26 --confirm
```

## 注意事项

1 需要先进行 wal 日志的备份再进行全备份。否则在恢复的时候可能会遗漏期间的 wal 日志。

2 全备份需要等待当前 wal 日志发生切换才能完成。如果是写入慢或暂无写入数据库可执行 select pg_switch_wal() 进行手动触发。

3 全备份不包括 pg_wal 目录下的 wal 日志文件

## 思考

归档备份 wal 日志 会比生产系统的数据库滞后一个 wal 文件 。 是当 wal 日志写满或切换写新 wal 日志的时候触发的归档 。

如果需要使用归档文件恢复数据库时需要考虑时候可以找到最近的 wal 日志文件，比如在从库中。

## 其他有用脚本

下载一段连续范围内的 wal 日志文件 到目录 walbackup 目录中，防止下载过程中出现网络问题等。可重复多次执行

cat refetch_wal.sh

```
walfiles=$(python calc_wal.py $1 $2)

source mydir/wal-g.env

for wal_seq in $walfiles; do
 if [[ ! -f walbackup/"$wal_seq" ]];then
   wal-g wal-fetch $wal_seq walbackup/$wal_seq
   echo "fetch wal file " $wal_seq
 fi
done
```

cat calc_wal.py

```
import sys


def next_str(start):
    s_8 = start[:8]
    s_16 = start[8:16]
    s_24 = start[16:]
    if s_24.endswith('FF'):
        s_24 = hex(int('01',base=16))[2:].zfill(8)
        s_16 = hex(int(s_16, base=16) + 1)[2:].zfill(8)
    else:
        s_24 = hex(int(s_24, base=16) + 1)[2:].zfill(8)
    return ''.join([s_8, s_16, s_24]).upper()


def get_all(start, end):
    start = start.upper()
    end = end.upper()
    new_seq = None
    print(start)
    while new_seq != end:
        new_seq = next_str(new_seq if new_seq is not None else start)
        print(new_seq)


if __name__ == "__main__":
    get_all(sys.argv[1], sys.argv[2])

```

使用方法

refetch_wal.sh wal 开始文件名 wal 结束文件名

## wal-g 3.0

## 安装

官方目前只提供 ubuntu 系统的编译文件，其他环境需要自己进行编译

### centos 7 安装

```
# 1. 安装基础依赖
sudo yum groupinstall "Development Tools" -y
sudo yum install epel-release -y
sudo yum install git wget cmake3 brotli-devel libsodium-devel -y
sudo ln -sf /usr/bin/cmake3 /usr/bin/cmake

# 2. 安装最新版 Go 编译器 (CentOS 7 默认 Go 版本过低)

GO_VERSION=1.25.2
# 根据需要调整版本
wget https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz

# 3. 配置 Go 环境变量
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
echo 'export GOPATH=$HOME/go' >> ~/.bashrc
source ~/.bashrc

# 4. 获取 WAL-G 源码
mkdir -p $GOPATH/src/github.com/wal-g
git clone https://github.com/wal-g/wal-g.git $GOPATH/src/github.com/wal-g/wal-g
cd $GOPATH/src/github.com/wal-g/wal-g
git checkout v3.0.5

# 5. 配置编译选项（启用压缩优化）
export USE_BROTLI=1
export USE_LIBSODIUM=1


# 6. 编译 PostgreSQL 版本
make deps            # 安装Go依赖
make pg_build        # 编译主程序

# 7. 验证安装
$GOPATH/src/github.com/wal-g/wal-g/main/pg/wal-g --version
```

## 配置

提供两种配置管理方式

- 环境变量
- 配置文件

### 压缩

WALG_COMPRESSION_METHOD

- lz4 默认， 最快
- lzma 压缩率最高约 6 倍 lz4，速度慢
- zstd
- brotli

### 加密

#### 结合三方加密 Yandex Cloud KMS

#### LIBSODIUM 加密算法

- WALG_LIBSODIUM_KEY
- WALG_LIBSODIUM_KEY_PATH
- WALG_LIBSODIUM_KEY_TRANSFORM

**三变量协同关系**

**密钥来源**

| 变量                      | 作用                                                           |
| ------------------------- | -------------------------------------------------------------- |
| `WALG_LIBSODIUM_KEY`      | **直接赋值密钥**（如 `export WALG_LIBSODIUM_KEY="d0b1e2..."`） |
| `WALG_LIBSODIUM_KEY_PATH` | **从文件读取密钥**（文件内容自动去除空格/换行符）              |

> ✅ **优先级**：若同时设置，`WALG_LIBSODIUM_KEY` 优先于 `WALG_LIBSODIUM_KEY_PATH`

**密钥格式转换 (`WALG_LIBSODIUM_KEY_TRANSFORM`)**

密钥需精确 **32 字节**（256 位），用户输入的原始数据需转换：

| 转换类型      | 操作方式                                                                | 适用场景                             |
| ------------- | ----------------------------------------------------------------------- | ------------------------------------ |
| `hex`         | 将**十六进制字符串**转换为二进制（如 `"1a2b3c"` → `0x1a 0x2b 0x3c...`） | `openssl rand -hex 32` 生成的密钥    |
| `base64`      | 解码 **Base64 字符串**为二进制                                          | `openssl rand -base64 32` 生成的密钥 |
| `none` (默认) | **不转换**：<br> - 超长 → 截断前 32 字节<br> - 不足 → 补零至 32 字节    | **不推荐**（安全隐患）               |

应用示例

```bash
# 方式 1：生成 HEX 格式密钥（需设 transform=hex）
openssl rand -hex 32  # 输出类似 deae5d7c7b34a3a5e4e...
export WALG_LIBSODIUM_KEY="deae5d7c7b34a3a5e4e..."  # 64字符hex串
export WALG_LIBSODIUM_KEY_TRANSFORM="hex"
```

```
# 方式 2：生成 Base64 格式密钥（需设 transform=base64）
openssl rand -base64 32  # 输出类似 RvmrEXp9CqO8gU6Zq7b7vw==
echo "RvmrEXp9CqO8gU6Zq7b7vw==" > /etc/walg.key
export WALG_LIBSODIUM_KEY_PATH="/etc/walg.key"
export WALG_LIBSODIUM_KEY_TRANSFORM="base64"
```

#### OpenPGP 加密

- WALG_PGP_KEY
- WALG_PGP_KEY_PATH
- WALG_PGP_KEY_PASSPHRASE

与前面使用方式类似

具体案例

```
# 生成加密文件，根据提示填写
gpg --full-generate-key

# 列成key
gpg --list-keys
 8316E01F780D5E7FBCF722C3C4B51651B1B807F9
# 根据前面列出的key 导出 公钥和私钥
# 公钥
gpg --armor --export 8316E01F780D5E7FBCF722C3C4B51651B1B807F9 > public.key
# 私钥
gpg --armor --export-secret-keys     --pinentry-mode loopback     --passphrase "123"     8316E01F780D5E7FBCF722C3C4B51651B1B807F9 > private.key
```

wal-push ，backup-push 上传时用公钥 wal-fetch ，backup-fetch 下载时候用私钥

#### Envelope PGP 混合加密

### FOR postgres 配置

#### WALG_DISK_RATE_LIMIT

backup-push 磁盘读数据速率限制

#### 下载并行 backup-fetch 或 wal-fetch

WALG_DOWNLOAD_CONCURRENCY

#### 上传并行 wal-push

WALG_UPLOAD_CONCURRENCY

#### 上传并行 backup-push

WALG_UPLOAD_DISK_CONCURRENCY

#### DELTA 备份

WALG_DELTA_MAX_STEPS 默认 0

#### bundle 大小

WALG_TAR_SIZE_THRESHOLD

### 使用

#### 备份数据

backup-push $PGDATA

#### 恢复数据

backup-fetch

#### 备份 wal

wal-g wal-push

#### 恢复 wal

wal-g wal-fetch

#### 删除归档

wal-g delete

#### 远程备份

export PGPORT=xxxx
export PGUSER=xxxx
export PGPASSWORD=xxx
export PGHOST=xxx

执行的是 pg_basebackup, 需要 replication 权限

只能全备份，不能 delta 备份

POSTGER >= 15 版本目前不能远程备份，存在问题

```
wal-g backup-push
```

适合场景如 kubernets 中的 cronjobs

### 实际应用

#### 配置

/opt/wal-g.env

```

export AWS_ACCESS_KEY_ID="xxx"
export AWS_SECRET_ACCESS_KEY="xxxx"
export WALG_S3_PREFIX="s3://xxx/"
export AWS_ENDPOINT="http://xxxx:9000"
export AWS_S3_FORCE_PATH_STYLE="true"
export AWS_REGION=dx-1
export PGDATA=/var/lib/pgsql/14/data/
export PGPORT=xxx
export PGUSER=poxxstgres
export PGPASSWORD=xxxx
export PGHOST=xxxx
export WALG_TAR_SIZE_THRESHOLD=3221225472
export WALG_DELTA_MAX_STEPS=3
export WALG_UPLOAD_DISK_CONCURRENCY=3
```

#### 数据备份

主从数据库建议配置相同，单实际上只有主库生效

```
# - Archiving -
archive_mode = on               # enables archiving; off, on, or always
                                # (change requires restart)
archive_command = 'source /opt/wal-g.env &&  wal-g wal-push %p'         # command to use to archive a logfile segment
                                # placeholders: %p = path of file to archive
                                #               %f = file name only
                                # e.g. 'test ! -f /mnt/server/archivedir/%f && cp %p /mnt/server/archivedir/%f'
archive_timeout = 300           # force a logfile segment switch after thi
```

从库执行数据完整和增量备份

```bash
# 加载环境变量
source /opt/wal-g.env

# 执行全量备份
wal-g backup-push $PGDATA
```

#### 数据恢复

数据下载

```bash
# 加载环境变量
source /opt/wal-g.env

# 执行全量备份
wal-g backup-fetch $PGDATA
```

在启动前根据需求，全新的主库还是从库 配置 postgresql.auto.conf

从库建议这两个都配置上，当恢复时使用的 wal 通过 restore_command 从远程恢复后会自动切换到通过 primary_conninfo 获取，当 primary_conninfo 失败是会尝试 restore_command 从远程获取。

```
primary_conninfo =
restore_command =
recovery_target_XXX =
```

```
touch $PGDATA/recovery.signal or $PGDATA/standby.signal
```

#### Partial restore (experimental)

部分恢复功能，试验阶段

#### 定时任务

cat /etc/cron.weekly/walg-backup-push.sh

```
source /opt/wal-g.env &&  wal-g  backup-push $PGDATA
source /opt/wal-g.env &&  wal-g delete retain FULL 4 --confirm

```

TODO 如何 监控备份情况
