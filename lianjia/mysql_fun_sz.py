#!/usr/bin/python
# encoding=utf-8

import pymysql


# 批量插入分区
def insert_batch_partition(data_in_list) :
    conn=pymysql.connect(
        host     = '127.0.0.1',
        port     = 3306,
        user     = 'root',
        password = 'mysql',
        db       = 'lianjia',
        charset  = 'utf8mb4'
    )

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

    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='mysql',
        db='lianjia',
        charset='utf8mb4'
    )

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
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='mysql',
        db='lianjia',
        charset='utf8mb4'
    )

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
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='mysql',
        db='lianjia',
        charset='utf8mb4'
    )

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
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='mysql',
        db='lianjia',
        charset='utf8mb4'
    )
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
        conn = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='mysql',
            db='lianjia',
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        sql = 'INSERT INTO apartment_sz (detail_url, summary, partition_url, community_name) VALUES (%s, %s, %s, %s)'
        rows = cursor.executemany(sql, apartment_list)

        # 提交
        conn.commit()
        cursor.close()
        conn.close()
        return rows

def select_apartments(page_size):
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='mysql',
        db='lianjia',
        charset='utf8mb4'
    )
    if page_size>1000:
        page_size = 1000
    cursor = conn.cursor()
    sql = 'select id, detail_url from apartment_sz where chengjiaoshijian is null limit 0, %d' % page_size
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

    return cursor.fetchall()


def del_apartment_by_id(apartment_id):
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='mysql',
        db='lianjia',
        charset='utf8mb4'
    )

    cursor = conn.cursor()
    sql = 'delete from apartment_sz where id=%d' % apartment_id
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()


def update_apartment(param_data):
    # 建立数据库连接
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='mysql',
        db='lianjia',
        charset='utf8mb4'
    )

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
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='mysql',
        db='lianjia',
        charset='utf8mb4'
    )

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
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='mysql',
        db='lianjia',
        charset='utf8mb4'
    )
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

    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='mysql',
        db='lianjia',
        charset='utf8mb4'
    )

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

def select_apartments_by_direct(direct_name):
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='mysql',
        db='lianjia',
        charset='utf8mb4'
    )

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
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='mysql',
        db='lianjia',
        charset='utf8mb4'
    )

    cursor = conn.cursor()
    sql = 'select record_price, record_time from apartment_trans_record_sz where apartment_id=\'%s\'' % apartment_id

    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

    return cursor.fetchall()

# apartment_list = [('https://sz.lianjia.com/chengjiao/105104068377.html', '鹏盛村 1室1厅 38.82平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103574778.html', '鹏益花园 1室0厅 37.49平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103799369.html', '旭飞花园 1室1厅 35.68平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103909332.html', '八卦岭宿舍 1室0厅 29.34平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105104045392.html', '翠馨居花园 1室0厅 31.45平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103066384.html', '八卦岭宿舍 1室0厅 13.77平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103717407.html', '八卦岭宿舍 4室1厅 71.26平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103874567.html', '城市主场 1室1厅 44.75平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103630990.html', '旭飞花园 1室1厅 26.42平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103932380.html', '旭飞花园 1室0厅 21.04平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103977059.html', '翠馨居花园 1室0厅 32.7平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103704373.html', '旭飞花园 1室0厅 24.26平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103817584.html', '鹏益花园 2室1厅 63.59平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103879187.html', '旭飞花园 1室0厅 21.04平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103894299.html', '先科机电大厦 1室0厅 38.86平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103911249.html', '旭飞花园 1室0厅 21.04平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103632514.html', '城市主场 1室0厅 35.25平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103719547.html', '旭飞花园 1室1厅 28.61平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103430579.html', '鹏盛村 1室0厅 38.82平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103928216.html', '八卦岭宿舍 1室0厅 28.2平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103887703.html', '八卦岭宿舍 1室0厅 28.01平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103819833.html', '旭飞花园 1室0厅 22.06平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103520952.html', '鹏盛村 1室0厅 39.52平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103385899.html', '岭尚时代园 2室1厅 59平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103742021.html', '翠馨居花园 1室0厅 30.46平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103745834.html', '八卦岭宿舍 1室0厅 28.25平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103727713.html', '翠馨居花园 1室0厅 32.9平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103771230.html', '先科机电大厦 1室1厅 38.02平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105103243134.html', '城市主场 1室1厅 44.6平米', '/chengjiao/bagualing/'), ('https://sz.lianjia.com/chengjiao/105102932889.html', '鹏盛村 2室1厅 50.85平米', '/chengjiao/bagualing/')]
# insert_batch_apartment(apartment_list)

restore_data()