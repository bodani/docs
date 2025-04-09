

updateStrategy:
  type: RollingUpdate
  rollingUpdate:
    partition: 3

3 个副本的 将 partition 从3 依次改成 2 ->1 -> 0 .实现分部重启


shell.options['dba.restartWaitTimeout']=300;

重启后重新加入集群
dba.getCluster().rejoinInstance('root@helmbroker-mysql-01-1:3306');

集群主节点切换
dba.getCluster().setPrimaryInstance('helmbroker-mysql-01-1:3306')



