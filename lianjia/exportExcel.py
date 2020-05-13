import xlwt
from lianjia import mysql_fun_sz

wb = xlwt.Workbook()
# 添加一个表
ws = wb.add_sheet('test')


# 写入列名称
ws.write(0, 0, '片区名称')
ws.write(0, 1, '摘要')
ws.write(0, 2, '社区名称')
ws.write(0, 3, '成交时间')
ws.write(0, 4, '成交价格(万元)')
ws.write(0, 5, '平均价格（元）')
ws.write(0, 6, '挂牌价格（万元）')
ws.write(0, 7, '成交周期（天）')
ws.write(0, 8, '房屋户型')
ws.write(0, 9, '所在楼层')
ws.write(0, 10, '建筑面积')
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
ws.write(0, 28, '成交时间')

max_trans_time = 1

data_list = mysql_fun_sz.select_apartments('futianqu')
row_num = 1
for apartment in data_list:

    for column_num in range(len(apartment)):
        if column_num != 0:
            ws.write(row_num, column_num-1, apartment[column_num])

    apartment_id = apartment[0]
    trans_records = mysql_fun_sz.select_trans_record_sz_by_apartment_id(apartment_id)
    addition = len(trans_records) - max_trans_time
    if addition>0:
        for i in range(addition):
            ws.write(0, 27+(max_trans_time+i)*2, '历史成交价格')
            ws.write(0, 28+(max_trans_time+i)*2, '成交时间')
        max_trans_time = len(trans_records)
    for index in range(len(trans_records)):
        ws.write(row_num, 27+index*2, trans_records[index][0])
        ws.write(row_num, 28+index*2, trans_records[index][1])

    row_num += 1

# 保存excel文件
wb.save('C:\\Users\\cyanks\\Desktop\\福田区.xls')