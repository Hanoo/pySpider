#!/usr/bin/python
# encoding=utf-8

import time
import random
import requests
import traceback
from pyquery import PyQuery as pq

from lianjia import mysql_fun_sz

separator = "\\"
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '

                         'AppleWebKit/537.36 (KHTML, like Gecko) '

                         'Chrome/56.0.2924.87 Safari/537.36'}

base_url = 'https://sz.lianjia.com'
districts = ['futianqu', 'nanshanqu', 'baoanqu', 'guangmingqu', 'longhuaqu'] # 福田区， 南山区， 宝安区， 光明区， 龙华区


# 在二手房成交首页爬取分片信息并存入数据库
def fetch_partition():
    for district in districts:
        list1 = []
        url = base_url + '/chengjiao/' + district
        html = requests.get(url).content
        pq_doc = pq(html)
        div_data_role = pq_doc('div[data-role]')
        partitions = div_data_role.items('a')
        for partition in partitions:
            if not partition.attr('title'):
                ele = (partition.html(), partition.attr('href'))
                list1.append(ele)
        print ('搞定%s区的片区了，有：%d条记录' % (district, len(list1)))
        ret = mysql_fun_sz.filter_dup_partition_by_url(list1)

        if len(ret)>0:
            ret = mysql_fun_sz.insert_batch_partition(ret)
            if ret<1:
                print ('插入片区失败，当前分区：%s' % district)
        time.sleep(20)


# 在分区列表页抓取交易详情的链接
def fetch_apartments():
    start_index = 47
    page_size = 7
    partition_list = mysql_fun_sz.select_partition(start_index, page_size)
    for partition in partition_list:
        page = 1
        while page<101:
            url = base_url + partition + 'pg%d' % page
            print ('当前处理页面的url：%s' % url)
            url_mapping = fetch_apartment_detail_url(url, partition)
            if len(url_mapping) > 0:
                ret = mysql_fun_sz.insert_batch_apartment(url_mapping)
                if ret<1:
                    print ('写入程序出错！正在写入的小区id：%s' % partition)
                page += 1
                time.sleep(12)
            else:
                print('分区%s处理完成。' % partition)
                time.sleep(5)
                break


# 根据url获取当前页面的房屋详情页url
def fetch_apartment_detail_url(url, partition_url):
    html = requests.get(url).content
    pq_doc = pq(html)
    url_mapping = []
    list_content = pq_doc('.listContent')
    if list_content:
        infoes = list_content.items('.info')
        for info in infoes:
            title = info('.title')
            tag_a = title('a')
            url = tag_a.attr('href')
            summary = tag_a.text()
            temp = summary.split(' ')
            community_name = temp[0]
            url_mapping.append((url, summary, partition_url, community_name))

    return url_mapping


def fetch_apartment_info():
    # 从数据库取出成交详情
    ret = mysql_fun_sz.select_apartments(100)
    pedometer = 1
    for apartment in ret:
        apartment_id = apartment[0]
        apartment_url = apartment[1]
        ret = fetch_apartment_detail(apartment_url, apartment_id)
        if ret>0:
            sleep_sec = random.randint(3, 6)
            time.sleep(sleep_sec)
            # if sleep_sec == 3:
            print ('当前执行条数：%d' % pedometer)
            pedometer += 1
        elif ret == -404 :
            print ('页面内找不到交易历史，删除对应房屋信息：%d' % apartment_id)
            mysql_fun_sz.del_apartment_by_id(apartment_id)
        else:
            print ('有异常导致插入出错！')



def fetch_apartment_detail(url, apartment_id):
    html = requests.get(url, timeout=15).content
    apartment_info_list = []
    pq_doc = pq(html)

    # 获取成交时间
    house_title = pq_doc('.house-title')
    chengjiaoshijian = house_title('span').text().split(' ')
    apartment_info_list.append(chengjiaoshijian[0])

    # 获取成交价格和均价
    div_price = pq_doc('.price')
    chengjiaojiage = div_price('.dealTotalPrice')('i').html()
    pingjunjiage = div_price('b').text()
    apartment_info_list.append(chengjiaojiage)
    apartment_info_list.append(pingjunjiage)

    # 获取挂牌价格和成交周期
    div_msg = pq_doc('.msg')
    spans = div_msg.items('span')
    msg_list = []
    for span in spans:
        msg_list.append(span('label').text())
    if len(msg_list)<1:
        return -404
    guapaijiage = msg_list[0]
    chengjiaozhouqi = msg_list[1]
    apartment_info_list.append(guapaijiage)
    apartment_info_list.append(chengjiaozhouqi)

    intro_content = pq_doc('.introContent')
    base_info_list = intro_content('.base').items('li')
    for base_info in base_info_list:
        li_info = base_info.text()[4:]
        if not li_info:
            li_info = '暂无数据'
        apartment_info_list.append(li_info)

    trans_info_list = intro_content('.transaction').items('li')
    for trans_info in trans_info_list:
        li_info = trans_info.text()[4:]
        if not li_info:
            li_info = '暂无数据'
        apartment_info_list.append(li_info)
    apartment_info_list.append(apartment_id)

    ret = mysql_fun_sz.update_apartment(tuple(apartment_info_list))

    # 获取历史成交信息
    chengjiao_records = pq_doc('.chengjiao_record').items('li')
    chengjiao_record_count = len(pq_doc('.chengjiao_record').find('li'))
    if chengjiao_record_count>0:
        for chengjiao_record in chengjiao_records:
            record_price = chengjiao_record('.record_price').text()
            record_detail = chengjiao_record('.record_detail').text()

            mysql_fun_sz.add_trans_record(apartment_id, record_price, record_detail)

    return ret




start = time.time()
print ('程序开始时间：%s' % time.strftime('%H:%M:%S',time.localtime(start)))
# fetch_apartments()
# fetch_apartment_detail('https://sz.lianjia.com/chengjiao/SZ0000851630.html', '/chengjiao/qianhai/')
# mysql_fun_sz.insert_batch_apartment(dataes)
# fetch_apartment_detail('https://sz.lianjia.com/chengjiao/105104068377.html', 43172)
i = 1
run_time = 0
while run_time < 8:
    try :
        print('第%d轮执行' % i)
        fetch_apartment_info()
    except IndexError as ie:
        traceback.print_exc()
        break
    except requests.exceptions.ConnectionError:
        print ('遇到网络错误，再试一次。')
        continue
    except requests.exceptions.ReadTimeout:
        print('网络超时，暂停一分钟')
        time.sleep(60)
    time.sleep(8)
    print('一轮爬取结束，休息8秒。')
    current = time.time()
    print ('本轮执行时间：%.01f' % (current-start))
    run_time = (current - start)/3600
    i += 1
end = time.time()
print ('程序结束时间：%s' % time.strftime('%H:%M:%S',time.localtime(end)))
print("The function running time is : %.03f seconds" % (end - start))