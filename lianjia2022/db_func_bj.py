import pymysql


class DBOperateSet(object):
    __conn = None

    def __init__(self, db):
        if db == 1:
            self.__conn = pymysql.connect(
                host='127.0.0.1',
                port=3306,
                user='root',
                password='mysql',
                db='lianjia',
                charset='utf8mb4')
        else:
            self.__conn = pymysql.connect(
                host='10.10.66.102',
                port=8306,
                user='crosdev',
                password='crosdev',
                db='lianjia',
                charset='utf8mb4')

    def before_quit(self):
        self.__conn.close()

    def insert_batch_partition(self, data_in_list):
        cursor = self.__conn.cursor()
        sql = 'INSERT INTO partitions_bj (partition_name, partition_url) VALUES (%s,%s)'
        rows = cursor.executemany(sql, data_in_list)
        self.__conn.commit()
        cursor.close()
        print(rows)

    def filter_dup_partition_by_url(self, data_in_list):
        i_data_list = []
        if len(data_in_list) == 0:
            return

        cursor = self.__conn.cursor()

        for i in range(len(data_in_list)):
            ele = data_in_list[i]
            cursor.execute('select count(id) from partitions_bj where partition_url=\'%s\';' % ele[1])
            self.__conn.commit()
            count = cursor.fetchone()[0]
            if count == 0:
                i_data_list.append(ele)
        cursor.close()
        return i_data_list

    def select_partition(self, condition):
        cursor = self.__conn.cursor()
        cursor.execute('select * from partitions_bj %s' % condition)
        self.__conn.commit()
        cursor.close()

        return cursor.fetchall()

    def insert_partition(self):
        # 建立数据库连接
        cursor = self.__conn.cursor()
        sql = 'INSERT INTO partitions_bj (partition_name, partition_url) VALUES (%s,%s)'
        rows = cursor.execute(sql, ('4', 'qzcsbj4'))
        self.__conn.commit()
        cursor.close()
        print(rows)

    def insert_community(self, commu_list):
        cursor = self.__conn.cursor()

        sql = 'INSERT INTO community_bj_2022 (d_name_py, c_name) VALUES (%s,%s)'
        rows = cursor.executemany(sql, commu_list)

        self.__conn.commit()
        cursor.close()
        print(rows)

    def select_community(self, start, page):
        cursor = self.__conn.cursor()
        sql = 'select * from community_bj_2022 limit %d, %d' % (start, page)
        cursor.execute(sql)
        self.__conn.commit()
        cursor.close()

        return cursor.fetchall()

    def select_community_by_condition_2022(self, condition):
        cursor = self.__conn.cursor()
        sql = 'select * from community_bj_2022 %s' % condition
        cursor.execute(sql)
        self.__conn.commit()
        cursor.close()

        return cursor.fetchall()

    def insert_batch_apartment(self, apartment_list, table_name_suffix):
        if len(apartment_list) == 0:
            return
        else:
            cursor = self.__conn.cursor()
            sql = 'INSERT INTO apartment_bj_%s' % table_name_suffix
            sql += ' (detail_url, summary, direct_name, partition_name, community_name) VALUES (%s, %s, %s, %s, %s)'
            rows = cursor.executemany(sql, apartment_list)

            # 提交
            self.__conn.commit()
            cursor.close()
            return rows

    # 更新分区表，写入分区准确的所属市区
    def update_partition_bj(self, partition_id, direct_name):
        cursor = self.__conn.cursor()
        sql = 'update partitions_bj set direct_name=\'%s\' where id=%d' % (direct_name, partition_id)
        rows = cursor.execute(sql)
        self.__conn.commit()
        cursor.close()

        return rows

    def update_community_bj_2022(self, p_name_py, direct_name, partition_url, partition_name):
        cursor = self.__conn.cursor()
        sql = 'update community_bj_2022 set direct_name=\'%s\', partition_url=\'%s\', partition_name=\'%s\' where ' \
              'p_name_py=\'%s\'' % (direct_name, partition_url, partition_name, p_name_py)
        rows = cursor.execute(sql)
        self.__conn.commit()
        cursor.close()

        return rows

    def update_community_bj_2022_for_finish(self, community_id, flag, total_count):
        cursor = self.__conn.cursor()
        sql = 'update community_bj_2022 set finished=\'%d\', apartment_count=%d where id=\'%d\'' % (
                                                                                        flag, total_count, community_id)
        rows = cursor.execute(sql)
        self.__conn.commit()
        cursor.close()

        return rows

    def select_apartments(self, reverse, direct_name, d_name_py, page_size):
        if page_size > 1000:
            page_size = 1000
        cursor = self.__conn.cursor()
        condition = ' and direct_name=\'%s\' ' % direct_name
        if reverse:
            condition += ' order by id desc '

        sql = 'select id, detail_url from apartment_bj_%s ' \
              ' where chengjiaoshijian is null %s limit 0, %d' % (d_name_py, condition, page_size)
        cursor.execute(sql)
        self.__conn.commit()
        cursor.close()

        return cursor.fetchall()

    # 先更新主表，再更新从表，遇到错误回滚
    def update_apartment(self, d_name_py, apartment_info, trans_record_list):
        cursor = self.__conn.cursor()
        try:
            sql_update_apartment = 'update apartment_bj_%s' % d_name_py
            sql_update_apartment += ' set chengjiaoshijian=\'%s\', chengjiaojiage=\'%s\', pingjunjiage=\'%s\', guapaijiage=\'%s\', chengjiaozhouqi=\'%s\', fangwuhuxing=\'%s\', ' \
                                    'suozailouceng=\'%s\', jianzhumianji=\'%s\', huxingjiegou=\'%s\', taoneimianji=\'%s\', jianzhuleixing=\'%s\', fangwuchaoxiang=\'%s\', jianchengniandai=\'%s\', ' \
                                    'zhuangxiuqingkuang=\'%s\', jianzhujiegou=\'%s\', gongnuanfangshi=\'%s\', tihubili=\'%s\', peibeidianti=\'%s\', lianjiabianhao=\'%s\', jiaoyiquanshu=\'%s\', ' \
                                    'guapaishijian=\'%s\', fangwuyongtu=\'%s\', fangwunianxian=\'%s\', fangquansuoshu=\'%s\' where id=%d' % apartment_info
            cursor.execute(sql_update_apartment)
            self.__conn.commit()

            sql_add_trans_record = 'insert into apartment_trans_record_bj_%s' % d_name_py
            sql_add_trans_record += ' (apartment_id, record_price, record_detail, record_time, price_per_sm)' \
                                    ' values (%s, %s, %s, %s, %s)'
            cursor.executemany(sql_add_trans_record, trans_record_list)
            self.__conn.commit()
            return 1
        except IndexError:
            print('数据库操作异常，执行回滚操作。')
            self.__conn.rollback()
            return -1
        finally:
            cursor.close()

    def del_apartment_by_id(self, d_name_py, apartment_id):

        cursor = self.__conn.cursor()
        sql = 'delete from apartment_bj_%s where id=%d' % (d_name_py, apartment_id)
        cursor.execute(sql)
        self.__conn.commit()
        cursor.close()

    def select_all_apartments(self, d_name_py):
        cursor = self.__conn.cursor()

        apartment_fetch_sql = 'select id, chengjiaoshijian, chengjiaojiage, pingjunjiage, guapaijiage, chengjiaozhouqi, fangwuhuxing, ' \
                              'suozailouceng, jianzhumianji, huxingjiegou, taoneimianji, jianzhuleixing, fangwuchaoxiang, jianchengniandai, ' \
                              'zhuangxiuqingkuang, jianzhujiegou, gongnuanfangshi, tihubili, peibeidianti, lianjiabianhao, jiaoyiquanshu, ' \
                              'guapaishijian, fangwuyongtu, fangwunianxian, fangquansuoshu, id from apartment_bj_%s' % d_name_py
        cursor.execute(apartment_fetch_sql)
        self.__conn.commit()
        cursor.close()

        return cursor.fetchall()

    def select_trans_record_bj_by_apartment_id(self, d_name_py, apartment_id):

        cursor = self.__conn.cursor()
        sql = 'select apartment_id, record_price, price_per_sm, record_time from apartment_trans_record_bj_%s where ' \
              'apartment_id=\'%s\'' % (d_name_py, apartment_id)

        cursor.execute(sql)
        self.__conn.commit()
        cursor.close()

        return cursor.fetchall()

    def select_all_trans_record(self, d_name_py):
        cursor = self.__conn.cursor()
        sql = 'select apartment_id, record_price, price_per_sm, record_time from apartment_trans_record_bj_%s' % d_name_py

        cursor.execute(sql)
        self.__conn.commit()
        cursor.close()

        return cursor.fetchall()

    def select_partition_name_in_direct(self, direct_name):
        cursor = self.__conn.cursor()

        sql = 'select partition_name from partitions_bj where direct_name=\'%s\'' % direct_name
        cursor.execute(sql)
        self.__conn.commit()
        cursor.close()

        return cursor.fetchall()

    def select_apartments_in_partition(self, d_name_py, partition_name):
        cursor = self.__conn.cursor()

        apartment_fetch_sql = 'select id, detail_url, summary, community_name, chengjiaoshijian, chengjiaojiage, pingjunjiage, guapaijiage, chengjiaozhouqi, fangwuhuxing, ' \
                              'suozailouceng, jianzhumianji, huxingjiegou, taoneimianji, jianzhuleixing, fangwuchaoxiang, jianchengniandai, ' \
                              'zhuangxiuqingkuang, jianzhujiegou, gongnuanfangshi, tihubili, peibeidianti, lianjiabianhao, jiaoyiquanshu, ' \
                              'guapaishijian, fangwuyongtu, fangwunianxian, fangquansuoshu from apartment_bj_%s where partition_name=\'%s\'' \
                              % (d_name_py, partition_name)
        cursor.execute(apartment_fetch_sql)
        self.__conn.commit()
        cursor.close()

        return cursor.fetchall()

    def restore_records(self):

        cursor = self.__conn.cursor()
        sql = 'select apartment_id, record_price, record_detail, record_time, price_per_sm from ' \
              'apartment_trans_record_bj_chy where apartment_id in (select id from apartment_bj_chp where id not in (' \
              'select apartment_id from apartment_trans_record_bj_chp)) '

        cursor.execute(sql)
        self.__conn.commit()

        record_list = list(cursor.fetchall())
        sql_add_trans_record = 'insert into apartment_trans_record_bj_chp (apartment_id, record_price, record_detail,' \
                               ' record_time, price_per_sm) values (%s, %s, %s, %s, %s)'
        cursor.executemany(sql_add_trans_record, record_list)
        self.__conn.commit()
        cursor.close()

    # 删除指定小区的所有房屋交易
    def delete_apartment_by_community_name(self, table_name_suffix, community_name):
        cursor = self.__conn.cursor()
        sql = 'delete from apartment_bj_%s where community_name=%s' % (table_name_suffix, community_name)

        rows = cursor.execute(sql)
        self.__conn.commit()

        cursor.close()

        return rows


# 一种更加智能的写法
def new_etl(d_name_py):
    conn_102 = pymysql.connect(
        host='10.10.66.102',
        port=8306,
        user='crosdev',
        password='crosdev',
        db='lianjia',
        charset='')
    cursor_102 = conn_102.cursor()

    conn_local = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='mysql',
        db='lianjia',
        charset='utf8mb4')
    cursor_local = conn_local.cursor()

    # 查找本地库中没有成交时间的ID
    need_update_sql = 'select id from apartment_bj_%s where chengjiaoshijian is null limit 0, 10000' % d_name_py
    rows = 1
    while rows > 0:
        rows = cursor_local.execute(need_update_sql)
        conn_local.commit()
        nn_apartment_list = cursor_local.fetchall()
        if len(nn_apartment_list) > 0:
            print('本地查询，需要转移的数据条数：%d' % len(nn_apartment_list))
            id_list = []
            for apartment_id in nn_apartment_list:
                id_list.append(apartment_id[0])
            # 再查询远程库对应的数据
            target_sql = 'select chengjiaoshijian, chengjiaojiage, pingjunjiage, guapaijiage, chengjiaozhouqi, ' \
                         'fangwuhuxing, suozailouceng, jianzhumianji, huxingjiegou, taoneimianji, jianzhuleixing,' \
                         ' fangwuchaoxiang, jianchengniandai, zhuangxiuqingkuang, jianzhujiegou, gongnuanfangshi,' \
                         ' tihubili, peibeidianti, lianjiabianhao, jiaoyiquanshu,  guapaishijian, fangwuyongtu,' \
                         ' fangwunianxian, fangquansuoshu, id from apartment_bj_%s where id in %s' % (
                             d_name_py, tuple(id_list))
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
                                'apartment_trans_record_bj_%s where apartment_id in %s' % (
                                    d_name_py, tuple(id_list))
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
