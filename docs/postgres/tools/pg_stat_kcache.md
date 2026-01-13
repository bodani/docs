# pg_stat_kcache

`pg_stat_kcache` is an extension for PostgreSQL that provides statistics about the kernel's cache usage by PostgreSQL queries. It helps in monitoring and optimizing the performance of your PostgreSQL database by giving insights into the cache hit ratio and other related metrics.

## Installation

To install the `pg_stat_kcache` extension, follow these steps:

1. Connect to your PostgreSQL database:
    ```sh
    psql -U your_username -d your_database
    ```

2. Install the extension:
    ```sql
    CREATE EXTENSION pg_stat_kcache;
    ```

## Usage

Once installed, you can query the `pg_stat_kcache` view to get statistics about cache usage. Here is an example query:

```sql
SELECT * FROM pg_stat_kcache;
```

## Example Query

To get detailed statistics for a specific query, you can use the following example:

```sql
SELECT
    query,
    calls,
    total_time,
    read_time,
    write_time,
    user_time,
    system_time
FROM
    pg_stat_kcache
JOIN
    pg_stat_statements
ON
    pg_stat_kcache.queryid = pg_stat_statements.queryid
ORDER BY
    total_time DESC
LIMIT 10;
```

This query will return the top 10 queries by total execution time, along with their cache usage statistics.

## References

For more information, refer to the official documentation:
- [pg_stat_kcache GitHub Repository](https://github.com/powa-team/pg_stat_kcache)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
