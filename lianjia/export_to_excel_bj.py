import os

import xlwt
import datetime
import time
from lianjia import mysql_fun_bj


def gen_xlwt_in_direct_and_partition(d_name_py, partition_name, apartment_id_records_mapping, directory):
    wb = xlwt.Workbook()
    # 添加一个表
    ws = wb.add_sheet('sheet1')

    # 写入列名称
    ws.write(0, 0, '详情页地址')
    ws.write(0, 1, '摘要')
    ws.write(0, 2, '社区名称')
    ws.write(0, 3, '成交时间')
    ws.write(0, 4, '单价（元）')
    ws.write(0, 5, '成交价格(万元)')
    ws.write(0, 6, '房屋户型')
    ws.write(0, 7, '建筑面积')
    ws.write(0, 8, '挂牌价格（万元）')
    ws.write(0, 9, '成交周期（天）')
    ws.write(0, 10, '所在楼层')
    ws.write(0, 11, '户型结构')
    ws.write(0, 12, '套内面积')
    ws.write(0, 13, '建筑类型')
    ws.write(0, 14, '房屋朝向')
    ws.write(0, 15, '建成年代')
    ws.write(0, 16, '装修情况')
    ws.write(0, 17, '建筑结构')
    ws.write(0, 18, '供暖方式')
    ws.write(0, 19, '梯户比例')
    ws.write(0, 20, '配备电梯')
    ws.write(0, 21, '链家编号')
    ws.write(0, 22, '交易权属')
    ws.write(0, 23, '挂牌时间')
    ws.write(0, 24, '房屋通途')
    ws.write(0, 25, '房屋年限')
    ws.write(0, 26, '房权所属')
    ws.write(0, 27, '历史成交价格')
    ws.write(0, 28, '平均价格')
    ws.write(0, 29, '成交时间')

    max_trans_time = 1

    apartment_list = mysql_fun_bj.select_apartments_in_partition(d_name_py, partition_name)

    datastyle = xlwt.XFStyle()
    datastyle.num_format_str = 'yyyy年mm月'
    row_num = 1
    for apartment in apartment_list:

        apartment_id = apartment[0]
        according_record = apartment_id_records_mapping[apartment_id]
        for column_num in range(len(apartment)):
            if column_num != 0:
                fillings = apartment[column_num]
                if column_num == 4:
                    if len(fillings) > 7:
                        datetime_p = datetime.datetime.strptime(fillings, '%Y.%m.%d')
                        chengjiaoshijian = datetime_p.strftime('%Y年%m月')
                    else:
                        datetime_p = datetime.datetime.strptime(fillings, '%Y.%m')
                        chengjiaoshijian = datetime_p.strftime('%Y年%m月')
                    ws.write(row_num, column_num - 1, chengjiaoshijian, datastyle)
                elif column_num == 5:
                    last_trans = according_record[0]  # 取最新的一次交易作为单价
                    ws.write(row_num, column_num - 1, last_trans[1])
                else:
                    ws.write(row_num, column_num-1, fillings)

        addition = len(according_record) - max_trans_time
        if addition > 0:
            for i in range(addition):
                ws.write(0, 27+(max_trans_time+i)*3, '历史成交价格')
                ws.write(0, 28+(max_trans_time+i)*3, '平均价格')
                ws.write(0, 29+(max_trans_time+i)*3, '成交时间')

            max_trans_time = len(according_record)
        for index in range(len(according_record)):
            ws.write(row_num, 27+index*3, according_record[index][0])
            ws.write(row_num, 28+index*3, according_record[index][1])
            ws.write(row_num, 29+index*3, according_record[index][2])

        row_num += 1
        # print('写入的行数：%d' % row_num)

    # 保存excel文件
    wb.save('%s\\%s.xls' % (directory, partition_name))
    print('%s 区的片区 %s 文件生成完毕，一共有记录：%d 条' % (d_name_py, partition_name, row_num))


def main_fun(d_name_py, d_name):
    base_path = 'C:\\Users\\cyanks\\Desktop\\'
    path = base_path+d_name
    is_exists = os.path.exists(path)
    if not is_exists:
        os.makedirs(path)
    trans_records = mysql_fun_bj.select_all_trans_record(d_name_py)
    apartment_id_records_mapping = {}
    for trans_record in trans_records:
        apartment_id = trans_record[0]
        record_price = trans_record[1]
        price_per_sm = trans_record[2]
        record_time = trans_record[3]
        if apartment_id in apartment_id_records_mapping:
            apartment_id_records_mapping[apartment_id].append((record_price, price_per_sm, record_time))
            print('key已经存在了，将值追加其中。')
        else:
            apartment_id_records_mapping[apartment_id] = [(record_price, price_per_sm, record_time)]

    partition_name_list = mysql_fun_bj.select_partition_name_in_direct(d_name)
    for ele in partition_name_list:
        partition_name = ele[0]
        print('当前正在处理的片区：%s' % partition_name)
        gen_xlwt_in_direct_and_partition(d_name_py, partition_name, apartment_id_records_mapping, path)


if __name__ == "__main__":
    direct_mapping = {
        '昌平': 'chp',
        '朝阳': 'chy',
        '东城': 'dch',
        '大兴': 'dx',
        '丰台': "ft",
        '海底': 'hd',
        '通州': 'tzh',
        '西城': 'xch'
    }
    for key in direct_mapping:
        direct_name = key
        direct_name_py = direct_mapping[key]
        main_fun(direct_name_py, direct_name)
