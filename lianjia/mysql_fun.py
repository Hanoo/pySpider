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
    sql = 'INSERT INTO partitions (partition_name, partition_url) VALUES (%s,%s)'
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
        cursor.execute('select count(id) from partitions where partition_url=\'%s\';' % ele[1])
        conn.commit()
        count = cursor.fetchone()[0]
        if count==0:
            i_data_list.append(ele)


    # 关闭游标
    cursor.close()
    return i_data_list


def select_partition() :
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
    cursor.execute('select * from partitions')

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
    sql = 'INSERT INTO partitions (partition_name, partition_url) VALUES (%s,%s)'
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
    sql = 'INSERT INTO community (d_name_py, c_name) VALUES (%s,%s)'
    rows = cursor.executemany(sql, commu_list)

    # 提交
    conn.commit()

    # 关闭游标
    cursor.close()

    # 关闭连接
    conn.close()
    print(rows)

# list1 = [('安定门', '/chengjiao/andingmen/'), ('安贞', '/chengjiao/anzhen1/'), ('朝阳门内', '/chengjiao/chaoyangmennei1/')]
# insert_batch_partition(list1)
# insert_partition()
# filter_dup_partition_by_url(list1)
select_partition()