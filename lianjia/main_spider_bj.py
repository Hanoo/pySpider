#!/usr/bin/python
# encoding=utf-8

import time

import requests
from pyquery import PyQuery as pq

from lianjia import mysql_fun_bj

separator = "\\"
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '

                         'AppleWebKit/537.36 (KHTML, like Gecko) '

                         'Chrome/56.0.2924.87 Safari/537.36'}

base_url = 'https://bj.lianjia.com/'
districts = ['xicheng', 'chaoyang', 'haidian', 'fengtai', 'shijingshan', 'tongzhou', 'changping', 'daxing', 'yizhuangkaifaqu', 'shunyi', 'fangshan']
offline = False


def fetch_apartments():
    start = 700
    page_size = 100
    id_list = gen_apartment_url(start, page_size)
    for community_id in id_list:
        page = 1
        while page<101:
            url = base_url + 'chengjiao/pg%drs%s' % (page, community_id)
            print ('当前处理页面的url：%s' % url)
            url_mapping = fetch_apartment_detail(url)
            if len(url_mapping) > 0:
                ret = mysql_fun_bj.insert_batch_apartment(url_mapping)
                if ret<1:
                    print ('写入程序出错！正在写入的小区id：%s' % community_id)
                page += 1
                time.sleep(16)
            else:
                print('本小区处理完成。')
                time.sleep(5)
                break


# 根据url获取当前页面的房屋详情页url
def fetch_apartment_detail(url):
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
            url_mapping.append((url, summary))

    return url_mapping


def gen_apartment_url(start, page_size):
    communities = mysql_fun_bj.select_community(start, page_size)
    id_list = []
    for community in communities:
        id_list.append(community[3])
    return id_list


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
        url = base_url + 'chengjiao/' + district
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
    partition_urls = mysql_fun_bj.select_partition()
    for partition_url in partition_urls :
        partition_id = partition_url.split('/')[2]
        fetch_community_page(partition_id)


# 根据分片的url获取小区名称
def fetch_community_page(partition_id):
    communities = []
    index = 1
    while True:
        url = base_url + 'xiaoqu/' + partition_id + "/pg%d" % index
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

start = time.time()
print ('程序开始时间：%s' % time.strftime('%H:%M:%S',time.localtime(start)))
# fetch_community_page("andingmen")
# gen_apartment_url()
# test_py()
# fetch_apartment_detail('https://bj.lianjia.com/chengjiao/pg2rs上龙西里')
fetch_apartments()
end = time.time()
print ('程序结束时间：%s' % time.strftime('%H:%M:%S',time.localtime(end)))
print("The function run time is : %.03f seconds" % (end - start))