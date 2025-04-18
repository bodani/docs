#!/bin/python3
# -*- coding: utf-8 -*-

import click
import psycopg2
import time
import sys,os
from urllib.parse import parse_qs, urlparse

SRC_CONN=None
DEST_CONN=None

SRC_CONN_INFO=""
DEST_CONN_INFO=""

def log(msg):
   click.echo("%s \033[32mINFO\033[0m: %s" % (time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()),msg))

def error(msg):
   click.echo("%s \033[31mERROR\033[0m: %s" % (time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()),msg))

@click.group(help='数据迁移步骤： check -> start-mgirate -> show-progress -> verify ->  原库停止写入  -> sync-sequence - >  业务切换至新库 -> finish-migrate')
@click.option('--src_conn',  default="", help='"dbname=test user=postgres password=secret host=localhost port=5432 connect_timeout=10 sslmode=disable"')
@click.option('--dest_conn', default="", help='"dbname=test user=postgres password=secret host=localhost port=5432 connect_timeout=10 sslmode=disable"')
def cli(src_conn,dest_conn):
    global SRC_CONN 
    global DEST_CONN 
    global SRC_CONN_INFO
    global DEST_CONN_INFO
    
    SRC_CONN_INFO=src_conn
    DEST_CONN_INFO=dest_conn
    # 建立连接
    SRC_CONN = psycopg2.connect(src_conn)
    DEST_CONN = psycopg2.connect(dest_conn)

    SRC_CONN.autocommit = True
    log('源端已建立连接')
    DEST_CONN.autocommit = True
    log('目标端已建立连接')

def parse_conn_string(conn_str):
    """将连接字符串解析为字典"""
    params = {}
    # 替换空格为 & 以便解析
    conn_str = conn_str.replace(" ", "&")
    parsed = parse_qs(conn_str)
    for key in parsed:
        params[key] = parsed[key][0]  # 取第一个值
    return params

def run_sql_one(conn,sql):
    cursor = conn.cursor()
    cursor.execute(sql)
    data = cursor.fetchone()
    return data

def run_sql_excute(conn,sql):
    cursor = conn.cursor()
    cursor.execute(sql)

def run_sql_batch(conn,sql):
    cursor = conn.cursor()
    cursor.execute(sql)
    datas = cursor.fetchall()
    return datas

@click.command(help='数据迁移前环境检测')
def check():
    sql = "SELECT VERSION()"
    log("源数据库版本: %s" % run_sql_one(SRC_CONN,sql))
    log("目标数据库版本: %s" % run_sql_one(DEST_CONN,sql))
### wal_level
    wal_level = run_sql_one(SRC_CONN,"select current_setting('wal_level');")

    if(wal_level[0] != "logical"):
        error("源端数据库要求wal_level必须为 logical ,当前数据库wal_level: %s" %(wal_level[0]))
        return
    log("数据库wal_level: %s,OK!" % wal_level[0])
### 是否表不满足订阅的表
    sql = """
        select  relname FROM pg_class c JOIN pg_namespace n ON c.relnamespace = n.oid, LATERAL (SELECT array_agg(contype) AS ri FROM pg_constraint WHERE conrelid = c.oid) con
        WHERE relkind = 'r' AND nspname = 'public' AND relreplident = 'd' and con.ri is null;
        """
    tables = run_sql_one(SRC_CONN,sql)
    if(tables is not None):
        error("缺失复制标识的表")
        error(tables)
        error("please use : alter table public.xxx_talbe replica identity xxx")
        return
    log("数据库表满足发布条件， OK！")

### 是否存在锁等待 

    sql = "select count(pid) from pg_stat_activity where state = 'idle in transaction'";
    result = run_sql_one(SRC_CONN,sql)
    if result[0] > 0:
        error("源数据库中存在锁等待事件")
        return

### 数据库基本信息统计
    sql = """
        select pg_size_pretty(pg_database_size(current_database()));
    """
    db_size = run_sql_one(SRC_CONN,sql)
    log("数据库大小: %s" % db_size)
    
    sql = """
        select count(1) from pg_tables where schemaname='public';
    """
    table_num = run_sql_one(SRC_CONN,sql)
    log("共: %s 张表" % table_num)
    if table_num == 0:
        error("提前结束")
        return

    sql = """
      select tablename,  pg_size_pretty(pg_total_relation_size(tablename::regclass)) size from  pg_tables 
      where schemaname='public' order by pg_total_relation_size(tablename::regclass) desc limit 10;
    """
    table_size_top_10 = run_sql_batch(SRC_CONN,sql)
    log("表大小 top10")
    for table in  table_size_top_10:
        log(table)

    sql = "select extname,extversion from pg_extension"
    extensions = run_sql_batch(SRC_CONN,sql)
    log("拓展列表:")
    for extension in  extensions:
        log(extension)
    for extension in  extensions:
        sql = "select name,version from pg_available_extension_versions where name = '%s'" % extension[0]
        result = run_sql_one(DEST_CONN,sql)
        if result is None:
            error("请在目标数据库中提前安装 %s 拓展的依赖！"  % extension[0])
            return
            
    log("拓展列表检测 OK!")

    log("本地运行环境检测")
    if os.system("whereis pg_dump") !=0 :
        error("导出表结构使用pg_dump,请保证本地环境可以运行pg_dump")
    if os.system("whereis sql") !=0 :
        error("导入表结构使用psql,请保证本地环境可以运行psql")

    sql = "select count(1) from pg_sequences where schemaname = 'public'" 
    result = run_sql_one(SRC_CONN,sql)
    if result is not None and result[0] > 0:
       log("是否存在序列： 是")
    else:
       log("是否存在序列： 否")

    log("所有检测完毕！结果通过!")
    log("接下来请使用: migrate.py start_migrate 进行数据迁移!")

@click.command('start-migate',help="进行数据迁移")
def start_migrate():
    log("拓展迁移")
    sql = "select extname from pg_extension";
    extensions = run_sql_batch(SRC_CONN,sql)
    for extension in  extensions:
        # extionsion 中存在特殊符号
        sql = """create extension IF NOT EXISTS "%s" """ % extension[0]
        run_sql_excute(DEST_CONN,sql)
        log(extension[0]+ "  OK！")

    log("迁移表结构")
    migrate_schema()
    log("源端发布数据")
    publication_tables()
    log("目标端订阅数据")
    supscribtion_tables()

    show_migrete_stat()

    log("开始数据迁移 watch migrate.py show_progress 查看迁移进度!")

def show_migrete_stat():
    sql= "select client_addr,to_char(backend_start,'YYYY-MM-DD HH24:MI:SS'),state,sent_lsn,write_lsn,flush_lsn,replay_lsn,sync_state from pg_stat_replication where application_name = 'pg_tea_subscription'"
    result = run_sql_one(SRC_CONN,sql)
    log("复制信息")
    log("(client_addr,backend_start,state,sent_lsn,write_lsn,flush_lsn,replay_lsn,sync_state)")
    log(result)

    sql = " select pubname,pubowner,puballtables,pubinsert,pubupdate,pubdelete from pg_publication where pubname='pg_tea_public'"
    log("发布信息")
    log("(pubname,pubowner,puballtables,pubinsert,pubupdate,pubdelete)")
    result = run_sql_one(SRC_CONN,sql)
    log(result)

    sql = " select subenabled,subslotname,subpublications from pg_subscription where subname='pg_tea_subscription';"
    log("订阅信息")
    log("(subenabled,subslotname,subpublications)")
    result = run_sql_one(DEST_CONN,sql)
    log(result)


def publication_tables():
    sql = "CREATE PUBLICATION pg_tea_public FOR ALL TABLES"
    run_sql_excute(SRC_CONN,sql)
    log("源端创建数据发布完成")
    
def supscribtion_tables():
    sql = "CREATE SUBSCRIPTION pg_tea_subscription CONNECTION '%s' PUBLICATION pg_tea_public" %  SRC_CONN_INFO
    log(sql)
    run_sql_excute(DEST_CONN,sql)
    log("目标端创建订阅完成")

@click.command('sync-sequence',help='同步序列')
def sync_sequence():
    run_sql_excute(SRC_CONN,"CHECKPOINT;CHECKPOINT;")
    run_sql_excute(DEST_CONN,"ANALYZE;")
    sql = "select sequencename,last_value,increment_by from pg_sequences where schemaname = 'public'"
    sequences = run_sql_batch(SRC_CONN,sql)
    if sequences is not None:
        for sequence in sequences:
            if sequence[1] is not None:
                update_seq_sql = "SELECT setval('public.%s', %s);" % (sequence[0], sequence[1])
                run_sql_excute(DEST_CONN,update_seq_sql)
    log("序列同步完成")

@click.command('show-progress',help='查看数据迁移进度')
def show_progress():
    sql = """
        select pg_current_wal_lsn() curren_lsn , replay_lsn,sync_state ,pg_wal_lsn_diff(pg_current_wal_lsn(),replay_lsn) diff_lsn
        from pg_stat_replication where application_name = 'pg_tea_subscription'
        """
    log("同步数据进度,延迟")
    log("(原库lsn,目标库 lsn, 同步状态 ,同步延迟")
    result = run_sql_one(SRC_CONN,sql)
    log(result)
  
    sql = "select received_lsn ,latest_end_lsn, to_char(last_msg_send_time,'YYYY-MM-DD HH24:MI:SS'),to_char(last_msg_receipt_time,'YYYY-MM-DD HH24:MI:SS'),to_char(latest_end_time,'YYYY-MM-DD HH24:MI:SS') from pg_stat_subscription where subname = 'pg_tea_subscription'";
    log("数据接受情况")
    log("(最新接收到lsn ,最新完成同步 lsn,最新发送时间,最新接收时间,最新同步时间")
    result = run_sql_one(DEST_CONN,sql)
    log(result)

    sql = "select sum(case when srsubstate='r' then 1 else 0  end) as done, sum(case when srsubstate = 'r' then 0 else 1 end) as  migrating from pg_subscription_rel join pg_subscription on  pg_subscription.oid = srsubid where subname='pg_tea_subscription'"
    result = run_sql_one(DEST_CONN,sql)
    log("已完成迁移表: %s, 正在迁移中表: %s" % (result[0],result[1]))
    if result[1] > 0:
        sql = "select  srrelid::regclass t_name,srsubstate  from pg_subscription_rel join pg_subscription on  pg_subscription.oid = srsubid where subname='pg_tea_subscription' and  srsubstate<>'r' order by srsubstate limit 5"
        result = run_sql_batch(DEST_CONN,sql)
        if result is not None:
            log("正在迁移表状态: i = 初始化， d = 正在复制数据， s = 已同步， r = 准备好")
            for t in result:
                log(t)

def migrate_schema():
    log(SRC_CONN_INFO)
    log(DEST_CONN_INFO)
    cmd = "pg_dump '%s' --schema-only -n public | psql '%s' " % (SRC_CONN_INFO,DEST_CONN_INFO)
    log(cmd)
    if os.system(cmd) != 0:
        error("表结构迁移失败！")
        return
    log("表结构迁移完成！")

@click.command('verify',help='数据迁移结果验证')
def verify():
    pass

@click.command('finish-migrate',help='数据迁移完成，清理订阅发布及复制槽')
def finish_migrate():
    run_sql_excute(SRC_CONN,"CHECKPOINT;CHECKPOINT;")
    log("源端checkpoint ok!")
    run_sql_excute(DEST_CONN,"ANALYZE;")
    log("目标端 analyze ok!")

    run_sql_excute(DEST_CONN,"ALTER SUBSCRIPTION pg_tea_subscription DISABLE;")
    run_sql_excute(DEST_CONN," DROP SUBSCRIPTION pg_tea_subscription;")
    log("清理订阅及逻辑复制槽完毕!")
    
    run_sql_excute(SRC_CONN," DROP PUBLICATION pg_tea_public; ")
    log("清理发布完毕!")
    log("finish_migrate done!")

cli.add_command(check)
cli.add_command(start_migrate)
cli.add_command(show_progress)
cli.add_command(verify)
cli.add_command(finish_migrate)
cli.add_command(sync_sequence)

if __name__ == '__main__':
  try:  
    cli()
  finally:
    if SRC_CONN is not None:
        SRC_CONN.close()
    if SRC_CONN is not None:
     SRC_CONN.close()
"""
python pg_migrate.py --s_host=10.10.2.11 --s_user=supper_test --s_database=pgbench --s_password=123456 --s_port=5432 --d_host=10.10.2.12 --d_user=supper_dest --d_database=pgbench --d_password=123456 --d_port=15432 check
"""

"""

sudo pip install pyinstaller

pyinstaller --clean -F pg_migrate.py
"""
