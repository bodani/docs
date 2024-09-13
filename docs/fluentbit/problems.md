
## 常见问题集合

#### 问题描述

当fluentbit 在运行过程中如何发生错误，会导致cpu持续升高，直到资源耗尽不可用。

#### 问题描述

output 到minio 错误信息
```
[2024/08/20 01:49:40] [error] [/root/go/src/fluent-bit/src/flb_http_client.c:1201 errno=32] Broken pipe
[2024/08/20 01:49:41] [error] [/root/go/src/fluent-bit/src/flb_http_client.c:1201 errno=32] Broken pipe
[2024/08/20 01:49:41] [error] [output:s3:s3.0] PutObject request failed
.....
[2024/08/20 02:09:45] [error] [output:s3:s3.0] PutObject request failed
[2024/08/20 02:10:05] [error] [output:s3:s3.0] PutObject API responded with error='SignatureDoesNotMatch', message='The request signature we calculated does not match the signature you provided. Check your key and signing method.'
[2024/08/20 02:10:05] [error] [output:s3:s3.0] Raw PutObject response: HTTP/1.1 403 Forbidden
Accept-Ranges: bytes
```
解决, minio 文件名过长
```
- s3_key_format   /$TAG/%Y/%m/%d/.log 
+ s3_key_format   /$TAG[4]/%Y/%m/%d/%H/%M/%S.log
```

#### 问题描述

上传到 minio 时 MultipartUpload 模式错误
```
[2024/08/15 02:52:11] [error] [output:s3:s3.2] CreateMultipartUpload: Could not parse response
[2024/08/15 02:52:11] [error] [output:s3:s3.2] CreateMultipartUpload request failed
[2024/08/15 02:52:11] [error] [output:s3:s3.2] Could not initiate multipart upload
[2024/08/15 02:52:19] [error] [output:s3:s3.2] CreateMultipartUpload: Could not parse response
[2024/08/15 02:52:19] [error] [output:s3:s3.2] CreateMultipartUpload request failed
```

解决 ，关闭MultipartUpload，采用单实例上传。 分批上传会产生多个worker 进程来进行上传。
```
use_put_object  On
```


^\[(?P<start_time>[^\]]*)\] "(?P<method>\S+) (?P<path>[^\"]*?) (?P<protocol>\S+)"
^\[(?<start_time>[^\]]*)\] "(?<method>\S+)(?: +(?<path>[^\"]*?)(?: +\S*)?)? (?<protocol>\S+)" (?<code>[^ ]*)



[2016-04-15T20:17:00.310Z] "POST /api/v1/locations HTTP/2" 204 - 154 0 226 100 "10.0.35.28" "nsq2http" "cc21d9b0-cf5c-432b-8c7e-98aeb7988cd2" "locations" "tcp://10.0.2.1:80"

[2024-08-21T01:14:56.707Z] "HEAD / HTTP/1.1" 404 NR route_not_found - "-" 0 0 0 - "10.0.0.15" "curl/7.81.0" "a01beb57-4024-4302-b96a-019c2de2c5e6" "10.2.14.4" "-" - - 10.0.2.42:80 10.0.0.15:38970 - -