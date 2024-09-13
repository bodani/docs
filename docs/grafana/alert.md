调用webhook
#!/bin/bash
curl -H "Content-Type: application/json" \
-X POST \
-d '{"msg_type": "text",
     "content": {
         "text": "测试信息"
     }
    }' \
https://webhook地址


curl -H "Content-Type: application/json" \
-X POST \
-d '{
    "timestamp": "1723776159",     
    "sign": "gwg2H/c79MK7BJF8A3uQl0+duKnAbuKxMUXz8ms9BQM=", 
    "msg_type": "text",
    "content": { "text": "request example"}
  }' \
https://open.feishu.cn/open-apis/bot/v2/hook/c76b4167-ee86-48eb-a616-2fc7d640bfba

{"msg_type":"text","content":{"text":"request example"}}

[ var='B0' metric='百科A区_bka54' labels={device=/dev/md127, fstype=xfs, idc=百科A区, instance=bka54, job=system, mountpoint=/data} value=83.18487280678053 ], [ var='B1' metric='百科B区_bkb55' labels={device=/dev/md127, fstype=xfs, idc=百科B区, instance=bkb55, job=system, mountpoint=/data} value=80.64210742368793 ]


调用alertmanager 
配置报警规则
https://help.aliyun.com/zh/grafana/user-guide/configure-grafana-native-alarm


https://www.feishu.cn/flow/api/trigger-webhook/66f1e8fc523fecd5e8886c9b12c14c16


#!/usr/bin/env bash
alerts_message='[
  {
    "labels": {
       "alertname": "磁盘已满",
       "dev": "sda1",
       "instance": "实例1",
       "msgtype": "testing"
     },
     "annotations": {
        "info": "程序员小王提示您：这个磁盘sda1已经满了，快处理！",
        "summary": "请检查实例示例1"
      }
  },
  {
    "labels": {
       "alertname": "磁盘已满",
       "dev": "sda2",
       "instance": "实例1",
       "msgtype": "testing"
     },
     "annotations": {
        "info": "程序员小王提示您：这个磁盘sda2已经满了，快处理！",
        "summary": "请检查实例示例1",
        "runbook": "以下链接http://test-url应该是可点击的"
      }
  }
]'


curl -XPOST -d"$alerts_message" http://127.0.0.1:9093/api/v1/alerts