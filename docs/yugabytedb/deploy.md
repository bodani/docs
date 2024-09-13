## 部署集群

#### 检测列表

- CPU: x86 and ARM (aarch64) 
- 操作系统:  AlmaLinux 8 and RHEL 8
- NTP & Chrony

####  资源需求

- 最小需求 2 cores  2GB RAM
- 生产需要
    YCQL - 16+ cores and 32GB+ RAM ,
    YSQL - 16+ cores and 64GB+ RAM

#### 指令集 

```
grep -q sse4_2 /proc/cpuinfo && echo "true" || echo "false"
```

#### 硬盘
- SSD
- JBOD
- XFS