#!/usr/bin/python
# encoding=utf-8

import time

import requests
from pyquery import PyQuery as pq

from lianjia import mysql_fun

separator = "\\"
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '

                         'AppleWebKit/537.36 (KHTML, like Gecko) '

                         'Chrome/56.0.2924.87 Safari/537.36'}

base_url = 'https://bj.lianjia.com/'
districts = ['xicheng', 'chaoyang', 'haidian', 'fengtai', 'shijingshan', 'tongzhou', 'changping', 'daxing', 'yizhuangkaifaqu', 'shunyi', 'fangshan']
# districts = ['dongcheng']
offline = False


def fetch_html(url):

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
        ret = mysql_fun.filter_dup_partition_by_url(list1)

        if len(ret)>0:
            mysql_fun.insert_batch_partition(ret)
        time.sleep(20)



fetch_partition()