# 高可用 patroni+pg17+ubuntu2024

## 组件及版本

sudo apt-get install python3-psycopg2  # install psycopg2 module on Debian/Ubuntu

## etcd 

```
wget https://github.com/etcd-io/etcd/releases/download/v3.5.21/etcd-v3.5.21-linux-amd64.tar.gz
tar -zxvf etcd-v3.5.21-linux-amd64.tar.gz
cd etcd-v3.5.21-linux-amd64
cp etcd* /usr/local/bin/
```