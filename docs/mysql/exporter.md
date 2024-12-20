# exporter 监控

## 用户及权限
```
CREATE USER 'exporter'@'%' IDENTIFIED BY 'f72affe6577a5b6334ae79adf2936f27' WITH MAX_USER_CONNECTIONS 3;
GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'exporter'@'%';
```

## Multi-target support
```
mysql1
mysql2  -> exporter -> prometheus   
mysql3 
```

### 配置 mysqld_exporter

my.cnf
```
[client]
  user = exporter
  password = f72affe6577a5b6334ae79adf2936f27
[client.servers1]
    user = bar1
    password = bar1123
[client.servers2]
    user = bar2
    password = bar1223
```

```
./mysqld_exporter --config.my-cnf=my.cnf 
```

### prometheus 配置
```
 - job_name: mysql # To get metrics about the mysql exporter’s targets
      params:
        # Not required. Will match value to child in config file. Default value is `client`.
        auth_module: [client.servers]
      static_configs:
        - targets:
          # All mysql hostnames or unix sockets to monitor.
          - server1:3306
          - server2:3306
      relabel_configs:
        - source_labels: [__address__]
          target_label: __param_target
        - source_labels: [__param_target]
          target_label: instance
        - target_label: __address__
          # The mysqld_exporter host:port
          replacement: localhost:9104
```



helmbroker-m002-0.helmbroker-m002.zhangjint.svc.cluster.local

hb-mysql-cluster-standard-10-0.hb-mysql-cluster-standard-10.drycc-addons-test.svc.cluster.local


IYZGaU5Wdw