#!/usr/bin/python
# encoding=utf-8

import pymysql

# db_host = '10.10.66.102'
# db_port = 8306
# db_user = 'crosdev'
# db_password = 'crosdev'
db_name = 'lianjia'
db_charset = 'utf8mb4'
db_host = '127.0.0.1'
db_port = 3306
db_user = 'root'
db_password = 'mysql'


# 批量插入分区
def insert_batch_partition(data_in_list):
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)

    # 获取游标
    cursor = conn.cursor()

    # 执行sql语句
    sql = 'INSERT INTO partitions_sz (partition_name, partition_url) VALUES (%s,%s)'
    rows = cursor.executemany(sql, data_in_list)

    # 提交
    conn.commit()

    # 关闭游标
    cursor.close()

    # 关闭连接
    conn.close()
    return rows


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
        cursor.execute('select count(id) from partitions_sz where partition_url=\'%s\';' % ele[1])
        conn.commit()
        count = cursor.fetchone()[0]
        if count==0:
            i_data_list.append(ele)


    # 关闭游标
    cursor.close()
    return i_data_list


def select_partition(start_index, page_size) :
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)

    # 获取游标
    cursor = conn.cursor()

    # 执行sql语句
    cursor.execute('select * from partitions_sz limit %d, %d' % (start_index, page_size))

    # 提交
    conn.commit()

    # 关闭游标
    cursor.close()

    # 关闭连接
    conn.close()
    partitions = cursor.fetchall()
    urls = []
    for partition in partitions:
        urls.append(partition[2])
    return urls


def insert_community(commu_list):
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)

    # 获取游标
    cursor = conn.cursor()

    # 执行sql语句
    sql = 'INSERT INTO community_sz (d_name_py, c_name) VALUES (%s,%s)'
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
    sql = 'select * from community_sz limit %d, %d' % (start, page)
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

    return cursor.fetchall()


def insert_batch_apartment(apartment_list):
    if len(apartment_list)==0:
        return
    else:
        conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)
        cursor = conn.cursor()
        sql = 'INSERT INTO apartment_sz (detail_url, summary, partition_url, community_name) VALUES (%s, %s, %s, %s)'
        rows = cursor.executemany(sql, apartment_list)

        # 提交
        conn.commit()
        cursor.close()
        conn.close()
        return rows


def select_apartments(reverse, max_id, page_size):
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)
    if page_size > 1000:
        page_size = 1000
    cursor = conn.cursor()
    if reverse:
        condition = ' and id>%d order by id desc ' % max_id
    else:
        condition = ' and id<=%d ' % max_id
    sql = 'select id, detail_url from apartment_sz ' \
          ' where chengjiaoshijian is null %s limit 0, %d' % (condition, page_size)
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

    return cursor.fetchall()


def del_apartment_by_id(apartment_id):
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)

    cursor = conn.cursor()
    sql = 'delete from apartment_sz where id=%d' % apartment_id
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()


def update_apartment(param_data):
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)

    # 获取游标
    cursor = conn.cursor()

    # 执行sql语句
    sql = 'update apartment_sz set chengjiaoshijian=\'%s\', chengjiaojiage=\'%s\', pingjunjiage=\'%s\', guapaijiage=\'%s\', chengjiaozhouqi=\'%s\', fangwuhuxing=\'%s\', ' \
          'suozailouceng=\'%s\', jianzhumianji=\'%s\', huxingjiegou=\'%s\', taoneimianji=\'%s\', jianzhuleixing=\'%s\', fangwuchaoxiang=\'%s\', jianchengniandai=\'%s\', ' \
          'zhuangxiuqingkuang=\'%s\', jianzhujiegou=\'%s\', gongnuanfangshi=\'%s\', tihubili=\'%s\', peibeidianti=\'%s\', lianjiabianhao=\'%s\', jiaoyiquanshu=\'%s\', ' \
          'guapaishijian=\'%s\', fangwuyongtu=\'%s\', fangwunianxian=\'%s\', fangquansuoshu=\'%s\' where id=%d' % param_data
    rows = cursor.execute(sql)

    conn.commit()
    cursor.close()
    conn.close()

    return rows


def add_apartment_community_name():
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)

    cursor = conn.cursor()
    sql = 'select id, summary from apartment_sz where community_name is null limit 0, 1000'
    cursor.execute(sql)
    conn.commit()
    apartment_list = cursor.fetchall()
    community_name_list = []
    for apartment in apartment_list:
        summary = apartment[1].split(' ')
        apartment_id = apartment[0]
        community_name_list.append((summary[0], apartment_id))
    print (community_name_list)
    if len(community_name_list)>0 :
        sql = 'update apartment_sz set community_name=%s where id=%s'
        cursor.executemany(sql, community_name_list)
        conn.commit()

    cursor.close()
    conn.close()


def add_trans_record(apartment_id, record_price, record_detail):
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)
    details = record_detail.split(',')
    record_time = details[1].replace('成交','')
    sql = 'insert into apartment_trans_record_sz (apartment_id, record_price, record_detail, record_time)' \
          ' values (%s, %s, %s, %s)'
    cursor = conn.cursor()
    cursor.execute(sql, (apartment_id, record_price, record_detail, record_time))
    conn.commit()
    cursor.close()
    conn.close()


def restore_data():
    data_list = ['79908']

    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)

    for apartment_id in data_list:
        sql1 = 'select * from apartment_sz where id=\'%s\'' % apartment_id
        cursor = conn.cursor()
        rows = cursor.execute(sql1)
        conn.commit()
        if rows==0 : # 如果数据表中没有就去备份表中查找
            sql = 'select id, detail_url, summary, partition_url, community_name from apartment_sz_bak20200506 where id=\'%s\'' % apartment_id
            cursor.execute(sql)
            conn.commit()
            apartment = cursor.fetchone()

            sql2 = 'INSERT INTO apartment_sz (id, detail_url, summary, partition_url, community_name) VALUES (%s, %s, %s, %s, %s)'
            rows = cursor.execute(sql2, apartment)
            cursor.execute(sql)
            conn.commit()
            if rows>0:
                print('插入成功：%s' % apartment_id)

    cursor.close()
    conn.close()


def read_file():
    # filename = '/home/cyanks/Desktop/xicheng.html'
    filename = 'C:\\Users\\cyanks\\Desktop\\restore.txt'
    data_list = []
    try:
        fp = open(filename, 'r', encoding='UTF-8')
        for line in fp:
            data_list.append(line.strip('\n'))
        fp.close()
        return data_list
    except IOError:
        print ('打开文件失败！')


# 根据片区进行连接查询，获取全部成交信息
def select_apartments_by_direct(direct_name):
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)

    cursor = conn.cursor()
    sql = 'select apartment_sz.id, partitions_sz.partition_name, apartment_sz.summary, apartment_sz.community_name, apartment_sz.chengjiaoshijian, apartment_sz.chengjiaojiage,' \
          ' apartment_sz.pingjunjiage,apartment_sz.guapaijiage,apartment_sz.chengjiaozhouqi,apartment_sz.fangwuhuxing,' \
          ' apartment_sz.suozailouceng, apartment_sz.jianzhumianji, apartment_sz.huxingjiegou, apartment_sz.taoneimianji,' \
          ' apartment_sz.jianzhuleixing, apartment_sz.fangwuchaoxiang, apartment_sz.jianchengniandai, apartment_sz.zhuangxiuqingkuang,' \
          ' apartment_sz.jianzhujiegou, apartment_sz.gongnuanfangshi, apartment_sz.tihubili, apartment_sz.peibeidianti,' \
          ' apartment_sz.lianjiabianhao,apartment_sz.jiaoyiquanshu,apartment_sz.guapaishijian,apartment_sz.fangwuyongtu,' \
          ' apartment_sz.fangwunianxian,apartment_sz.fangquansuoshu from apartment_sz, partitions_sz' \
          ' where apartment_sz.partition_url=partitions_sz.partition_url and partitions_sz.direct_name=\'%s\'' % direct_name

    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

    return cursor.fetchall()


def select_trans_record_sz_by_apartment_id(apartment_id):
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)

    cursor = conn.cursor()
    sql = 'select record_price, record_time from apartment_trans_record_sz where apartment_id=\'%s\'' % apartment_id

    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

    return cursor.fetchall()


def etl():
    conn = pymysql.connect(
        host='10.10.66.102',
        port=8306,
        user='crosdev',
        password='crosdev',
        db=db_name,
        charset=db_charset)
    cursor = conn.cursor()
    condition = 'where id>%d' % 96558
    sql = 'select chengjiaoshijian, chengjiaojiage, pingjunjiage, guapaijiage, chengjiaozhouqi, fangwuhuxing, ' \
          'suozailouceng, jianzhumianji, huxingjiegou, taoneimianji, jianzhuleixing, fangwuchaoxiang, jianchengniandai, ' \
          'zhuangxiuqingkuang, jianzhujiegou, gongnuanfangshi, tihubili, peibeidianti, lianjiabianhao, jiaoyiquanshu, ' \
          'guapaishijian, fangwuyongtu, fangwunianxian, fangquansuoshu, id from apartment_sz %s' % condition
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()
    data_list = list(cursor.fetchall())
    # for apartment in data_list:
    #     print(apartment)

    conn = pymysql.connect(host=db_host, port=db_port, user=db_user,
                           password=db_password, db=db_name, charset=db_charset)
    cursor = conn.cursor()
    sql = 'update apartment_sz set chengjiaoshijian=%s, chengjiaojiage=%s, pingjunjiage=%s, guapaijiage=%s, chengjiaozhouqi=%s, fangwuhuxing=%s, ' \
          'suozailouceng=%s, jianzhumianji=%s, huxingjiegou=%s, taoneimianji=%s, jianzhuleixing=%s, fangwuchaoxiang=%s, jianchengniandai=%s, ' \
          'zhuangxiuqingkuang=%s, jianzhujiegou=%s, gongnuanfangshi=%s, tihubili=%s, peibeidianti=%s, lianjiabianhao=%s, jiaoyiquanshu=%s, ' \
          'guapaishijian=%s, fangwuyongtu=%s, fangwunianxian=%s, fangquansuoshu=%s where id=%s'
    cursor.executemany(sql, data_list)
    conn.commit()
    cursor.close()
    conn.close()

def etl_trans_records():
    conn = pymysql.connect(
        host='10.10.66.102',
        port=8306,
        user='crosdev',
        password='crosdev',
        db=db_name,
        charset=db_charset)

    cursor = conn.cursor()
    condition = 'where apartment_id>%d' % 96558
    sql = 'select apartment_id, record_price, record_detail, record_time from apartment_trans_record_sz %s' % condition

    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

    trans_records = list(cursor.fetchall())
    for record in trans_records:
        add_trans_record(record[0],record[1],record[2])