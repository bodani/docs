## 解决 kubernetes 编辑 configmap 格式问题

# Step 1: 提取并编辑配置数据
```
kubectl get cm helmbroker-ch01 -o jsonpath='{.data.00_default_overrides\.xml}' > overrides.xml
vim overrides.xml
```
# Step 2: 将文件内容转换为单行字符串
```
xml_content=$(<overrides.xml)
json_data=$(jq -n --arg v "$xml_content" '{ "data": { "00_default_overrides.xml": $v } }')
```
# Step 3: 应用补丁

```
kubectl patch cm helmbroker-ch01 -p "$json_data"
```