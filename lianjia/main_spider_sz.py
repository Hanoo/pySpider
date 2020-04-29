#!/usr/bin/python
# encoding=utf-8

import time

import requests
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
    start_index = 32
    page_size = 8
    partition_list = mysql_fun_sz.select_partition(start_index, page_size)
    for partition in partition_list:
        page = 1
        while page<101:
            url = base_url + partition + 'pg%d' % page
            print ('当前处理页面的url：%s' % url)
            url_mapping = fetch_apartment_detail(url, partition)
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
def fetch_apartment_detail(url, partition_url):
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
            url_mapping.append((url, summary, partition_url))

    return url_mapping

def fetch_apartment_info():
    mysql_fun_sz.select_apartments()


start = time.time()
print ('程序开始时间：%s' % time.strftime('%H:%M:%S',time.localtime(start)))
fetch_apartments()
# dataes = fetch_apartment_detail('https://sz.lianjia.com/chengjiao/qianhai/pg87', '/chengjiao/qianhai/')
# mysql_fun_sz.insert_batch_apartment(dataes)
end = time.time()
print ('程序结束时间：%s' % time.strftime('%H:%M:%S',time.localtime(end)))
print("The function run time is : %.03f seconds" % (end - start))