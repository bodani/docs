## 利用 ddrescue 进行磁盘克隆和数据恢复

核心命令

```
sudo ddrescue -d -J -r 3 -b 4096 -c 256k --timeout=300s --force /dev/sdb /dev/sdc mapfile.ddrescue
```

-r 3 标准重试次数控制（替换不支持的 --max-retries）
-b 4096 强制 4K 对齐（替代 --sector-size=4096）
-c 1M 设置 1MB 拷贝块大小（提升克隆效率）
--timeout=300s 单 I/O 超时 300 秒（仍可用）

错误
sudo ddrescue -d -J -r 3 -b 4096 -c 1M --timeout=300s --force /dev/sdb /dev/sdc mapfile.ddrescue
terminate called after throwing an instance of 'std::bad_alloc'
what(): std::bad_alloc

这个 `std::bad_alloc` 错误表示 ddrescue 在尝试分配内存时失败了，通常是由于 `-c 1M` 参数设置的缓冲区过大导致的。

## 示例

```
sudo ddrescue -d -J -r 3 -b 4096 -c 256k --timeout=300s --force /dev/sdb /dev/sdc mapfile.ddrescue
GNU ddrescue 1.27
Press Ctrl-C to interrupt
     ipos:    7340 MB, non-trimmed:        0 B,  current rate:    174 MB/s
     opos:    7340 MB, non-scraped:        0 B,  average rate:    262 MB/s
     ipos:   19922 MB, non-trimmed:        0 B,  current rate:  95325 kB/s
     opos:   19922 MB, non-scraped:        0 B,  average rate:  88546 kB/s
     ipos:   25165 MB, non-trimmed:        0 B,  current rate:    116 MB/s
     opos:   25165 MB, non-scraped:        0 B,  average rate:  80401 kB/s
     ipos:  193986 MB, non-trimmed:        0 B,  current rate:    116 MB/s
     opos:  193986 MB, non-scraped:        0 B,  average rate:  81954 kB/s
     ipos:  255852 MB, non-trimmed:        0 B,  current rate:       0 B/s
     opos:  255852 MB, non-scraped:        0 B,  average rate:  90640 kB/s
non-tried:        0 B,  bad-sector:        0 B,    error rate:       0 B/s
  rescued:  256060 MB,   bad areas:        0,        run time:     47m  4s
pct rescued:  100.00%, read errors:        0,  remaining time:         n/a
                              time since last successful read:          0s
Copying non-tried blocks... Pass 1 (forwards)
Finished
```
