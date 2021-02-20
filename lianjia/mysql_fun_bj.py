import pymysql
import logging
logging.basicConfig(level=logging.INFO)

# db_host = '10.10.66.102'
# db_port = 8306
# db_user = 'crosdev'
# db_password = 'crosdev'
db_name = 'lianjia1'
db_charset = 'utf8mb4'
db_host = '127.0.0.1'
db_port = 3306
db_user = 'root'
db_password = 'mysql'


def insert_batch_partition(data_in_list) :
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)

    # 获取游标
    cursor = conn.cursor()

    # 执行sql语句
    sql = 'INSERT INTO partitions_bj (partition_name, partition_url) VALUES (%s,%s)'
    rows = cursor.executemany(sql, data_in_list)

    # 提交
    conn.commit()

    # 关闭游标
    cursor.close()

    # 关闭连接
    conn.close()
    print(rows)


def filter_dup_partition_by_url(data_in_list):
    i_data_list = []
    if len(data_in_list)==0:
        return

    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)

    # 获取游标
    cursor = conn.cursor()

    for i in range(len(data_in_list)):
        ele = data_in_list[i]
        cursor.execute('select count(id) from partitions_bj where partition_url=\'%s\';' % ele[1])
        conn.commit()
        count = cursor.fetchone()[0]
        if count==0:
            i_data_list.append(ele)


    # 关闭游标
    cursor.close()
    return i_data_list


def select_partition(condition) :
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)

    cursor = conn.cursor()
    cursor.execute('select * from partitions_bj %s' % condition)
    conn.commit()
    cursor.close()
    conn.close()

    return cursor.fetchall()


def insert_partition():
    # 建立数据库连接
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)
    cursor = conn.cursor()
    sql = 'INSERT INTO partitions_bj (partition_name, partition_url) VALUES (%s,%s)'
    rows = cursor.execute(sql, ('4', 'qzcsbj4'))
    conn.commit()
    cursor.close()
    conn.close()
    print (rows)


def insert_community(commu_list):
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)

    # 获取游标
    cursor = conn.cursor()

    # 执行sql语句
    sql = 'INSERT INTO community_bj (d_name_py, c_name) VALUES (%s,%s)'
    rows = cursor.executemany(sql, commu_list)

    # 提交
    conn.commit()

    # 关闭游标
    cursor.close()

    # 关闭连接
    conn.close()
    print(rows)


def select_community(start, page):
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)
    cursor = conn.cursor()
    sql = 'select * from community_bj limit %d, %d' % (start, page)
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

    return cursor.fetchall()


def select_community_by_condition(condition):
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)
    cursor = conn.cursor()
    sql = 'select * from community_bj %s' % condition
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

    return cursor.fetchall()


def insert_batch_apartment(apartment_list, table_name_suffix):
    if len(apartment_list)==0:
        return
    else:
        conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                                password=db_password, db=db_name, charset=db_charset)
        cursor = conn.cursor()
        sql = 'INSERT INTO apartment_bj_%s' % table_name_suffix
        sql +=' (detail_url, summary, direct_name, partition_name, community_name) VALUES (%s, %s, %s, %s, %s)'
        rows = cursor.executemany(sql, apartment_list)

        # 提交
        conn.commit()
        cursor.close()
        conn.close()
        return rows


def apartment_insert_full(apartment_list, table_name_suffix):
    if not isinstance(apartment_list, list) or len(apartment_list) == 0:
        return
    else:
        conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                                password=db_password, db=db_name, charset=db_charset)
        cursor = conn.cursor()
        sql = 'INSERT INTO apartment_bj_%s' % table_name_suffix
        sql += ' (direct_name, partition_name, community_name, chengjiaoshijian, chengjiaojiage, guapaijiage,' \
               ' chengjiaozhouqi, fangwuhuxing, suozailouceng, jianzhumianji, huxingjiegou, jianzhuleixing,' \
               ' fangwuchaoxiang, jianchengniandai, zhuangxiuqingkuang, jianzhujiegou, gongnuanfangshi,' \
               ' tihubili, peibeidianti, jiaoyiquanshu, guapaishijian, fangwuyongtu, fangwunianxian, fangquansuoshu,' \
               ' detail_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s' \
               ', %s, %s, %s, %s, %s)'
        price_per_sm = apartment_list.pop(6)  # 平米均价
        try:
            cursor.execute(sql, tuple(apartment_list))
            row_id = cursor.lastrowid
            # 提交
            conn.commit()

            date_info = apartment_list[3].split('.')
            date_in_format = date_info[0] + '-' + date_info[1]
            sql_add_trans_record = 'insert into apartment_trans_record_bj_%s' % table_name_suffix
            sql_add_trans_record += '(apartment_id, record_price, price_per_sm, record_time) values (%s, %s, %s, %s)'
            cursor.execute(sql_add_trans_record, (row_id, str(apartment_list[4]) + '万', price_per_sm, date_in_format))

            conn.commit()
            return 1
        except :
            print('数据库连接错误')
            conn.rollback()
            return -1
        finally:
            cursor.close()
            conn.close()


# 更新分区表，写入分区准确的所属市区
def update_partition_bj(partition_id, direct_name):
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)
    cursor = conn.cursor()
    sql = 'update partitions_bj set direct_name=\'%s\' where id=%d' % (direct_name, partition_id)
    rows = cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

    return rows


def update_community_bj(p_name_py, direct_name, partition_url, partition_name):
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)
    cursor = conn.cursor()
    sql = 'update community_bj set direct_name=\'%s\', partition_url=\'%s\', partition_name=\'%s\' where p_name_py=\'%s\''\
          % (direct_name, partition_url, partition_name, p_name_py)
    rows = cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

    return rows


def update_community_bj_for_finish(community_id, flag, total_count):
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)
    cursor = conn.cursor()
    sql = 'update community_bj set finished=\'%d\', apartment_count=%d where id=\'%d\'' % (flag, total_count, community_id)
    rows = cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

    return rows


def select_apartments(reverse, direct_name, d_name_py, page_size):
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)
    if page_size > 1000:
        page_size = 1000
    cursor = conn.cursor()
    condition = ' and direct_name=\'%s\' ' % direct_name
    if reverse:
        condition += ' order by id desc '

    sql = 'select id, detail_url from apartment_bj_%s ' \
          ' where chengjiaoshijian is null %s limit 0, %d' % (d_name_py, condition, page_size)
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

    return cursor.fetchall()


# 先更新主表，再更新从表，遇到错误回滚
def update_apartment(d_name_py, apartment_info, trans_record_list):
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)
    cursor = conn.cursor()
    try :
        sql_update_apartment = 'update apartment_bj_%s' % d_name_py
        sql_update_apartment += ' set chengjiaoshijian=\'%s\', chengjiaojiage=\'%s\', pingjunjiage=\'%s\', guapaijiage=\'%s\', chengjiaozhouqi=\'%s\', fangwuhuxing=\'%s\', ' \
              'suozailouceng=\'%s\', jianzhumianji=\'%s\', huxingjiegou=\'%s\', taoneimianji=\'%s\', jianzhuleixing=\'%s\', fangwuchaoxiang=\'%s\', jianchengniandai=\'%s\', ' \
              'zhuangxiuqingkuang=\'%s\', jianzhujiegou=\'%s\', gongnuanfangshi=\'%s\', tihubili=\'%s\', peibeidianti=\'%s\', lianjiabianhao=\'%s\', jiaoyiquanshu=\'%s\', ' \
              'guapaishijian=\'%s\', fangwuyongtu=\'%s\', fangwunianxian=\'%s\', fangquansuoshu=\'%s\' where id=%d' % apartment_info
        cursor.execute(sql_update_apartment)
        conn.commit()

        sql_add_trans_record = 'insert into apartment_trans_record_bj_%s' % d_name_py
        sql_add_trans_record += ' (apartment_id, record_price, record_detail, record_time, price_per_sm)' \
              ' values (%s, %s, %s, %s, %s)'
        cursor.executemany(sql_add_trans_record, trans_record_list)
        conn.commit()
        return 1
    except IndexError:
        print('数据库操作异常，执行回滚操作。')
        conn.rollback()
        return -1
    finally:
        cursor.close()
        conn.close()


def del_apartment_by_id(d_name_py, apartment_id):
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)

    cursor = conn.cursor()
    sql = 'delete from apartment_bj_%s where id=%d' % (d_name_py,apartment_id)
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()


def etl(d_name_py):
    conn_102 = pymysql.connect(
        host='10.10.66.102',
        port=8306,
        user='crosdev',
        password='crosdev',
        db=db_name,
        charset=db_charset)
    cursor_102 = conn_102.cursor()

    conn_local = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)
    cursor_local = conn_local.cursor()

    # 抽取远程库的交易详情
    condition_apartment = 'where id>%d' % 423944
    apartment_fetch_sql = 'select chengjiaoshijian, chengjiaojiage, pingjunjiage, guapaijiage, chengjiaozhouqi, fangwuhuxing, ' \
          'suozailouceng, jianzhumianji, huxingjiegou, taoneimianji, jianzhuleixing, fangwuchaoxiang, jianchengniandai, ' \
          'zhuangxiuqingkuang, jianzhujiegou, gongnuanfangshi, tihubili, peibeidianti, lianjiabianhao, jiaoyiquanshu, ' \
          'guapaishijian, fangwuyongtu, fangwunianxian, fangquansuoshu, id from apartment_bj_%s %s' % (d_name_py, condition_apartment)
    cursor_102.execute(apartment_fetch_sql)
    conn_102.commit()
    apartment_list = list(cursor_102.fetchall())
    for apartment in apartment_list:
        print(apartment)

    # 交易详情写入本地库
    sql_import = 'update apartment_bj_%s' % d_name_py
    sql_import += ' set chengjiaoshijian=%s, chengjiaojiage=%s, pingjunjiage=%s, guapaijiage=%s, chengjiaozhouqi=%s, fangwuhuxing=%s, ' \
          'suozailouceng=%s, jianzhumianji=%s, huxingjiegou=%s, taoneimianji=%s, jianzhuleixing=%s, fangwuchaoxiang=%s, jianchengniandai=%s, ' \
          'zhuangxiuqingkuang=%s, jianzhujiegou=%s, gongnuanfangshi=%s, tihubili=%s, peibeidianti=%s, lianjiabianhao=%s, jiaoyiquanshu=%s, ' \
          'guapaishijian=%s, fangwuyongtu=%s, fangwunianxian=%s, fangquansuoshu=%s where id=%s'
    cursor_local.executemany(sql_import, apartment_list)
    conn_local.commit()

    # 抽取远程库中的交易记录数据
    sql_fetch_records = 'select apartment_id, record_price, record_detail, record_time, price_per_sm from apartment_trans_record_bj_%s' % d_name_py
    cursor_102.execute(sql_fetch_records)
    trans_records = list(cursor_102.fetchall())

    # 将交易记录写入本地库
    sql_import_records = 'insert into apartment_trans_record_bj_%s ' % d_name_py
    sql_import_records += ' (apartment_id, record_price, record_detail, record_time, price_per_sm)' \
          ' values (%s, %s, %s, %s, %s)'
    cursor_local.executemany(sql_import_records, trans_records)
    conn_local.commit()

    cursor_102.close()
    conn_102.close()
    cursor_local.close()
    conn_local.close()


# 一种更加智能的写法
def new_etl(d_name_py):
    conn_102 = pymysql.connect(
        host='10.10.66.102',
        port=8306,
        user='crosdev',
        password='crosdev',
        db=db_name,
        charset=db_charset)
    cursor_102 = conn_102.cursor()

    conn_local = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)
    cursor_local = conn_local.cursor()

    # 查找本地库中没有成交时间的ID
    need_update_sql = 'select id from apartment_bj_%s where chengjiaoshijian is null limit 0, 10000' % d_name_py
    rows = 1
    while rows > 0:
        rows = cursor_local.execute(need_update_sql)
        conn_local.commit()
        nn_apartment_list = cursor_local.fetchall()
        if len(nn_apartment_list) > 0:
            id_list = []
            for apartment_id in nn_apartment_list:
                id_list.append(apartment_id[0])
            # 再查询远程库对应的数据
            target_sql = 'select chengjiaoshijian, chengjiaojiage, pingjunjiage, guapaijiage, chengjiaozhouqi, ' \
                         'fangwuhuxing, suozailouceng, jianzhumianji, huxingjiegou, taoneimianji, jianzhuleixing,' \
                         ' fangwuchaoxiang, jianchengniandai, zhuangxiuqingkuang, jianzhujiegou, gongnuanfangshi,' \
                         ' tihubili, peibeidianti, lianjiabianhao, jiaoyiquanshu,  guapaishijian, fangwuyongtu,' \
                         ' fangwunianxian, fangquansuoshu, id from apartment_bj_%s where id in %s' % (d_name_py, tuple(id_list))
            cursor_102.execute(target_sql)
            conn_102.commit()
            apartment_list = list(cursor_102.fetchall())
            if len(apartment_list) == 0:
                print('未能在远程库查询到对应的记录，程序退出。')
                break
            # for apartment in apartment_list:
            #     print(apartment)
            # 交易详情写入本地库
            sql_import = 'update apartment_bj_%s' % d_name_py
            sql_import += ' set chengjiaoshijian=%s, chengjiaojiage=%s, pingjunjiage=%s, guapaijiage=%s, chengjiaozhouqi=%s, fangwuhuxing=%s, ' \
                          'suozailouceng=%s, jianzhumianji=%s, huxingjiegou=%s, taoneimianji=%s, jianzhuleixing=%s, fangwuchaoxiang=%s, jianchengniandai=%s, ' \
                          'zhuangxiuqingkuang=%s, jianzhujiegou=%s, gongnuanfangshi=%s, tihubili=%s, peibeidianti=%s, lianjiabianhao=%s, jiaoyiquanshu=%s, ' \
                          'guapaishijian=%s, fangwuyongtu=%s, fangwunianxian=%s, fangquansuoshu=%s where id=%s'
            cursor_local.executemany(sql_import, apartment_list)
            conn_local.commit()

            # 抽取远程库中的交易记录数据
            sql_fetch_records = 'select apartment_id, record_price, record_detail, record_time, price_per_sm from ' \
                                'apartment_trans_record_bj_%s where apartment_id in %s' % (d_name_py, tuple(id_list))
            cursor_102.execute(sql_fetch_records)
            trans_records = list(cursor_102.fetchall())
            # for record in trans_records:
            #     print(record)

            # 将交易记录写入本地库
            sql_import_records = 'insert into apartment_trans_record_bj_%s ' % d_name_py
            sql_import_records += ' (apartment_id, record_price, record_detail, record_time, price_per_sm)' \
                                  ' values (%s, %s, %s, %s, %s)'
            cursor_local.executemany(sql_import_records, trans_records)
            conn_local.commit()
            print('完成一组数据的处理。')
        else:
            print('未获取到任何需要执行的信息。')

    cursor_102.close()
    conn_102.close()
    cursor_local.close()
    conn_local.close()


def select_all_apartments(d_name_py):
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)
    cursor = conn.cursor()

    apartment_fetch_sql = 'select id, chengjiaoshijian, chengjiaojiage, pingjunjiage, guapaijiage, chengjiaozhouqi, fangwuhuxing, ' \
                          'suozailouceng, jianzhumianji, huxingjiegou, taoneimianji, jianzhuleixing, fangwuchaoxiang, jianchengniandai, ' \
                          'zhuangxiuqingkuang, jianzhujiegou, gongnuanfangshi, tihubili, peibeidianti, lianjiabianhao, jiaoyiquanshu, ' \
                          'guapaishijian, fangwuyongtu, fangwunianxian, fangquansuoshu, id from apartment_bj_%s' % d_name_py
    cursor.execute(apartment_fetch_sql)
    conn.commit()
    cursor.close()
    conn.close()

    return cursor.fetchall()


def select_trans_record_bj_by_apartment_id(d_name_py, apartment_id):
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)

    cursor = conn.cursor()
    sql = 'select apartment_id, record_price, price_per_sm, record_time from apartment_trans_record_bj_%s where ' \
          'apartment_id=\'%s\'' % (d_name_py, apartment_id)

    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

    return cursor.fetchall()


def select_all_trans_record(d_name_py):
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)

    cursor = conn.cursor()
    sql = 'select apartment_id, record_price, price_per_sm, record_time' \
          ' from apartment_trans_record_bj_%s order by record_time desc' % d_name_py

    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

    return cursor.fetchall()


def select_partition_name_in_direct(direct_name):
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)
    cursor = conn.cursor()

    sql = 'select partition_name from partitions_bj where direct_name=\'%s\'' % direct_name
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

    return cursor.fetchall()


def select_apartments_in_partition(d_name_py, partition_name):
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)
    cursor = conn.cursor()

    sql = 'select id, detail_url, summary, community_name, chengjiaoshijian, pingjunjiage, chengjiaojiage,' \
          ' fangwuhuxing, jianzhumianji, guapaijiage, chengjiaozhouqi, suozailouceng, huxingjiegou, taoneimianji,' \
          ' jianzhuleixing, fangwuchaoxiang, jianchengniandai, zhuangxiuqingkuang, jianzhujiegou, gongnuanfangshi,' \
          ' tihubili, peibeidianti, lianjiabianhao, jiaoyiquanshu, guapaishijian, fangwuyongtu, fangwunianxian,' \
          ' fangquansuoshu from apartment_bj_%s where partition_name=\'%s\' order by chengjiaoshijian desc'\
          % (d_name_py, partition_name)
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

    return cursor.fetchall()


def restore_records():

    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)

    cursor = conn.cursor()
    sql = 'select apartment_id, record_price, record_detail, record_time, price_per_sm from apartment_trans_record_bj_chy where apartment_id in (select id from apartment_bj_chp where id not in (select apartment_id from apartment_trans_record_bj_chp))'

    cursor.execute(sql)
    conn.commit()

    record_list = list(cursor.fetchall())
    sql_add_trans_record = 'insert into apartment_trans_record_bj_chp (apartment_id, record_price, record_detail,' \
                           ' record_time, price_per_sm) values (%s, %s, %s, %s, %s)'
    cursor.executemany(sql_add_trans_record, record_list)
    conn.commit()
    cursor.close()
    conn.close()


# 删除指定小区的所有房屋交易
def delete_apartment_by_community_name(table_name_suffix, community_name):
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)
    cursor = conn.cursor()
    sql = 'delete from apartment_bj_%s where community_name=%s' % (table_name_suffix, community_name)

    rows = cursor.execute(sql)
    conn.commit()

    cursor.close()
    conn.close()

    return rows


# 根据成交页的url进行查询
def select_apartments_by_detail_url(detail_url, table_suffix):
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)
    cursor = conn.cursor()

    apartment_fetch_sql = 'select id, detail_url, summary, community_name, chengjiaoshijian, chengjiaojiage, pingjunjiage, guapaijiage, chengjiaozhouqi, fangwuhuxing, ' \
                          'suozailouceng, jianzhumianji, huxingjiegou, taoneimianji, jianzhuleixing, fangwuchaoxiang, jianchengniandai, ' \
                          'zhuangxiuqingkuang, jianzhujiegou, gongnuanfangshi, tihubili, peibeidianti, lianjiabianhao, jiaoyiquanshu, ' \
                          'guapaishijian, fangwuyongtu, fangwunianxian, fangquansuoshu from apartment_bj_%s where detail_url=\'%s\''\
                          % (table_suffix, detail_url)
    cursor.execute(apartment_fetch_sql)
    conn.commit()
    cursor.close()
    conn.close()

    return cursor.fetchall()


def insert_trans_record(table_suffix, record_list):
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)

    cursor = conn.cursor()
    sql_add_trans_record = 'insert into apartment_trans_record_bj_%s' % table_suffix
    sql_add_trans_record += '(apartment_id, record_price, price_per_sm, record_time) values (%s, %s, %s, %s)'
    cursor.execute(sql_add_trans_record, record_list)
    conn.commit()
    cursor.close()
    conn.close()


def dup_clean():
    table_suffixes = ['xch']  # , 'chp', 'chy', 'ft', 'dch', 'dx', 'hd', 'xch']
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)
    cursor = conn.cursor()
    for suffix in table_suffixes:
        print('处理 %s 区的重复数据···' % suffix)
        query_sql = 'select count(detail_url), detail_url from apartment_bj_%s group by detail_url having count(' \
                    'detail_url) >1 limit 0,500' % suffix
        cursor.execute(query_sql)
        conn.commit()
        dup_url_list = cursor.fetchall()
        if len(dup_url_list)==0:
            logging.info('已经处理完毕，程序退出')
            break
        del_count_sum = 0
        for dup_url in dup_url_list:
            del_count_sum += dup_url[0] - 1
        logging.info('需要删除的记录数量为：%d' % del_count_sum)
        count_sql = 'select count(id) from apartment_bj_%s' % suffix
        cursor.execute(count_sql)
        conn.commit()
        count = cursor.fetchone()[0]
        logging.info('删除前数据库记录数：%d' % count)
        logging.info('理论上删除后数据库记录数：%d' % (count-del_count_sum))

        del_apartment_list = []
        for record in dup_url_list:
            logging.debug('重复的url： %s' % record[1])
            q_d_sql = 'select id, summary, direct_name, partition_name, community_name from apartment_bj_%s where ' \
                      'detail_url=\'%s\'' % (suffix, record[1])
            cursor.execute(q_d_sql)
            conn.commit()
            data_list = cursor.fetchall()

            del_ids = []
            record_count = record[0]
            for data in data_list:
                apartment_id = data[0]
                summary = data[1]
                # direct_name = data[2]
                community_name = data[4]
                if summary is None or community_name not in summary:
                    logging.info('小区信息和摘要信息不符，加入待删除列表。')
                    del_ids.append(str(apartment_id))

            if len(del_ids) == 0:
                logging.info('没有信息不符的记录，就把第二条以后的都删了')
                for i in range(1, record_count):
                    del_ids.append(str(data_list[i][0]))
            elif len(del_ids) == record_count:
                logging.info('竟然所有的小区名都跟摘要信息不符，没办法，留一条吧')
                del_ids.pop()

            logging.info('要删除的id数量：%d, 这一条url的数据量：%d' % (len(del_ids), record_count))

            del_apartment_list.extend(del_ids)

        del_id_str = ','.join(del_apartment_list)
        try:
            apartment_del_sql = 'delete from apartment_bj_%s where id in (%s)' % (suffix, del_id_str)
            cursor.execute(apartment_del_sql)
            conn.commit()
            logging.debug('删除主表记录: %s' % apartment_del_sql)
            trans_del_sql = 'delete from apartment_trans_record_bj_%s where apartment_id in (%s)' % (suffix, del_id_str)
            cursor.execute(trans_del_sql)
            conn.commit()
            logging.debug('删除从表记录: %s' % trans_del_sql)
        except Exception as err:
            logging.error("Error for execute sql: %s" % err)
            conn.rollback()
            return -1
        cursor.execute(count_sql)
        conn.commit()
        logging.info('删除后数据库记录数：%d' % cursor.fetchone())

    cursor.close()
    conn.close()


if __name__ == "__main__":
    for i in range(0, 3):
        dup_clean()
