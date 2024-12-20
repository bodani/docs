# mysql 安装

## ubuntu 
基础依赖软件安装
```
sudo apt-get install libmecab2 \
                     libjson-perl \ 
                     mecab-ipadic-utf8 \
                     mecab-utils \ 
                     mecab-ipadic
```
### apt 源安装 
安装当前最新版本,有apt源维护

https://dev.mysql.com/downloads/

`MySQL APT Repository -> `

`Ubuntu / Debian (Architecture Independent), DEB Package 		17.6K 	Download`

```
wget mysql-apt-config_0.8.33-1_all.deb
dpkg -i ./mysql-apt-config_0.8.33-1_all.deb
```
生成源文件 `/etc/apt/sources.list.d/mysql.list`

```
# apt-get update -y 

# apt list -a mysql-server
Listing... Done
mysql-server/unknown 8.0.40-1ubuntu22.04 amd64 [upgradable from: 8.0.36-1ubuntu22.04]
mysql-server/jammy-updates,jammy-security 8.0.40-0ubuntu0.22.04.1 amd64
mysql-server/now 8.0.36-1ubuntu22.04 amd64 [installed,upgradable to: 8.0.40-1ubuntu22.04]
mysql-server/jammy 8.0.28-0ubuntu4 amd64
```
选择版本进行安装
```
apt-get install mysql-server='8.0.40-1ubuntu22.04'
```
大版本选择
```
sudo dpkg-reconfigure mysql-apt-config
```
### 安装包指定版本安装

下载指的版本 https://downloads.mysql.com/archives/community/

`Ubuntu Linux 23.10 (x86, 64-bit), DEB Bundle 	Dec 14, 2023 	415.2M 	Download`

解压并安装
```
tar xf ./mysql-server_8.0.36-1ubuntu22.04_amd64.deb-bundle.tar
dpkg -i  ./*.deb
```

### mysqlshell

下载地址 https://dev.mysql.com/downloads/shell/

```
DEB Package 	8.0.40 	36.5M 	Download
(mysql-shell_8.0.40-1ubuntu22.04_amd64.deb) 	MD5: d965889b156b3db9451bfd367ea8d51a | Signature
```
下载并安装
```
wget https://dev.mysql.com/get/Downloads/MySQL-Shell/mysql-shell_8.0.40-1ubuntu22.04_amd64.deb
dpkg -i ./mysql-shell_8.0.40-1ubuntu22.04_amd64.deb
```

### mysql-router

下载地址 https://dev.mysql.com/downloads/router/
```
DEB Package 	8.0.40 	9.0M 	Download
(mysql-router-community_8.0.40-1ubuntu22.04_amd64.deb) 	MD5: 9e207810588fad642c93306c483e76b8 | Signature
```
下载并安装
```
wget https://dev.mysql.com/get/Downloads/MySQL-Router/mysql-router-community_8.0.40-1ubuntu22.04_amd64.deb
dpkg -i ./mysql-router-community_8.0.40-1ubuntu22.04_amd64.deb
```

## 源码安装

### 基础软件安装
```
apt-get install libaio-dev \
    libsasl2-modules-gssapi-mit \
    libkrb5-dev \
    libsasl2-dev \
    libldap2-dev \
    bison \
    autoconf \
    automake \
    libtool
```
### 下载源码
```
MYSQL_MAJOR=8.0
MYSQL_VERSION=8.0.40
curl https://cdn.mysql.com/Downloads/MySQL-${MYSQL_MAJOR}/mysql-${MYSQL_VERSION}.tar.gz --output mysql-${MYSQL_VERSION}.tar.gz
tar --no-same-owner -xf mysql-${MYSQL_VERSION}.tar.gz
cd mysql-${MYSQL_VERSION}
```
### 编译安装
```
cmake  -DDOWNLOAD_BOOST=1 -DWITH_BOOST=/tmp/boost/ -DBUILD_CONFIG=mysql_release -DWITH_AUTHENTICATION_LDAP=1 -DCMAKE_INSTALL_PREFIX=/usr/local/mysql -DSYSCONFDIR=/usr/local/mysql/conf -DDEFAULT_SYSCONFDIR=/usr/local/mysql/conf -DFORCE_INSOURCE_BUILD=1
make  --jobs=2
make  install --jobs=2
make  clean
strip  /usr/local/mysql/bin/comp_err
strip  /usr/local/mysql/bin/ibd2sdi
strip  /usr/local/mysql/bin/innochecksum
strip  /usr/local/mysql/bin/lz4_decompress
strip  /usr/local/mysql/bin/my_print_defaults
strip  /usr/local/mysql/bin/myisam_ftdump
strip  /usr/local/mysql/bin/myisamchk
strip  /usr/local/mysql/bin/myisamlog
strip  /usr/local/mysql/bin/myisampack
strip  /usr/local/mysql/bin/mysql
strip  /usr/local/mysql/bin/mysql_config_editor
strip  /usr/local/mysql/bin/mysql_migrate_keyring
strip  /usr/local/mysql/bin/mysql_secure_installation
strip  /usr/local/mysql/bin/mysql_ssl_rsa_setup
strip  /usr/local/mysql/bin/mysql_tzinfo_to_sql
strip  /usr/local/mysql/bin/mysql_upgrade
strip  /usr/local/mysql/bin/mysqladmin
strip  /usr/local/mysql/bin/mysqlbinlog
strip  /usr/local/mysql/bin/mysqlcheck
strip  /usr/local/mysql/bin/mysqld
strip  /usr/local/mysql/bin/mysqldump
strip  /usr/local/mysql/bin/mysqlimport
strip  /usr/local/mysql/bin/mysqlpump
strip  /usr/local/mysql/bin/mysqlrouter
strip  /usr/local/mysql/bin/mysqlrouter_keyring
strip  /usr/local/mysql/bin/mysqlrouter_passwd
strip  /usr/local/mysql/bin/mysqlrouter_plugin_info
strip  /usr/local/mysql/bin/mysqlshow
strip  /usr/local/mysql/bin/mysqlslap
strip  /usr/local/mysql/bin/perror
strip  /usr/local/mysql/bin/zlib_decompress

# remove mysql test dir
rm -rf /usr/local/mysql/mysql-test
rm -rf /usr/local/mysql/mysql-8.0/mysql-test

# copy mysql build files to data dir
cp -r /usr/local/mysql/ ${DATA_DIR}/

# clean tmp data
cd .. && rm -rf mysql-${MYSQL_VERSION} mysql-${MYSQL_VERSION}.tar.gz 
```


### 初始化数据
```
1、查看 apparmor 的开启和保护情况：
（1）sudo apparmor_status
 
2、列出AppArmor所有可用配置文件：
（1）ls /etc/apparmor.d/
 
3、假设我们要禁用Apparmor for MySQL Server：
（1）sudo ln -s /etc/apparmor.d/usr.sbin.mysqld /etc/apparmor.d/disable/
（2）apparmor_parser -R /etc/apparmor.d/disable/usr.sbin.mysqld
（3）这是再次执行apparmor_status，应该看不到/usr/sbin/mysqld 了
 
4、要完全禁用AppArmor：
（1）sudo systemctl disable apparmor
```

```
sudo mysqld --initialize --user=mysql --datadir=/var/lib/rancher/mysql/
```
