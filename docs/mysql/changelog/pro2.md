## Public Key Retrieval is not allowed

解决 java.sql.SQLNonTransientConnectionException: Public Key Retrieval is not allowed 错误

在使用 MySQL 8.0 或更高版本时，可能会遇到以下错误：java.sql.SQLNonTransientConnectionException: Public Key Retrieval is not allowed
这是因为 MySQL 8.0 默认启用了 caching_sha2_password 插件，而 JDBC 驱动默认不允许检索公钥。以下是几种常见的解决方法：
解决方案一：修改数据库连接字符串

在 JDBC 连接 URL 中添加 allowPublicKeyRetrieval=true 参数：

jdbc:mysql://localhost:3306/your_database?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC

    1

    allowPublicKeyRetrieval=true：允许检索公钥。
    useSSL=false：禁用 SSL，视需求而定。

解决方案二：修改 MySQL 用户认证插件

ALTER USER 'your_user'@'your_host' IDENTIFIED WITH mysql_native_password BY 'your_password';

    1

解决方案三：更新 MySQL JDBC 驱动

确保使用最新版的 MySQL JDBC 驱动，以避免与 MySQL 8.0 的认证方式不兼容
Maven 示例：

<dependency>
    <groupId>mysql</groupId>
    <artifactId>mysql-connector-java</artifactId>
    <version>8.0.30</version>
</dependency>

总结

    如果不想修改认证插件，使用 allowPublicKeyRetrieval=true 解决问题。
    可以修改用户认证插件为 mysql_native_password，或更新 JDBC 驱动。