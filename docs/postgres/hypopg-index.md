 
# PostgreSQL 中的假设索引 
[github](https://github.com/HypoPG/hypopg)

## 背景
数据库中索引对性能的影响至关重要。往往采用创建新的索引的方式来优化现有数据库。

测试环境通常与正式环境的数据量数据分布不同，在测试环境中索引效果不能完全代表真实的运行环境索引的效果。
但是创建一个索引会占用系统的资源并且需要一定的时间。对正在运行的系统会带来额外的压力。
如果新的索引并不理想或不生，再把索引删除效岂不是既费时有费力，对线上运行的数据库也不友好。

创建假设索引几乎不需要占用系统的资源，本质上是利用数据库的统计信息来模拟索引使用的效果。

创建完成后可通过explain 来验证索引，预先了解新索引的使用效果。


### 安装

- RHEL/Rocky Linux
```
yum install hypopg
```
- Debian / Ubuntu
```
#  XY is the major version
apt install postgresql-XY-hypopg
```
- 源码安装
```
wget https://github.com/HypoPG/hypopg/archive/master.zip

unzip master.zip
cd hypopg-master

make
sudo make install

make install
```

## 介绍
HypoPG 创建的索引 只存在当前连接的私有内存中，不会影响到任何其他运行中的连接。

## 
