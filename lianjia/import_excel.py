import xlrd
from openpyxl import load_workbook
from lianjia import mysql_fun_bj


def do_read():
    # 打开文件
    workbook = xlrd.open_workbook('D:\\lianjia\\12.xlsx')

    # 根据sheet索引或者名称获取sheet内容
    sheet1 = workbook.sheet_by_index(0)  # sheet索引从0开始

    for i in range(0, sheet1.nrows):
        line_num = sheet1.nrows-1-i
        row = sheet1.row_values(sheet1.nrows-1-i)  # 倒序读取

        table_suffix = direct_mapping.get(row[0])
        if table_suffix is None:
            print('这个区是不是不受重视？%s' % row[0])
            continue

        print('处理行：%d， 所属区县：%s' % (line_num, table_suffix))
        detail_url = row[25]
        apartment_list = mysql_fun_bj.select_apartments_by_detail_url(detail_url, table_suffix)
        if len(apartment_list) == 0:
            print('没有重复的，可以直接写入')
            direct_chinese_name = direct_py_mapping.get(row[0])
            if direct_chinese_name:
                row[0] = direct_chinese_name
                row[1] = get_partition_chinese_name(row[1])
                print(row)
                result = mysql_fun_bj.apartment_insert_full(row, table_suffix)
                if result < 0:
                    print('插入数据失败，程序退出！')
                    break
            else:
                print('这个区可能不属于需要考察的内容：%s' % row[0])
        else:
            apartment = apartment_list[0]  # 这里应该只有一条，主表是不允许detail_url重复的
            apartment_id = apartment[0]
            trans_record_list = mysql_fun_bj.select_trans_record_bj_by_apartment_id(table_suffix, apartment_id)
            not_duplicated = True
            for trans_record in trans_record_list:
                if compare_date(trans_record[3], row[3]):
                    print('时间一致，可以认为是同一条记录')
                    not_duplicated = False
                    break
            if not_duplicated:
                date_info = row[3].split('.')
                date_in_format = date_info[0] + '-' + date_info[1]
                print('即将插入数据的主表id：%d，成交时间为：%s' % (apartment_id, date_in_format))
                mysql_fun_bj.insert_trans_record(table_suffix, (apartment[0], str(row[4])+'万', row[6], date_in_format))


def get_partition_chinese_name(lianjia_pinyin):
    if len(partition_Mapping.keys()) == 0:
        partition_list = mysql_fun_bj.select_partition('')
        for partition in partition_list:
            partition_url = partition[2].replace('chengjiao', '').replace('/', '')
            partition_Mapping[partition_url] = partition[1]

    return partition_Mapping.get(lianjia_pinyin)


def compare_date(from_db, from_file):
    from_db_array = from_db.split('-')
    from_file_array = from_file.split('.')
    return from_db_array[0] == from_file_array[0] and from_db_array[1] == from_file_array[1]


def hard_insert():
    mysql_fun_bj.insert_trans_record('ft', (62961, '327万', 48089, '2020-04'))


if __name__ == '__main__':
    signer_position = 26
    partition_Mapping = {}
    direct_mapping = {
        'tongzhou': 'tzh',
        'changping': 'chp',
        'chaoyang': 'chy',
        'fengtai': "ft",
        'dongcheng': 'dch',
        'daxing': 'dx',
        'haidian': 'hd',
        'xicheng': 'xch'
    }
    direct_py_mapping = {
        'tongzhou': '通州',
        'changping': '昌平',
        'chaoyang': '朝阳',
        'fengtai': '丰台',
        'dongcheng': '东城',
        'daxing': '大兴',
        'haidian': '海淀',
        'xicheng': '西城'
    }
    do_read()
    # read_and_update()
