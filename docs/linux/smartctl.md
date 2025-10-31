# 利用 smartctl + prometheus 监控硬盘健康状态

## 安装 exporter

### 依赖

```
smartmontools >= 7.0
```

### 安装包

根据自身系统下载相应的软件包

```
wget https://github.com/prometheus-community/smartctl_exporter/releases/download/v0.14.0/smartctl_exporter-0.14.0.linux-amd64.tar.gz
```

解压可运行文件到 `/usr/local/bin/`

创建服务

```
sudo tee /etc/systemd/system/smartctl_exporter.service > /dev/null <<EOF
[Unit]
Description=Prometheus Smartctl Exporter
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/smartctl_exporter \
 --smartctl.interval=60s \
 --smartctl.rescan=10m \
 --web.listen-address=:9633 \
 --log.level=info
Restart=on-failure
RestartSec=5s
TimeoutStopSec=10s
Environment="SMARTCTL_EXPORTER_ENABLE_INTERVAL=15s"
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=smartctl_exporter

[Install]
WantedBy=multi-user.target
EOF
```

### 启动服务

```
sudo systemctl daemon-reload
sudo systemctl enable smartctl_exporter
sudo systemctl start smartctl_exporter
```

### 验证服务状态

```
sudo systemctl status smartctl_exporter
```

## 配置 Prometheus

```yaml
- job_name: "smartctl_exporter"
  static_configs:
    - targets: ["localhost:9633"]
```

将上述配置添加到 Prometheus 的配置文件 `prometheus.yml` 中，然后重启 Prometheus 服务以应用更改。

### 重点指标

### 🚨 硬盘健康监控关键指标（Prometheus/Grafana 告警规则）

| 规则类型         | 规则表达式                                                                                 | 监控对象                                    | 阈值设定       | 物理含义                                                                                | 风险等级    | 监控建议                                                                              |
| ---------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------- | -------------- | --------------------------------------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------- |
| **坏道检测**     | `smartctl_device_attribute{attribute_id="5", attribute_value_type="raw"} > 0`              | 重分配扇区计数<br>(Reallocated_Sector_Ct)   | >0 触发告警    | 每增加 1=1 个物理坏扇区被替换<br>**机械盘致命隐患**                                     | ⚠️⚠️⚠️ 致命 | **立即更换硬盘**<br>即使 1 也需重点关注                                               |
| **SSD 寿命**     | `smartctl_device_attribute{attribute_id="173", attribute_value_type="value"} < 80`         | 磨损平衡健康度<br>(厂商自定义, SSD 常见)    | <80 触发告警   | 值下降速度反映 SSD 磨损：<br>- 80≈ 剩余 20%寿命<br>- **需结合备用块数综合判断**         | ⚠️⚠️ 高危   | 企业盘: <70 换盘<br>消费盘: <50 换盘                                                  |
| **SSD 寿命**     | `smartctl_device_attribute{attribute_id="233", attribute_value_type="value"} < 50`         | 剩余寿命百分比<br>(Media_Wearout_Indicator) | <50 触发告警   | 企业级 SSD: 直接显示百分比寿命<br>**0 时写入锁定风险**                                  | ⚠️ 中危     | 进入 50 区间即备盘                                                                    |
| **老化风险**     | `smartctl_device_attribute{attribute_id="9", attribute_value_type="raw"} / (24 * 365) > 5` | 通电时间<br>(Power_On_Hours)                | >5 年 触发告警 | **机械盘**:<br>- 5 年故障率陡增<br>- 轴承/电机老化<br>**SSD**: 电子元件寿命衰减         | ⚠️⚠️ 高危   | 生产环境: >4 年即标记为高危<br>建议循环使用年限：<br>- 企业盘: 5 年<br>- 消费盘: 3 年 |
| **物理冲击**     | `smartctl_device_attribute{attribute_id="12", attribute_value_type="raw"} > 100`           | 启停次数<br>(Power_Cycle_Count)             | >100 触发警告  | 频繁启停加速磁头磨损<br>**特别警惕**：<br>- 单日>3 次异常重启<br>- 与温度骤变关联       | ⚠️ 中低危   | 结合`ID 190`(温度)监控<br>突发增高需排查供电/振动问题                                 |
| **数据完整性**   | `smartctl_device_attribute{attribute_id="187", attribute_value_type="raw"} > 0`            | 不可纠正错误<br>(Reported_Uncorrect)        | >0 触发告警    | **数据完整性风险**<br>物理损坏或传输错误                                                | ⚠️⚠️⚠️ 致命 | 出现即立即检查文件系统                                                                |
| **温度监控**     | `smartctl_device_attribute{attribute_id="194", attribute_value_type="value"} > 55`         | 工作温度<br>(Temperature_Celsius)           | >55℃ 触发告警  | **关键协同指标**：<br>- 高温加速老化<br>- SSD>60℃ 性能降级<br>- 机械盘>70℃ 磁头故障风险 | ⚠️ 中危     | 告警阈值建议：<br>- HDD: 50℃<br>- SSD: 60℃                                            |
| **数据传输异常** | `smartctl_device_attribute{attribute_id="184", attribute_value_type="value"} > 0`          | 数据传输异常<br>(End-to-End_Error)          | >0 触发告警    | **关键协同指标**：<br>- 传输错误                                                        | ⚠️ 中危     | 出现即立即检查文件系统，数据存在丢失风险                                              |

### 在 Prom 中查询，带硬盘序列号

```
(smartctl_device_attribute{attribute_id="5",attribute_value_type="raw"} *
on(instance,device) group_left(serial_number,model_name,job) smartctl_device) > 0
```

```
(smartctl_device_attribute{attribute_id="173",attribute_value_type="value"} *
on(instance,device) group_left(serial_number,model_name,job) smartctl_device) < 80
```

```
(smartctl_device_attribute{attribute_id="233",attribute_value_type="value"} *
on(instance,device) group_left(serial_number,model_name,job) smartctl_device) < 80
```

```
(smartctl_device_attribute{attribute_id="184",attribute_value_type="raw"} *
on(instance,device) group_left(serial_number,model_name,job) smartctl_device) > 0
```

### smartctl 命令查看

```
smartctl -A /dev/sda | awk '$1 ~ /^(5|9|173|233|9|187|ID)/ {print}'
```

- Pre-fail 表示潜在故障风险
- Old_age 表示正常老化指标

### 告警信息

```
groups:
- name: smartctl_disk_failure_alert
  rules:

  # 1. 坏道检测 - 重分配扇区计数
  - alert: HDD_Reallocated_Sectors_Critical
    expr: smartctl_device_attribute{attribute_id="5", attribute_value_type="raw"} > 0
    for: 5m
    labels:
      severity: critical
      category: storage
    annotations:
      summary: "硬盘物理坏道告警 (ID 5)"
      description: "{{ $labels.instance }} 的硬盘 {{ $labels.device }} 检测到物理坏扇区!\n序列号: {{ $labels.serial_number }}\n型号: {{ $labels.model_name }}\n当前值: {{ $value }} (大于0表示已触发备用扇区替换)\n处理建议: 立即备份数据并更换硬盘"

  # 2. SSD健康度 (磨损平衡)
  - alert: SSD_Wear_Leveling_Warning
    expr: smartctl_device_attribute{attribute_id="173", attribute_value_type="value"} < 80
    for: 30m
    labels:
      severity: warning
      category: storage
    annotations:
      summary: "SSD磨损健康度下降 (ID 173)"
      description: "{{ $labels.instance }} 的SSD {{ $labels.device }} 寿命低于80%\n序列号: {{ $labels.serial_number }}\n型号: {{ $labels.model_name }}\n当前值: {{ $value }}\n处理建议: 检查备用块计数，准备更换硬盘"

  # 3. SSD剩余寿命
  - alert: SSD_Remaining_Life_Warning
    expr: smartctl_device_attribute{attribute_id="233", attribute_value_type="value"} < 50
    for: 15m
    labels:
      severity: warning
      category: storage
    annotations:
      summary: "SSD剩余寿命不足 (ID 233)"
      description: "{{ $labels.instance }} 的SSD {{ $labels.device }} 剩余寿命低于50%\n序列号: {{ $labels.serial_number }}\n型号: {{ $labels.model_name }}\n当前值: {{ $value }}%\n处理建议: 企业级SSD应立即更换，消费级建议更换"

  # 4. 老化风险检测 (修复模板语法)
  - alert: Disk_Aging_Risk
    expr: smartctl_device_attribute{attribute_id="9", attribute_value_type="raw"} / (24 * 365) > 4
    for: 1h
    labels:
      severity: warning
      category: storage
    annotations:
      summary: "硬盘老化风险 (ID 9)"
      description: "{{ $labels.instance }} 的硬盘已连续工作超过4年!\n序列号: {{ $labels.serial_number }}\n型号: {{ $labels.model_name }}\n当前通电小时数: {{ $value | humanizeDuration | printf \"%.0f\" }}\n处理建议: 标记为高危设备，优先考虑替换"

  # 5. 物理冲击警告 (移除无效函数)
  - alert: Disk_Physical_Shock
    expr: smartctl_device_attribute{attribute_id="12", attribute_value_type="raw"} > 100
    for: 10m
    labels:
      severity: warning
      category: storage
    annotations:
      summary: "异常物理冲击 (ID 12)"
      description: "{{ $labels.instance }} 的硬盘 {{ $labels.device }} 检测到异常启停!\n序列号: {{ $labels.serial_number }}\n型号: {{ $labels.model_name }}\n总启停次数: {{ $value }}\n处理建议: 检查电源稳定性和物理振动源"

  # 6. 数据完整性风险
  - alert: Data_Integrity_Failure
    expr: smartctl_device_attribute{attribute_id="187", attribute_value_type="raw"} > 0
    for: 2m
    labels:
      severity: critical
      category: storage
    annotations:
      summary: "不可纠正数据错误 (ID 187)"
      description: "{{ $labels.instance }} 的硬盘 {{ $labels.device }} 检测到数据完整性损坏!\n序列号: {{ $labels.serial_number }}\n型号: {{ $labels.model_name }}\n错误计数: {{ $value }}\n处理建议: 立即运行文件系统检查，考虑更换硬盘"

  # 7. 温度过高告警 (修复正则语法)
  - alert: Disk_Overtemperature
    expr: >-
      (smartctl_device_attribute{attribute_id="194", attribute_value_type="value"} > 55 and
       smartctl_device_attribute{attribute_id="194", model_name=~".*HDD.*"})
      or
      (smartctl_device_attribute{attribute_id="194", attribute_value_type="value"} > 60 and
       smartctl_device_attribute{attribute_id="194", model_name=~".*SSD.*"})
    for: 10m
    labels:
      severity: warning
      category: storage
    annotations:
      summary: "硬盘温度异常 (ID 194)"
      description: "{{ $labels.instance }} 的硬盘 {{ $labels.device }} 温度过高!\n序列号: {{ $labels.serial_number }}\n型号: {{ $labels.model_name }}\n当前温度: {{ $value }}°C\n处理建议: 检查散热系统，改善机柜通风"

  # 8. 数据传输异常
  - alert: Data_Transfer_Error
    expr: smartctl_device_attribute{attribute_id="184", attribute_value_type="raw"} > 0
    for: 5m
    labels:
      severity: critical
      category: storage
    annotations:
      summary: "端到端数据校验失败 (ID 184)"
      description: "{{ $labels.instance }} 的硬盘 {{ $labels.device }} 数据传输完整性错误!\n序列号: {{ $labels.serial_number }}\n型号: {{ $labels.model_name }}\n错误计数: {{ $value }}\n处理建议: 检查数据线/背板连接，更换SATA线缆"
```
