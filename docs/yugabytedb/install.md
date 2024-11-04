
## 单实例安装

#### 下载
```
 wget https://downloads.yugabyte.com/releases/2.21.1.0/yugabyte-2.21.1.0-b271-linux-x86_64.tar.gz
 
 tar xvfz yugabyte-2.21.1.0-b271-linux-x86_64.tar.gz && cd yugabyte-2.21.1.0/
```

#### 启动
```
./bin/post_install.sh
./bin/yugabyted start
./bin/yugabyted status 
```
#### 连接
```
./bin/ysqlsh
./bin/ycqlsh
```
迁移工具
 
 YugabyteDB Voyager 

#### 清理
```
./bin/yugabyted destroy
```

## 单机集群部署

#### 网络模拟
```
sudo ifconfig lo 127.0.0.2
sudo ifconfig lo 127.0.0.3
```

#### 启动
```
./bin/yugabyted start \
                --advertise_address=127.0.0.1 \
                --base_dir={$HOME}/var/node1 \
                --cloud_location=aws.us-east.us-east-1a

./bin/yugabyted start \
                --advertise_address=127.0.0.2 \
                --base_dir={$HOME}/var/node2 \
                --cloud_location=aws.us-central.us-east-1b \
                --join=127.0.0.1

./bin/yugabyted start \
                --advertise_address=127.0.0.3 \
                --base_dir={$HOME}/var/node3 \
                --cloud_location=aws.us-west.us-west-1c \
                --join=127.0.0.1

./bin/yugabyted configure data_placement --base_dir={$HOME}/var/node1 --fault_tolerance=zone

./bin/yugabyted status --base_dir={$HOME}/var/node1
```

## 压测

#### 下载
```
 install openjdk

 wget https://github.com/YugabyteDB-Samples/yb-workload-simulator/releases/download/v0.0.8/yb-workload-sim-0.0.8.jar
```

#### 启动
```
java -jar \
    -Dnode=127.0.0.1 \
    ./yb-workload-sim-0.0.8.jar
```

http://localhost:8080/

## 监控

#### 集成 prometheus 
```
  - job_name: "yugabytedb"
    metrics_path: /prometheus-metrics
    relabel_configs:
      - target_label: "node_prefix"
        replacement: "cluster-1"
    metric_relabel_configs:
      # Save the name of the metric so we can group_by since we cannot by __name__ directly...
      - source_labels: ["__name__"]
        regex: "(.*)"
        target_label: "saved_name"
        replacement: "$1"
      # The following basically retrofit the handler_latency_* metrics to label format.
      - source_labels: ["__name__"]
        regex: "handler_latency_(yb_[^_]*)_([^_]*)_([^_]*)(.*)"
        target_label: "server_type"
        replacement: "$1"
      - source_labels: ["__name__"]
        regex: "handler_latency_(yb_[^_]*)_([^_]*)_([^_]*)(.*)"
        target_label: "service_type"
        replacement: "$2"
      - source_labels: ["__name__"]
        regex: "handler_latency_(yb_[^_]*)_([^_]*)_([^_]*)(_sum|_count)?"
        target_label: "service_method"
        replacement: "$3"
      - source_labels: ["__name__"]
        regex: "handler_latency_(yb_[^_]*)_([^_]*)_([^_]*)(_sum|_count)?"
        target_label: "__name__"
        replacement: "rpc_latency$4"

    static_configs:
      - targets: ["127.0.0.1:7000", "127.0.0.2:7000", "127.0.0.3:7000"]
        labels:
          export_type: "master_export"

      - targets: ["127.0.0.1:9000", "127.0.0.2:9000", "127.0.0.3:9000"]
        labels:
          export_type: "tserver_export"

      - targets: ["127.0.0.1:12000", "127.0.0.2:12000", "127.0.0.3:12000"]
        labels:
          export_type: "cql_export"

      - targets: ["127.0.0.1:13000", "127.0.0.2:13000", "127.0.0.3:13000"]
        labels:
          export_type: "ysql_export"

      - targets: ["127.0.0.1:11000", "127.0.0.2:11000", "127.0.0.3:11000"]
        labels:
          export_type: "redis_export
```

#### grafana

`12620`

#### 压测 

```
wget https://github.com/yugabyte/yb-sample-apps/releases/download/v1.4.1/yb-sample-apps.jar -O yb-sample-apps.jar
```

```
java -jar ./yb-sample-apps.jar \
    --workload CassandraKeyValue \
    --nodes 127.0.0.1:9042 \
    --num_threads_read 1 \
    --num_threads_write 1
```

#### 清理

```
./bin/yugabyted destroy --base_dir={$HOME}/var/node1
./bin/yugabyted destroy --base_dir={$HOME}/var/node2
./bin/yugabyted destroy --base_dir={$HOME}/var/node3
```