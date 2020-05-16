#!/usr/bin/python
# encoding=utf-8
import random
import time

import requests
from pyquery import PyQuery as pq

from lianjia import mysql_fun_bj

separator = "\\"
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '

                         'AppleWebKit/537.36 (KHTML, like Gecko) '

                         'Chrome/56.0.2924.87 Safari/537.36'}

base_url = 'https://bj.lianjia.com'
districts = ['xicheng', 'chaoyang', 'haidian', 'fengtai', 'shijingshan', 'tongzhou', 'changping', 'daxing', 'yizhuangkaifaqu', 'shunyi', 'fangshan']
offline = False
proxies1 = {'http': 'http://118.190.104.85:12306', 'https': 'https://118.190.104.85:12306'}
proxies2 = {'http': 'http://114.215.43.57:12306', 'https': 'https://114.215.43.57:12306'}


# flag作为爬取状态标记，0代表失败，1代表成功，2代表小区没有成交记录，
def fetch_apartments():
    community_list = mysql_fun_bj.select_community_by_condition(' where direct_name=\'昌平\' and finished is null')
    for community in community_list:
        flag = 0
        community_id = community[0]
        direct_name = community[1]
        partition_name = community[3]
        community_name = community[5]
        page = 1
        sleep_sec = random.randint(1, 3)
        total_count = 0
        while page<101:
            url = base_url + '/chengjiao/pg%drs%s' % (page, community_name)
            url_mapping, total_count = fetch_apartment_detail(page%3, url, direct_name, partition_name, community_name)
            if len(url_mapping) > 0:
                print ('当前处理页面的url：%s' % url)
                ret = mysql_fun_bj.insert_batch_apartment(url_mapping)
                if ret<1:
                    print ('写入程序出错！正在写入的小区id：%s' % community_id)
                    flag = 0
                else:
                    flag = 1
                page += 1
                time.sleep(sleep_sec)
            else:
                if page==1:
                    print('%s一套交易都没有' % community_name)
                    flag = 2
                time.sleep(sleep_sec)
                break
        mysql_fun_bj.update_community_bj_for_finish(community_id, flag, total_count)
        print('本小区处理完成。休息5秒')
        time.sleep(5)


# 根据url获取当前页面的房屋详情页url
def fetch_apartment_detail(switch, url, direct_name, partition_name, community_name):
    if switch==0:
        print('直接访问。')
        html = requests.get(url).content
    elif switch==1:
        print('使用代理1进行访问。')
        html = requests.get(url, proxies=proxies1).content
    else:
        print('使用代理2进行访问。')
        html = requests.get(url, proxies=proxies2).content

    pq_doc = pq(html)
    url_mapping = []
    list_content = pq_doc('.listContent')
    if list_content:
        infoes = list_content.items('.info')
        for info in infoes:
            title = info('.title')
            tag_a = title('a')
            detail_url = tag_a.attr('href')
            summary = tag_a.text()
            url_mapping.append((detail_url, summary, direct_name, partition_name, community_name))
    total_fl = pq_doc('.total')
    inner_span = int(total_fl('span').text())

    return url_mapping, inner_span


def fetch_apartment_from_page(url):

    if offline:
        html = read_file()
    else:
        html = requests.get(url).content
    pq_doc = pq(html)
    pq_doc.remove(".houseIcon")
    pq_doc.remove(".positionIcon")
    pq_doc.remove(".dealHouseIcon")
    pq_doc.remove(".dealCycleIcon")
    infoes = pq_doc(".info").items()

    for item in infoes:
        gaikuo = item(".title a").html().split(' ')  # 概括性描述
        fangwumingcheng = gaikuo[0]
        huxing = gaikuo[1]
        mianji = gaikuo[2]
        chaoxiangzhuangxiu = item(".houseInfo").html()  # 朝向 | 装修

        nianxianditie = ''  # 年限和地铁相关信息
        dealHouseTxt = item(".dealHouseTxt")
        if dealHouseTxt:
            dealHouseTxts = dealHouseTxt.find("span")
            nianxianditie = dealHouseTxts.html()
            iterator = dealHouseTxts.next()
            if iterator:
                nianxianditie = nianxianditie + " / " + iterator.html()
        else:
            print ('不存在')

        guapaijiage = ''
        chengjiaozhouqi = ''
        dealCycleTxt = item(".dealCycleTxt")
        if dealCycleTxt:
            dealCycleTxts = dealCycleTxt.find("span")
            guapaijiage = dealCycleTxts.html()
            chengjiaozhouqi = dealCycleTxts.next().html()

        chengjiaoshijian = item(".dealDate").html()
        chengjiaojiage = item(".totalPrice").text()
        pingjundanjia = item(".unitPrice").text()

        print ('房屋简介：%s' % fangwumingcheng)
        print ('户型：%s' % huxing)
        print ('面积：%s' % mianji)
        print ('房屋朝向|装修描述：%s' % chaoxiangzhuangxiu)
        print ('年限 / 地铁：%s' % nianxianditie)
        print ('挂牌价格：%s' % guapaijiage)
        print ('成交周期：%s' % chengjiaozhouqi)
        print ('成交时间：%s' % chengjiaoshijian)
        print ('成交价格：%s' % chengjiaojiage)
        print ('平均单价：%s' % pingjundanjia)
        print ('**********************************')


def read_file():
    # filename = '/home/cyanks/Desktop/xicheng.html'
    filename = 'D:\\lianjia.html'
    try:
        fp = open(filename, 'r', encoding='UTF-8')
        content = fp.read()
        fp.close()
        return content
    except IOError:
        print ('打开文件失败！')


# 爬取分片
def fetch_partition():
    for district in districts:
        list1 = []
        url = base_url + '/chengjiao/' + district
        if offline:
            html = read_file()
        else:
            html = requests.get(url).content
        pq_doc = pq(html)
        div_data_role = pq_doc('div[data-role]')
        partitions = div_data_role.items('a')
        for partition in partitions:
            if not partition.attr('title'):
                ele = (partition.html(), partition.attr('href'))
                list1.append(ele)
        print ('搞定%s区的片区了，有：%d条记录' % (district, len(list1)))
        ret = mysql_fun_bj.filter_dup_partition_by_url(list1)

        if len(ret)>0:
            mysql_fun_bj.insert_batch_partition(ret)
        time.sleep(20)


# 从数据库读取所有分片，循环获取小区名称
def fetch_community():
    partition_list = mysql_fun_bj.select_partition()
    for partition in partition_list :
        partition_url = partition[2]
        partition_id = partition_url.split('/')[2]
        fetch_community_page(partition_id)


# 根据分片的url获取小区名称
def fetch_community_page(partition_id):
    communities = []
    index = 1
    while True:
        url = base_url + '/xiaoqu/' + partition_id + "/pg%d" % index
        print(url)
        if offline:
            html = read_file()
        else:
            html = requests.get(url).content

        pq_doc = pq(html)
        listContent = pq_doc(".listContent")
        if listContent:
            li_items = listContent.items('li')
            for li in li_items:
                communitiy_name = li('img').attr('alt')
                print(communitiy_name)
                communities.append((partition_id, communitiy_name))
                print('----------------------------------------------------')
            time.sleep(20)
            index += 1
        else: # 页面没有内容
            print ('已经到了最后一页了')
            break
    mysql_fun_bj.insert_community(communities)


def get_exactly_direct_name():
    partition_list = mysql_fun_bj.select_partition(' where direct_name is null')
    for partition in partition_list:
        partition_id = partition[0]
        partition_name = partition[1]
        partition_url = base_url + partition[2]
        pq_doc = pq(requests.get(partition_url).content)
        position = pq_doc('.position')
        data_role = position('[data-role="ershoufang"]')
        selected = data_role('a.selected')
        direct_url = str(selected.attr('href'))
        direct_name = direct_url.replace('/', '').replace('chengjiao','')
        print('%s片区的真实区县：%s' % (partition_name, direct_name))
        ret = mysql_fun_bj.update_partition_bj(partition_id, direct_name)
        if ret > 0:
            print('%s片区的正确市区更新成功' % partition_name)
        time.sleep(4)


def update_community():
    partition_list = mysql_fun_bj.select_partition('')
    for partition in partition_list:
        partition_name = partition[1]
        partition_url = partition[2]
        print(partition_url)
        direct_name = partition[3]
        partition_name_py = partition_url.replace('/', '').replace('chengjiao', '')
        mysql_fun_bj.update_community_bj(partition_name_py, direct_name, partition_url, partition_name)


start_time = time.time()
print ('程序开始时间：%s' % time.strftime('%H:%M:%S',time.localtime(start_time)))
fetch_apartments()
# fetch_apartment_detail(0, 'https://bj.lianjia.com/chengjiao/rs%E8%BF%9C%E6%B4%8B%E6%96%B0%E5%B9%B2%E7%BA%BF/','','','')
end_time = time.time()
print('程序结束时间：%s' % time.strftime('%H:%M:%S', time.localtime(end_time)))
print("程序耗时 : %.03f seconds" % (end_time - start_time))