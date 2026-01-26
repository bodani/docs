# 逻辑卷管理

## 基本概念

- 物理卷 (PV): 底层存储设备（如硬盘、RAID阵列、分区）
- 卷组 (VG): 多个物理卷组成一个存储池
- 逻辑卷 (LV): 在卷组上划分的虚拟分区
- RAID10: RAID1（镜像） + RAID0（条带化），兼顾性能和数据安全
- PE/LE: 物理扩展块/逻辑扩展块，LVM管理的最小存储单元
- 快照: 基于时间点的数据副本，可用于备份或恢复

## 架构设计

```
  物理层: 8块4TB NVMe数据盘
  ↓
  RAID层: 每4块盘组成一个RAID10阵列
  md0 (磁盘1-4) md1 (磁盘5-8)
  ↓
  LVM层: 两个RAID设备组成一个逻辑卷组
  vg_database (包含md0和md1)
  ↓
  逻辑卷: 在卷组中创建多个逻辑卷
  mysql_data (5T) mysql_log (1T) postgres_data (4T) ...
  ↓
  文件系统: 每个逻辑卷格式化为文件系统
  /dev/vg_database/mysql_data → XFS → /db/mysql/data
```

## raid 配置

```
# 安装RAID管理工具
sudo apt install mdadm -y
```

```
# 创建RAID10阵列
sudo mdadm --create /dev/md0 \
    --level=10 \
    --raid-devices=4 \
    --metadata=1.2 \
    --name=DB_DATA_01 \
    /dev/nvme1n1 /dev/nvme2n1 /dev/nvme3n1 /dev/nvme4n1
```

```
sudo mdadm --create /dev/md1 \
    --level=10 \
    --raid-devices=4 \
    --metadata=1.2 \
    --name=DB_DATA_02 \
    /dev/nvme5n1 /dev/nvme6n1 /dev/nvme7n1 /dev/nvme8n1
```

参数说明

- --level=10: 使用RAID10级别
- --raid-devices=4: 使用4个设备
- --metadata=1.2: 使用1.2版元数据（推荐用于RAID10）

查看状态

```
sudo mdadm --detail /dev/md0
```

## lvm 配置

```
# 安装LVM管理工具
sudo apt install lvm2 thin-provisioning-tools epics-base -y
# 安装文件系统工具
sudo apt install xfsprogs btrfs-progs e2fsprogs -y
# 安装监控工具
sudo apt install smartctl nvme-cli sysstat -y
```

### 创建物理卷 (PV)

```
# 在RAID设备上创建物理卷
sudo pvcreate /dev/md0
sudo pvcreate /dev/md1

# 验证物理卷创建
sudo pvs
sudo pvdisplay
```

物理卷管理命令：

- pvs - 显示物理卷概览
- pvdisplay - 详细显示物理卷信息
- pvinfo - 显示物理卷信息
- pvscan - 扫描系统中所有物理卷
- pvmove - 移动物理卷上的数据到其他物理卷
- pvremove - 删除物理卷

### 创建卷组 (VG)

```
# 创建卷组，设置PE大小为64MB
sudo vgcreate -s 64M vg_database /dev/md0 /dev/md1

# 验证卷组
sudo vgs
sudo vgdisplay
```

### 创建逻辑卷 (LV)

```
 创建MySQL日志逻辑卷（分配1TB空间）
sudo lvcreate -L 1T -n mysql_log vg_database
# 创建PostgreSQL数据逻辑卷（分配4TB空间）
sudo lvcreate -L 4T -n postgres_data vg_database
# 创建PostgreSQL WAL日志逻辑卷（分配500GB空间）
sudo lvcreate -L 500G -n postgres_wal vg_database
```

逻辑卷管理命令：

- lvs - 显示逻辑卷概览
- lvdisplay - 详细显示逻辑卷信息
- lvscan - 扫描逻辑卷
- lvextend - 扩展逻辑卷
- lvreduce - 缩小逻辑卷
- lvremove - 删除逻辑卷
- lvresize - 调整逻辑卷大小

## 文件系统配置

```
# MySQL数据卷 - 使用XFS（适合大文件）
sudo mkfs.xfs -f -m reflink=1 /dev/vg_database/mysql_data

# MySQL日志卷 - 使用XFS
sudo mkfs.xfs -f /dev/vg_database/mysql_log

# PostgreSQL数据卷 - 使用XFS
sudo mkfs.xfs -f /dev/vg_database/postgres_data

# PostgreSQL WAL卷 - 使用EXT4（适合小文件）
sudo mkfs.ext4 -F /dev/vg_database/postgres_wal
```

## 卷管理

```
# 查看卷组剩余空间
sudo vgdisplay vg_database | grep Free

# 扩展逻辑卷（增加5GB）
sudo lvextend -L +5G /dev/vg_database/mysql_data

# 扩展文件系统（XFS）
sudo xfs_growfs /db/mysql/data

# 对于EXT4文件系统：
sudo resize2fs /dev/vg_database/mysql_log
```
