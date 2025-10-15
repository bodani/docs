# 单节点安装

## 简介

victorialogs 是一款用于替代elasticsearch 的日志存储服务。  

victorialogs 专注处理日志收集场景，elasticsearch 功能丰富，如全文检索等。

victorialogs 开源协议更加友好。 

在日志收集存储场景 victorialogs可大量节省服务器资源，包括存储压缩，cpu, 内存。

## 安装victorialogs

### 下载 
```
curl -L -O https://github.com/VictoriaMetrics/VictoriaLogs/releases/download/v1.28.0/victoria-logs-linux-amd64-v1.28.0.tar.gz
tar xzf victoria-logs-linux-amd64-v1.28.0.tar.gz
mv victoria-logs-prod /usr/local/bin/
```
### 创建专用用户和用户组
```
sudo groupadd --system victorialogs
sudo useradd --system -g victorialogs -d /nonexistent -s /usr/sbin/nologin victorialogs
```
### 创建数据存储目录并设置权限
```
sudo mkdir -p   /data/victorialogs
sudo chown -R victorialogs:victorialogs   /data/victorialogs
sudo chmod 750  /data/victorialogs
```

###  配置文件管理
创建环境变量配置文件 /etc/victoria-logs.conf

```
# Victoria Logs 配置
STORAGE_PATH="/data/victorialogs"
RETEN_PERIOD="10y"
MAX_DISK_PERCENT="80"
```

### Systemd 服务单元文件
创建 /etc/systemd/system/victoria-logs.service

```
[Unit]
Description=Victoria Logs Production Server
After=network.target
Documentation=https://docs.victoriametrics.com/victoria-logs/
[Service]
User=victorialogs
Group=victorialogs
EnvironmentFile=/etc/victoria-logs.conf
WorkingDirectory=/var/lib
ExecStart=/usr/local/bin/victoria-logs-prod \
    -storageDataPath=${STORAGE_PATH} \
    -retentionPeriod=${RETEN_PERIOD} \
    -retention.maxDiskUsagePercent=${MAX_DISK_PERCENT}
Restart=on-failure
RestartSec=5
StartLimitInterval=60
StartLimitBurst=3
LimitNOFILE=65535
LimitNPROC=65535
SyslogIdentifier=victoria-logs
[Install]
WantedBy=multi-user.target
```

### 启动服务
```
# 重载systemd配置
sudo systemctl daemon-reload
# 设置开机自启
sudo systemctl enable victoria-logs
# 启动服务
sudo systemctl start victoria-logs
# 检查状态
sudo systemctl status victoria-logs
```

## 安装 fluentbit 

优势C 实现，够轻量。 开源协议友好。

支持日志分解很诡异，没有任何错误提示。省心的原则真心不想用。通过在fluentbit的url中设置debug，没有任何问题，但是在vl中就是看不到任何数据，而且vl的日志等级没有debug最低是info. 问题调查难度太大。挣扎了几天放弃了parser ,pg15版本新增了 json格式的日志。

#### Ubuntu 24.04
```
sudo sh -c 'curl https://packages.fluentbit.io/fluentbit.key | gpg --dearmor > /usr/share/keyrings/fluentbit-keyring.gpg'
echo "deb [signed-by=/usr/share/keyrings/fluentbit-keyring.gpg] https://packages.fluentbit.io/ubuntu/noble noble main" | sudo tee /etc/apt/sources.list.d/fluent-bit.list
```
```
apt-get install fluent-bit -y
```

#### Centos7

cat /etc/yum.repos.d/fluent-bit.repo
```
[fluent-bit]
name = Fluent Bit
# Legacy server style
baseurl = https://packages.fluentbit.io/centos/$releasever/
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.fluentbit.io/fluentbit.key
enabled=1
```
#### 配置
vim /etc/fluent-bit/fluent-bit.conf
```
[SERVICE]
    Flush           5
    Daemon          off
    Log_Level       info
    Parsers_File    parsers.conf
    HTTP_Server     On
    HTTP_Listen     0.0.0.0
    HTTP_Port       2020
# 日志输入（替换实际路径）
[INPUT]
    Name              tail
    Path              /var/log/postgresql/*.csv
    Tag               postgres.log
    Mem_Buf_Limit     50MB
    Skip_Long_Lines   On
    Read_from_Head    true
    multiline.parser  multiline_postgres 
# 日志解析
[FILTER]
    Name          parser
    Match         postgres.log 
    Key_Name      log
    Parser        postgres
    Reserve_Data  On

# 提取SQL执行时间（可选）
# 提取执行时间（可选）
[FILTER]
    Name          rewrite_tag
    Match         postgres.log 
    Rule          message /duration: (\d+\.\d+) ms/ duration.$TAG false
    Emitter_Name  re_emitted

[Output]
    Name http
    Match postgres.log
    host localhost
    port 9428
    uri /insert/jsonline?_stream_fields=stream&_msg_field=log&_time_field=date
    format json_lines
    json_date_format iso8601
```


cat /etc/fluent-bit/parsers.conf
```
# PostgreSQL 日志字段解析器
[PARSER]
    Name    postgres
    Format  regex
    Regex   ^(?<log_time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} \w+),(?<user>\"[^\"]+\"),(?<database>\"[^\"]+\"),(?<pid>\d+),(?<connection>\"[^\"]+\"),(?<session_id>\w+\.[\w]+),(?<command_num>\d+),(?<command>\"[^\"]+\"),(?<session_time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \w+),(?<vtx_id>[\d\/]+),(?<tx_id>\d+),(?<log_level>\w+),(?<sql_state>\d+),\"(?<message>(?:[^\"]|\\\")*)\"
    Time_Key      log_time
    Time_Format   %Y-%m-%d %H:%M:%S.%L %Z
    Time_Keep     On
    Types         pid:integer command_num:integer tx_id:integer
[MULTILINE_PARSER]
    Name    multiline_postgres
    Type    regex
    key_content   log
    flush_timeout       1000
    Rule    "start_state" "/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} \w+/" "cont"
    Rule    "cont"        "/.*/"  "cont"
```

## 安装 filebeat (略)

不支持日志分解

### APT 环境
```
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -

sudo apt-get install apt-transport-https
<!-- echo "deb https://artifacts.elastic.co/packages/9.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-9.x.list -->
echo "deb https://artifacts.elastic.co/packages/oss-9.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-9.x.list

sudo apt-get update && sudo apt-get install filebeat

sudo systemctl enable filebeat
```

### YUM 环境

```
sudo rpm --import https://artifacts.elastic.co/GPG-KEY-elasticsearch

```
vi /etc/yum.repos.d/elastic.repo
```
[elastic-9.x]
name=Elastic repository for 9.x packages
baseurl=https://artifacts.elastic.co/packages/oss-9.x/yum
gpgcheck=1
gpgkey=https://artifacts.elastic.co/GPG-KEY-elasticsearch
enabled=1
autorefresh=1
type=rpm-md
```
```
sudo yum install filebeat

sudo systemctl enable filebeat
```

### 配置管理
使用modules ,好处是已预设置好mulitlines. 即多行日志规则
```
filebeat.config.modules:
  path: ${path.config}/modules.d/*.yml
  reload.enabled: true
output.elasticsearch:
  hosts: ["http://vmlogs:9428/insert/elasticsearch/"]
  parameters:
    _msg_field: "message"
    _time_field: "@timestamp"
    _stream_fields: "host.hostname,log.file.path"
```
对应修改 modules 配置文件,以 postgresql 为例
```
- module: postgresql
  log:
    enabled: true
    var.paths: ["/var/lib/pgsql/14/data/log/*.csv"]
```
开启 modules 

```
 # 查看 module
 filebeat modules list
 # 开启 postgresql module 
 filebeat modules enable postgresql
 # 检查配置
 filebeat test config 
 filebeat test output
```

启动服务
```
systemctl start filebeat
systemctl enable filebeat
```

## 安装logstash (略)

依赖java-jdk 耗资源

作用: 对日志字段进行提取分割

### 安装
```
apt-get install logstash-oss
```
### 配置
```

```



帮写一个在github上面的issue.

我在使用fluent-bit收集postgresql日志并进行parser解析后存储到victorialogs中。 

在fluent-bit 中的配置
```
[Output]
    Name http
    Match postgres.log
    host 10.1.80.54
    port 9428
    uri /insert/jsonline?_stream_fields=stream&_msg_field=log&_time_field=date&debug=1
    format json_lines
    json_date_format iso8601
```
这是在victorialogs查看到的运行日志
```
Aug 27 05:16:27 80-54 victoria-logs[1737902]: 2025-08-27T05:16:27.948Z        info        VictoriaLogs/app/vlinsert/insertutil/common_params.go:248        remoteAddr="10.1.80.87:39314"; requestURI=/insert/jsonline?_stream_fields=stream&_msg_field=log&_time_field=date&debug=1; ignoring log entry because of `debug` arg: {"_msg":"2025-08-27 13:16:27.649 CST,\"postgres\",\"postgres\",2165,\"127.0.0.1:36508\",68ae94ab.875,22,\"SELECT\",2025-08-27 13:16:27 CST,2/58378,0,LOG,00000,\"duration: 5.969 ms  execute \u003cunnamed>: SELECT pg_database_size($1)\",\"parameters: $1 = \u0027cloud_back\u0027\",,,,,,,,\"\",\"client backend\",,0","_stream":"{}","_time":"2025-08-27T19:16:27.649Z","command":"SELECT","command_num":"22","connection":"127.0.0.1:36508","database":"postgres","duration":"5.969","extra":",\"parameters: $1 = \u0027cloud_back\u0027\",,,,,,,,\"\",\"client backend\",,0","log_level":"LOG","log_time":"2025-08-27 13:16:27.649 CST","pid":"2165","session_id":"68ae94ab.875","session_time":"2025-08-27 13:16:27 CST","sql_state":"00000","tx_id":"0","user":"postgres","vtx_id":"2/58378"}
Aug 27 05:16:35 80-54 victoria-logs[1737902]: 2025-08-27T05:16:35.030Z        info        VictoriaLogs/app/vlinsert/insertutil/common_params.go:248        remoteAddr="10.1.80.87:39986"; requestURI=/insert/jsonline?_stream_fields=stream&_msg_field=log&_time_field=date&debug=1; ignoring log entry because of `debug` arg: {"_msg":"2025-08-27 13:16:33.704 CST,\"postgres\",\"postgres\",2228,\"127.0.0.1:37356\",68ae94b1.8b4,1,\"SELECT\",2025-08-27 13:16:33 CST,2/0,0,LOG,00000,\"duration: 2.198 ms  statement: select datname from pg_database where not datistemplate and datallowconn and datname!=\u0027postgres\u0027\",,,,,,,,,\"psql\",\"client backend\",,-4034325387031128140","_stream":"{}","_time":"2025-08-27T19:16:33.704Z","command":"SELECT","command_num":"1","connection":"127.0.0.1:37356","database":"postgres","duration":"2.198","extra":",,,,,,,,,\"psql\",\"client backend\",,-4034325387031128140","log_level":"LOG","log_time":"2025-08-27 13:16:33.704 CST","pid":"2228","session_id":"68ae94b1.8b4","session_time":"2025-08-27 13:16:33 CST","sql_state":"00000","tx_id":"0","user":"postgres","vtx_id":"2/0"}
```

我把debug=0
```
[Output]
    Name http
    Match postgres.log
    host 10.1.80.54
    port 9428
    uri /insert/jsonline?_stream_fields=stream&_msg_field=log&_time_field=date&debug=1
    format json_lines
    json_date_format iso8601
```

然而我并没有在victorialogs中查看到新的信息。

这个问题困扰了我很久，

我尝试过清理掉victorialogs的存储数据。也没有起作用
我想在victorialogs中开启debug等级的运行日志，但是好像没有。 

我发现一个奇怪的现象，有时候零点过后看的新数据。我不知道这是什么原因。我现在在调试这个问题。希望得到帮助



