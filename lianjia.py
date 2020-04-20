#!/usr/bin/python
# encoding=utf-8

import requests
from pyquery import PyQuery as pq
import time
import os
import sys
import re

reload(sys)
sys.setdefaultencoding('utf8')

separator = "\\"
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '

                         'AppleWebKit/537.36 (KHTML, like Gecko) '

                         'Chrome/56.0.2924.87 Safari/537.36'}

base_url = 'https://bj.lianjia.com/chengjiao/dongcheng'
# districts = ['dongcheng', 'xicheng', 'chaoyang']
offline = True

def fetchHtml(url):

    if offline:
        html = readFile()
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
            dealHouseTxts = dealHouseTxt.find("span").items()
            iterator = dealHouseTxts.next()
            if iterator:
                nianxianditie = iterator.html()
            iterator = iterator.next()
            if iterator:
                nianxianditie = nianxianditie + " / " + iterator.html()
        else:
            print '不存在'

        guapaijiage = ''
        chengjiaozhouqi = ''
        dealCycleTxt = item(".dealCycleTxt")
        if dealCycleTxt:
            dealCycleTxts = dealCycleTxt.find("span").items();
            iterator = dealCycleTxts.next()
            guapaijiage = iterator.html()
            iterator = iterator.next()
            chengjiaozhouqi = iterator.html()

        chengjiaoshijian = item(".dealDate").html()
        chengjiaojiage = item(".totalPrice").text()
        pingjundanjia = item(".unitPrice").text()

        # print '房屋简介：%s， 房屋朝向|装修描述: %s' % (gaikuo, chaoxiangzhuangxiu)
        print '房屋简介：%s' % fangwumingcheng
        print '户型：%s' % huxing
        print '面积：%s' % mianji
        print '房屋朝向|装修描述：%s' % chaoxiangzhuangxiu
        print '年限 / 地铁：%s' % nianxianditie
        print '挂牌价格：%s' % guapaijiage
        print '成交周期：%s' % chengjiaozhouqi
        print '成交时间：%s' % chengjiaoshijian
        print '成交价格：%s' % chengjiaojiage
        print '平均单价：%s' % pingjundanjia
        print '**********************************'


def readFile():
    filename = '/home/cyanks/Desktop/xicheng.html'

    try:
        fp = open(filename, 'r')
        content = fp.read()
        fp.close()
        return content
    except IOError:
        print '打开文件失败！'


fetchHtml(base_url)
