## 组件协作架构

###  各组件角色
组件	职责
Nessie	存储 Iceberg 表的元数据版本（如分支、提交记录），提供 REST API 接口
MinIO	存储 Iceberg 表的数据文件（Parquet/ORC）和元数据文件（metadata.json）
Spark	访问 Nessie  REST API 接口 通过 Nessie Catalog 管理元数据版本
Keycloak 对nessie 提供 OpenID 认证
Postgres 用于 nessie , keycloak 数据存储

通过 Nessie 的 版本化 Catalog 能力，Spark 可以在 Iceberg 表上实现类似 Git 的分支管理，同时 MinIO 提供低成本存储支持。这种架构适合需要多环境隔离（如开发/生产分支）和协作式数据湖场景。

参见 https://blog.csdn.net/biyeshejizhishi/article/details/142349823

一、Nessie 核心作用

Nessie 是类似 Git 的 分布式数据湖元数据服务，为 Iceberg 提供以下核心能力：

    版本控制：支持分支（Branch）、标签（Tag）、合并（Merge）等 Git 式操作，记录表结构（Schema）、分区等元数据变更历史。
    原子性提交：保证跨多表的元数据变更原子性，避免部分更新导致数据不一致。
    全局目录服务：作为 Iceberg Catalog 的统一入口，协调 Spark、Flink、Dremio 等工具访问同一版本元数据。

## 部署

### postgresql, minio 略

### 部署Keycloak

docker-compose.yaml
```
version: '3'
services:
  keycloak:
    image: quay.io/keycloak/keycloak:26.1.2
    ports:
      - "8080:8080"
      - "9001:9000"
    environment:
      KC_BOOTSTRAP_ADMIN_USERNAME: admin
      KC_BOOTSTRAP_ADMIN_PASSWORD: admin
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://10.0.60.28:15432/keylocak
      KC_DB_USERNAME: keycocak
      KC_DB_PASSWORD: 123456
    command: [
      "start",
      "--features=token-exchange",
      "--spi-connections-jpa-quarkus-migration-strategy=update",
      "--health-enabled=true",
      "--http-enabled=true",
      "--hostname-strict=false"
    ]
    healthcheck:
      test: "exec 3<>/dev/tcp/localhost/9000 && echo -e 'GET /health/ready HTTP/1.1\\r\\nHost: localhost\\r\\nConnection: close\\r\\n\\r\\n' >&3 && cat <&3 | grep -q '200 OK'"
      interval: 5s
      timeout: 2s
      retries: 15
```

访问http://localhost:8080创建管理员账号。

#### 创建Realm与客户端：

    新建Realm（如data-lake），用于隔离数据湖相关配置。
    创建客户端（Client）：
        Client ID：nessie-client
        Valid Redirect URIs：http://nessie-server:19120/*（Nessie服务地址）
        Access Type：confidential（需客户端密钥认证）
        生成client-secret并保存。 
    配置 Client scopes
     catalog
    
##### 配置用户与角色：

    添加用户（如spark-user），设置密码。
    创建角色（如data_engineer、admin），并分配权限（如BRANCH_CREATE）。
    为用户分配角色。 

#### 设置keycloak
https://projectnessie.org/guides/keycloak/?h=keycloak#setting-up-keycloak

##### 验证

curl http://keycloak:8080/realms/data-lake/protocol/openid-connect/token --resolve keycloak:8080:127.0.0.1 --user nessie-client:KdAo5WeQRrSOMyjJgPQcpUyU6c6cOikq -d 'grant_type=client_credentials' -d 'scope=catalog' 

token=$(curl http://keycloak:8080/realms/data-lake/protocol/openid-connect/token --resolve keycloak:8080:127.0.0.1 --user nessie-client:QIFul6x1H0jTxInEozVyukGYsHel61B1 -d 'grant_type=client_credentials' -d 'scope=catalog' | jq -r .access_token)

curl -v http://127.0.0.1:19120/api/v2/config -H "Authorization: Bearer $token"
curl -v http://127.0.0.1:19120/iceberg/v1/config -H "Authorization: Bearer $token"

### 配置nessis


依赖 postgres minio keycloak

```
version: '3'

services:

  nessie:
    # IMPORTANT: when upgrading Nessie images, make sure to update the spark-sql packages as well
    image: ghcr.io/projectnessie/nessie:0.103.0
    ports:
      # API port
      - "19120:19120"
      # Management port (metrics and health checks)
      - "9000:9000"
    environment:
      # Version store settings.
      # This example uses Postgres as the version store.
      - nessie.version.store.type=JDBC
      - nessie.version.store.persist.jdbc.datasource=postgresql
      - quarkus.datasource.postgresql.jdbc.url=jdbc:postgresql://10.0.60.28:15432/catalog
      - quarkus.datasource.postgresql.username=catalog
      - quarkus.datasource.postgresql.password=catalog
      # AuthN settings.
      # This examples uses Keycloak for authentication.
      - nessie.server.authentication.enabled=true
      - quarkus.oidc.auth-server-url=http://keycloak:8080/realms/data-lake
      - quarkus.oidc.client-id=nessie-client
      - quarkus.oidc.token.issuer=http://keycloak:8080/realms/data-lake
      # Object store settings.
      # This example uses MinIO as the object store.
      - nessie.catalog.default-warehouse=warehouse
      - nessie.catalog.warehouses.warehouse.location=s3://demobucket/
      - nessie.catalog.service.s3.default-options.region=us-east-1
      - nessie.catalog.service.s3.default-options.path-style-access=true
      - nessie.catalog.service.s3.default-options.access-key=urn:nessie-secret:quarkus:nessie.catalog.secrets.access-key
      - nessie.catalog.secrets.access-key.name=minioadmin
      - nessie.catalog.secrets.access-key.secret=minioadmin
      # MinIO endpoint
      - nessie.catalog.service.s3.default-options.endpoint=http://10.0.60.28:9002/
    healthcheck:
      test: "exec 3<>/dev/tcp/localhost/9000 && echo -e 'GET /q/health HTTP/1.1\\r\\nHost: localhost\\r\\nConnection: close\\r\\n\\r\\n' >&3 && cat <&3 | grep -q '200 OK'"
      interval: 5s
      timeout: 2s
      retries: 15
    extra_hosts:
      - "keycloak:10.0.60.28"
```

备注： nessie 对minio进行统一管理, 而不再spark 等client 中指定

官网的两处说明: 

https://projectnessie.org/guides/try-nessie/ NOTE 

https://projectnessie.org/guides/iceberg-rest/#migrate-an-iceberg-client-configuration

退出 http://keycloak:8080/realms/data-lake/account

### spark-sql
```
version: '3'
services:
  spark-sql:
    image: apache/spark:3.5.4-java17-python3
    depends_on:
      nessie:
        condition: service_healthy
    stdin_open: true
    tty: true
    ports:
      - "4040-4045:4040-4045"
    healthcheck:
      test: "curl localhost:4040"
      interval: 5s
      retries: 15
    command: [
      /opt/spark/bin/spark-sql,
      --packages, "org.projectnessie.nessie-integrations:nessie-spark-extensions-3.5_2.12:0.99.0,org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.6.0,software.amazon.awssdk:bundle:2.28.17,software.amazon.awssdk:url-connection-client:2.28.17",
      --conf, "spark.sql.extensions=org.projectnessie.spark.extensions.NessieSparkSessionExtensions,org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
      --conf, "spark.sql.catalog.nessie=org.apache.iceberg.spark.SparkCatalog",
      --conf, "spark.sql.catalog.nessie.type=rest",
      --conf, "spark.sql.catalog.nessie.uri=http://nessie:19120/iceberg/main",
      --conf, "spark.sql.catalog.nessie.oauth2-server-uri=http://keycloak:8080/realms/data-lake/protocol/openid-connect/token",
      --conf, "spark.sql.catalog.nessie.credential=nessie-client:KdAo5WeQRrSOMyjJgPQcpUyU6c6cOikq",
      --conf, "spark.sql.catalog.nessie.scope=catalog",
      --conf, "spark.sql.catalogImplementation=in-memory",
      --conf, "spark.jars.ivy=/tmp/.ivy2",
    ]
    volumes:
      - ./tmp/:/tmp/.ivy2
    extra_hosts:
      - "nessie:10.0.60.28"
      - "keycloak:10.0.60.28"
```

### nessie-cli

```
version: '3'
services:
  nessie-cli:
      image: ghcr.io/projectnessie/nessie-cli:0.103.0
      tty: true
      command: [
        --uri, "http://nessie:19120/api/v2",
        --client-option, "nessie.enable-api-compatibility-check=false",
        # Options for the internal Nessie client
        --client-option, "nessie.authentication.type=OAUTH2",
        --client-option, "nessie.authentication.oauth2.issuer-url=http://keycloak:8080/realms/data-lake",
        --client-option, "nessie.authentication.oauth2.client-id=nessie-client",
        --client-option, "nessie.authentication.oauth2.client-secret=KdAo5WeQRrSOMyjJgPQcpUyU6c6cOikq",
        --client-option, "nessie.authentication.oauth2.client-scopes=catalog sign",
        # Options for the internal Iceberg REST client
        #--client-option, "uri=http://nessie:19120/iceberg/main",
        #--client-option, "oauth2-server-uri=http://keycloak:8080/realms/iceberg/protocol/openid-connect/token",
        #--client-option, "credential=nessie-client:KdAo5WeQRrSOMyjJgPQcpUyU6c6cOikq",
        #--client-option, "scope=catalog",
      ]
      extra_hosts:
       - "nessie:10.0.60.28"
       - "keycloak:10.0.60.28"
```
配置可以成功创建连接，但是执行命令一直卡、 用下面的方式


CONNECT TO 'http://nessie:19120/iceberg/main'
USING 
  nessie.ref = 'main' AND 
  nessie.authentication.type = 'OAUTH2' AND 
  nessie.authentication.oauth2.client-id = 'nessie-client' AND 
  nessie.authentication.oauth2.client-secret = 'KdAo5WeQRrSOMyjJgPQcpUyU6c6cOikq' AND 
  nessie.authentication.oauth2.token-endpoint = 'http://keycloak:8080/realms/data-lake/protocol/openid-connect/token';

CONNECT TO 'http://10.1.50.200:19120/api/v2'
USING 
  nessie.ref = 'main' AND 
  nessie.authentication.type = 'OAUTH2' AND 
  nessie.authentication.oauth2.client-id = 'nessie-client' AND 
  nessie.authentication.oauth2.client-secret = 'KdAo5WeQRrSOMyjJgPQcpUyU6c6cOikq' AND 
  nessie.authentication.oauth2.token-endpoint = 'http://10.1.50.201:8080/realms/data-lake/protocol/openid-connect/token';

#### nessie 配置 附录
```properties
# 
# Copyright (C) 2020 Dremio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Nessie settings
### default base branch name
nessie.server.default-branch=main  # 设置默认的基础分支名称为“main”
nessie.server.send-stacktrace-to-client=false  # 是否将堆栈跟踪发送给客户端，默认为false

# To provide secrets via a keystore via Quarkus, the following configuration
# options need to be configured accordingly.
# For details see https://quarkus.io/guides/config-secrets#store-secrets-in-a-keystore
#smallrye.config.source.keystore."properties".path=properties  # keystore的路径
#smallrye.config.source.keystore."properties".password=arealpassword  # keystore的密码
#smallrye.config.source.keystore."properties".handler=aes-gcm-nopadding  # keystore的处理方式
#smallrye.config.source.keystore."key".path=key  # 密钥的路径
#smallrye.config.source.keystore."key".password=anotherpassword  # 密钥的密码

# Reverse Proxy Settings
#
# These config options are mentioned only for documentation purposes. Consult the
# Quarkus documentation for "Running behind a reverse proxy" and configure those
# depending on your actual needs.
#
# See https://quarkus.io/guides/http-reference#reverse-proxy
#
# Do NOT enable these option unless your reverse proxy (for example istio or nginx)
# is properly setup to set these headers but also filter those from incoming requests.
#
#quarkus.http.proxy.proxy-address-forwarding=true  # 代理地址转发
#quarkus.http.proxy.allow-x-forwarded=true  # 允许X-Forwarded头
#quarkus.http.proxy.enable-forwarded-host=true  # 启用Forwarded-Host头
#quarkus.http.proxy.enable-forwarded-prefix=true  # 启用Forwarded-Prefix头
#quarkus.http.proxy.trusted-proxies=127.0.0.1  # 信任的代理列表

# Support for external secrets managers - see http://127.0.0.1:8000/nessie-latest/configuration/#secrets-manager-settings
#
#nessie.secrets.type=  # 外部密钥管理器类型
# VAULT:  Hashicorp Vault. See https://docs.quarkiverse.io/quarkus-vault/dev/index.html#configuration-reference
#         for the Quarkus docs for Hashicorp Vault for specific information.
# AMAZON: AWS Secrets Manager. See https://docs.quarkiverse.io/quarkus-amazon-services/dev/amazon-secretsmanager.html#_configuration_reference
#         for the Quarkus docs for Amazon Services / Secrets Manager for specific information.
# AZURE:  AWS Secrets Manager. NOT SUPPORTED YET!
#         See https://docs.quarkiverse.io/quarkus-azure-services/dev/quarkus-azure-key-vault.html#_extension_configuration_reference
#         for the Quarkus docs for Azure Key Vault
# GOOGLE: Google Cloud Secrets Manager. NOT SUPPORTED YET!
#nessie.secrets.cache.max-elements=1000  # 密钥缓存的最大元素数量
#nessie.secrets.cache.ttl=PT15M  # 密钥缓存的TTL（存活时间）
#
# When using Google Cloud Secret Manager you may have to configure this to 'true'
quarkus.google.cloud.enable-metadata-server=false  # 是否启用Google Cloud元数据服务器
# To enable a specific secrets manager consult the documentations for those, more
# information here: https://projectnessie.org/nessie-latest/configuration/#secrets-manager-settings

##### Nessie Catalog

# Optional: validate that referenced secrets exist (default is false)
#nessie.catalog.validate-secrets=true  # 验证引用的秘密是否存在

# Optional: disable health check for object stores (default is true)
#nessie.catalog.object-stores.health-check.enabled=false  # 禁用对象存储的健康检查

# Iceberg default config (can be overridden per warehouse)
#nessie.catalog.iceberg-config-defaults.prop=value  # Iceberg默认配置
#nessie.catalog.iceberg-config-overrides.prop=value  # Iceberg配置覆盖

# Warehouses

# default warehouse
#nessie.catalog.default-warehouse=warehouse  # 默认仓库
#nessie.catalog.warehouses.warehouse.location=<object-store-URI>  # 仓库位置
#nessie.catalog.warehouses.warehouse.iceberg-config-defaults.prop-name=prop-value  # 仓库的Iceberg默认配置
#nessie.catalog.warehouses.warehouse.iceberg-config-overrides.prop-name=prop-value  # 仓库的Iceberg配置覆盖
# additional warehouses
#nessie.catalog.warehouses.another-warehouse.location=<object-store-URI>  # 额外仓库的位置

# S3 settings

# default S3 settings
#nessie.catalog.service.s3.default-options.endpoint=http://localhost:9000  # 默认S3设置的端点
#nessie.catalog.service.s3.default-options.path-style-access=false  # 路径样式访问
#nessie.catalog.service.s3.default-options.region=us-west-2  # 区域设置
#nessie.catalog.service.s3.default-options.access-key=urn:nessie-secret:quarkus:my-secrets.s3-default  # 访问密钥
#my-secrets.s3-default.name=awsAccessKeyId  # 密钥名称
#my-secrets.s3-default.secret=awsSecretAccessKey  # 密钥内容
# per-bucket S3 settings
#nessie.catalog.service.s3.buckets.bucket1.endpoint=s3a://bucket1  # 每个桶的设置
#nessie.catalog.service.s3.buckets.bucket1.access-key=urn:nessie-secret:quarkus:my-secrets.s3-bucket  # 桶的访问密钥
#nessie.catalog.service.s3.buckets.bucket1.region=us-east-1  # 桶的区域
#my-secrets.s3-bucket.name=awsAccessKeyId1  # 桶的密钥名称
#my-secrets.s3-bucket.secret=awsSecretAccessKey1  # 桶的密钥内容

# GCS settings

#nessie.catalog.service.gcs.default-options.host=http://localhost:4443  # GCS默认设置的主机
#nessie.catalog.service.gcs.default-options.project-id=nessie  # GCS默认设置的项目ID
#nessie.catalog.service.gcs.default-options.auth-type=access_token  # GCS默认设置的授权类型
#nessie.catalog.service.gcs.default-options.oauth2-token=urn:nessie-secret:quarkus:my-secrets.gcs-default  # GCS默认设置的OAuth2令牌
#my-secrets.gcs-default.token=tokenRef  # GCS默认设置的令牌引用
# per-bucket GCS settings
#nessie.catalog.service.gcs.buckets.bucket1.host=http://localhost:4443  # 每个桶的主机
#nessie.catalog.service.gcs.buckets.bucket1.project-id=nessie  # 每个桶的项目ID
#nessie.catalog.service.gcs.buckets.bucket1.auth-type=access_token  # 每个桶的授权类型
#nessie.catalog.service.gcs.buckets.bucket1.oauth2-token=urn:nessie-secret:quarkus:my-secrets.gcs-bucket  # 每个桶的OAuth2令牌
#my-secrets.gcs-bucket.token=tokenRef  # 每个桶的令牌引用

# ADLS settings

#nessie.catalog.service.adls.default-options.endpoint=http://localhost/adlsgen2/bucket  # ADLS默认设置的端点
#nessie.catalog.service.adls.default-options.auth-type=none  # ADLS默认设置的授权类型
#nessie.catalog.service.adls.default-options.account=urn:nessie-secret:quarkus:my-secrets.adls-default  # ADLS默认设置的账户
#nessie.catalog.service.adls.default-options.configuration.propname=propvalue  # ADLS默认设置的配置
#my-secrets.adls-default.name=account  # ADLS默认设置的账户名称
#my-secrets.adls-default.secret=secret  # ADLS默认设置的密钥
# per-file-system ADLS settings
#nessie.catalog.service.adls.file-systems.bucket1.endpoint=http://localhost/adlsgen2/bucket  # 每个文件系统的端点
#nessie.catalog.service.adls.file-systems.bucket1.auth-type=none  # 每个文件系统的授权类型
#nessie.catalog.service.adls.file-systems.bucket1.account=urn:nessie-secret:quarkus:my-secrets.adls-fs  # 每个文件系统的账户
#nessie.catalog.service.adls.file-systems.bucket1.configuration.propname=propvalue  # 每个文件系统的配置
#my-secrets.adls-fs.name=account  # 每个文件系统的账户名称
#my-secrets.adls-fs.secret=secret  # 每个文件系统的密钥


## Nessie authorization settings
### This will perform authorization on branches/tags and content where rule definitions are
### using a Common Expression Language (CEL) expression (an intro to CEL can be found at https://github.com/google/cel-spec/blob/master/doc/intro.md).
### Rule definitions are of the form nessie.server.authorization.rules.<ruleId>=<rule_expression>
### Available variables within the <rule_expression> are: 'op' / 'role' / 'ref' / 'path'
### The 'op' variable in the <rule_expression> can be any of:
### 'VIEW_REFERENCE', 'CREATE_REFERENCE', 'DELETE_REFERENCE', 'READ_ENTRIES', 'READ_CONTENT_KEY', 'LIST_COMMIT_LOG',
### 'COMMIT_CHANGE_AGAINST_REFERENCE', 'ASSIGN_REFERENCE_TO_HASH', 'UPDATE_ENTITY', 'READ_ENTITY_VALUE', 'DELETE_ENTITY', 'VIEW_REFLOG'
### The 'role' refers to the user's role and can be any string
### The 'ref' refers to a string representing a branch/tag name
### The 'path' refers to the Key for the content of an object and can be any string
### Some "use-case-based" example rules are shown below (in practice you might rather create a single rule that allows e.g. branch creation/deletion/commits/...):
# nessie.server.authorization.enabled=false  # 是否启用授权
# nessie.server.authorization.type=CEL  # 授权类型为CEL
# nessie.server.authorization.rules.allow_branch_listing=\
#   op=='VIEW_REFERENCE' && role.startsWith('test_user') && ref.startsWith('allowedBranch')  # 允许分支列表查看规则
# nessie.server.authorization.rules.allow_branch_creation=\
#   op=='CREATE_REFERENCE' && role.startsWith('test_user') && ref.startsWith('allowedBranch')  # 允许分支创建规则
# nessie.server.authorization.rules.allow_branch_deletion=\
#   op=='DELETE_REFERENCE' && role.startsWith('test_user') && ref.startsWith('allowedBranch')  # 允许分支删除规则
# nessie.server.authorization.rules.allow_listing_commitlog=\
#   op=='LIST_COMMIT_LOG' && role.startsWith('test_user') && ref.startsWith('allowedBranch')  # 允许提交日志列表规则
# nessie.server.authorization.rules.allow_entries_reading=\
#   op=='READ_ENTRIES' && role.startsWith('test_user') && ref.startsWith('allowedBranch')  # 允许条目读取规则
# nessie.server.authorization.rules.allow_assigning_ref_to_hash=\
#   op=='ASSIGN_REFERENCE_TO_HASH' && role.startsWith('test_user') && ref.startsWith('allowedBranch')  # 允许分配引用到哈希规则
# nessie.server.authorization.rules.allow_commits=\
#   op=='COMMIT_CHANGE_AGAINST_REFERENCE' && role.startsWith('test_user') && ref.startsWith('allowedBranch')  # 允许提交规则
# nessie.server.authorization.rules.allow_reading_entity_value=\
#   op=='READ_ENTITY_VALUE' && role=='test_user' && path.startsWith('allowed.')  # 允许读取实体值规则
# nessie.server.authorization.rules.allow_updating_entity=\
#   op=='UPDATE_ENTITY' && role=='test_user' && path.startsWith('allowed.')  # 允许更新实体规则
# nessie.server.authorization.rules.allow_deleting_entity=\
#   op=='DELETE_ENTITY' && role=='test_user' && path.startsWith('allowed.')  # 允许删除实体规则
# nessie.server.authorization.rules.allow_commits_without_entity_changes=\
#   op=='COMMIT_CHANGE_AGAINST_REFERENCE' && role=='test_user2' && ref.startsWith('allowedBranch')  # 允许没有实体更改的提交规则
# nessie.server.authorization.rules.allow_all=\
#   op in ['VIEW_REFERENCE','CREATE_REFERENCE','DELETE_REFERENCE','LIST_COMMITLOG','READ_ENTRIES','LIST_COMMIT_LOG',\
#   'COMMIT_CHANGE_AGAINST_REFERENCE','ASSIGN_REFERENCE_TO_HASH','UPDATE_ENTITY','READ_ENTITY_VALUE','DELETE_ENTITY'] \
#   && role=='admin_user'  # 允许所有操作规则
# nessie.server.authorization.rules.allow_listing_reflog=\
#   op=='VIEW_REFLOG' && role=='admin_user'  # 允许查看引用日志规则

### which type of version store to use: IN_MEMORY, ROCKSDB, DYNAMODB2, MONGODB2, CASSANDRA2, JDBC2, BIGTABLE.
# Note: the version store type JDBC is deprecated, please use the Nessie Server Admin Tool to migrate to JDBC2.
# Note: the version store type CASSANDRA is deprecated, please use the Nessie Server Admin Tool to migrate to CASSANDRA2.
# Note: the version store type DYNAMODB is deprecated, please use the Nessie Server Admin Tool to migrate to DYNAMODB2.
# Note: the version store type MONGODB is deprecated, please use the Nessie Server Admin Tool to migrate to MONGODB2.
nessie.version.store.type=IN_MEMORY  # 使用的版本存储类型

# Object cache size as a value relative to the JVM's max heap size. The `cache-capacity-fraction-adjust-mb`
# value will be "kept free" when calculating the effective cache size. Set `cache-capacity-fraction-of-heap`
# to 0 to use a fixed size.
# Entirely disabling the cache is not recommended and will negatively affect performance.
#nessie.version.store.persist.cache-capacity-fraction-of-heap=0.7  # 缓存容量相对于堆的比例
#nessie.version.store.persist.cache-capacity-fraction-adjust-mb=256  # 缓存容量调整MB
# When having very small heaps, use the `cache-capacity-fraction-min-size-mb` value. Set to `0` to disable
# the min cache capacity.
#nessie.version.store.persist.cache-capacity-fraction-min-size-mb=64  # 缓存最小容量MB
# Fixed size of Nessie's object cache in MB.
# Settings this value to 0 disables the fixed size object cache.
# Entirely disabling the cache is not recommended and will negatively affect performance.
#nessie.version.store.persist.cache-capacity-mb=0  # 固定大小的缓存容量MB

## Transactional database configuration

# Note: Nessie Quarkus Server comes with built-in support for Postgres and MariaDB, or any database
# compatible with these.
# Select the datasource to use with the `nessie.version.store.persist.jdbc.datasource` property;
# The possible built-in values are: "default" (deprecated), "postgresql", "mariadb", "mysql" and "h2".
#nessie.version.store.persist.jdbc.datasource=default  # 数据源选择

# Default datasource configuration (deprecated; use quarkus.datasource.postgresql.* instead):
quarkus.datasource.db-kind=postgresql  # 数据库类型为PostgreSQL
quarkus.datasource.active=false  # 数据源是否激活
quarkus.datasource.devservices.enabled=false  # 是否启用开发服务
#quarkus.datasource.jdbc.url=jdbc:postgresql://localhost:5432/my_database  # 数据库URL
#quarkus.datasource.username=<your username>  # 数据库用户名
#quarkus.datasource.password=<your password>  # 数据库密码

# Postgres datasource configuration:
quarkus.datasource.postgresql.db-kind=postgresql  # PostgreSQL数据源的数据库类型
quarkus.datasource.postgresql.active=false  # PostgreSQL数据源是否激活
quarkus.datasource.postgresql.devservices.enabled=false  # 是否启用PostgreSQL开发服务
#quarkus.datasource.postgresql.jdbc.url=jdbc:postgresql://localhost:5432/my_database  # PostgreSQL数据库URL
#quarkus.datasource.postgresql.username=<your username>  # PostgreSQL数据库用户名
#quarkus.datasource.postgresql.password=<your password>  # PostgreSQL数据库密码

# MariaDB datasource configuration:
quarkus.datasource.mariadb.db-kind=mariadb  # MariaDB数据源的数据库类型
quarkus.datasource.mariadb.active=false  # MariaDB数据源是否激活
quarkus.datasource.mariadb.devservices.enabled=false  # 是否启用MariaDB开发服务
#quarkus.datasource.mariadb.username=<your username>  # MariaDB数据库用户名
#quarkus.datasource.mariadb.password=<your password>  # MariaDB数据库密码
#quarkus.datasource.mariadb.jdbc.url=jdbc:mariadb://localhost:3306/my_database  # MariaDB数据库URL
# Do not remove or modify the following, as these optimization flags are incompatible with Nessie;
# see https://mariadb.com/docs/server/connect/programming-languages/java/batch.
quarkus.datasource.mariadb.jdbc.additional-jdbc-properties.useBulkStmts=false  # 禁用批量语句
quarkus.datasource.mariadb.jdbc.additional-jdbc-properties.useBulkStmtsForInserts=false  # 禁用批量插入

# MySQL datasource configuration:
quarkus.datasource.mysql.db-kind=mariadb  # MySQL数据源的数据库类型
quarkus.datasource.mysql.active=false  # MySQL数据源是否激活
quarkus.datasource.mysql.devservices.enabled=false  #

