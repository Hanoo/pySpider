import pymysql

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
        cursor.execute('select count(id) from partitions_bj where partition_url=\'%s\';' % ele[1])
        conn.commit()
        count = cursor.fetchone()[0]
        if count==0:
            i_data_list.append(ele)


    # 关闭游标
    cursor.close()
    return i_data_list


def select_partition(condition) :
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='mysql',
        db='lianjia',
        charset='utf8mb4'
    )

    cursor = conn.cursor()
    cursor.execute('select * from partitions_bj %s' % condition)
    conn.commit()
    cursor.close()
    conn.close()

    return cursor.fetchall()


def insert_partition():
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
    sql = 'INSERT INTO partitions_bj (partition_name, partition_url) VALUES (%s,%s)'
    rows = cursor.execute(sql, ('4', 'qzcsbj4'))

    # 提交
    conn.commit()

    # 关闭游标
    cursor.close()

    # 关闭连接
    conn.close()
    print (rows)

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
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='mysql',
        db='lianjia',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    sql = 'select * from community_bj limit %d, %d' % (start, page)
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

    return cursor.fetchall()


def select_community_by_condition(condition):
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='mysql',
        db='lianjia',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    sql = 'select * from community_bj %s' % condition
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
        sql = 'INSERT INTO apartment_bj (detail_url, summary, direct_name, partition_name, community_name) VALUES (%s, %s, %s, %s, %s)'
        rows = cursor.executemany(sql, apartment_list)

        # 提交
        conn.commit()
        cursor.close()
        conn.close()
        return rows


# 更新分区表，写入分区准确的所属市区
def update_partition_bj(partition_id, direct_name):
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='mysql',
        db='lianjia',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    sql = 'update partitions_bj set direct_name=\'%s\' where id=%d' % (direct_name, partition_id)
    rows = cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

    return rows


def update_community_bj(p_name_py, direct_name, partition_url, partition_name):
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='mysql',
        db='lianjia',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    sql = 'update community_bj set direct_name=\'%s\', partition_url=\'%s\', partition_name=\'%s\' where p_name_py=\'%s\''\
          % (direct_name, partition_url, partition_name, p_name_py)
    rows = cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

    return rows


def update_community_bj_for_finish(community_id, flag, total_count):
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='mysql',
        db='lianjia',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    sql = 'update community_bj set finished=\'%d\', apartment_count=%d where id=\'%d\'' % (flag, total_count, community_id)
    rows = cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

    return rows