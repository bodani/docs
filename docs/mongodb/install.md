# MongoDB 安装

## 简介

MongoDB 是一个基于分布式文件存储的开源数据库系统，属于 NoSQL 数据库，使用 JSON 风格的数据结构。

## 安装方式

### 1. 包管理器安装

#### Ubuntu/Debian

```bash
# 导入公钥
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -

# 添加MongoDB APT源
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# 更新包列表并安装MongoDB
sudo apt-get update
sudo apt-get install -y mongodb-org
```

#### CentOS/RHEL

```bash
# 创建MongoDB.repo文件
cat << EOF | sudo tee /etc/yum.repos.d/mongodb-org-6.0.repo
[mongodb-org-6.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/8/mongodb-org/6.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-6.0.asc
EOF

# 安装MongoDB
sudo dnf install -y mongodb-org
```

### 2. Docker 安装

```bash
# 拉取MongoDB镜像
docker pull mongo:latest

# 启动MongoDB容器
docker run -d -p 27017:27017 -v mongo-data:/data/db --name mongodb mongo:latest
```

## 验证安装

```bash
# 启动MongoDB服务
sudo systemctl start mongod

# 设置开机自启动
sudo systemctl enable mongod

# 连接MongoDB
mongo
```
