show clusters;

CREATE DATABASE db5 ON CLUSTER cluster

CREATE TABLE db5.table1 ON CLUSTER cluster
(
    `id` UInt64,
    `column1` String
)
ENGINE = ReplicatedMergeTree
ORDER BY id


CREATE TABLE db5.table1_dist ON CLUSTER cluster
(
    `id` UInt64,
    `column1` String
)
ENGINE = Distributed('cluster', 'db5', 'table1', rand())


INSERT INTO db5.table1 (id, column1) VALUES (1, 'rep1');
INSERT INTO db5.table1 (id, column1) VALUES (2, 'rep2');
INSERT INTO db5.table1 (id, column1) VALUES (3, 'rep3');

INSERT INTO db5.table1_dist (id, column1) VALUES (4, 'rep4');
INSERT INTO db5.table1_dist (id, column1) VALUES (5, 'rep5');
INSERT INTO db5.table1_dist (id, column1) VALUES (6, 'rep6');


select hostName(),* from db5.table1;
select hostName(),* from db5.table1_dist;



echo ruok | nc 10.2.14.13 2181

echo mntr | nc localhost 9181