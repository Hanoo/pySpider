#!/usr/bin/python
# encoding=utf-8
import random
import time
import traceback
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
            url_mapping, total_count = fetch_apartment_detail_url(page % 3, url, direct_name, partition_name, community_name)
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
def fetch_apartment_detail_url(switch, url, direct_name, partition_name, community_name):
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


def fetch_apartment_info(reverse):
    # 从数据库取出成交详情
    ret = mysql_fun_bj.select_apartments(reverse, '昌平', 100)
    pedometer = 1
    for apartment in ret:
        apartment_id = apartment[0]
        apartment_url = apartment[1]
        ret = fetch_apartment_info_and_update(pedometer%3, apartment_url, apartment_id)
        if ret > 0:
            sleep_sec = random.randint(1, 3)
            print('--- 休整%d秒 ---' % sleep_sec)
            time.sleep(sleep_sec)
            if sleep_sec == 1:
                print('当前执行记录ID：%d' % apartment_id)
        elif ret == -1024:
            print('页面内找不到交易历史，删除对应房屋信息：%d' % apartment_id)
            mysql_fun_bj.del_apartment_by_id(apartment_id)
        else:
            print('有异常导致插入出错！出错URL:%s' % apartment_url)
        pedometer += 1


def fetch_apartment_info_and_update(switch, url, apartment_id):
    if switch==0:
        html = requests.get(url, timeout=15).content
        print('***直接连接***')
    elif switch==1:
        html = requests.get(url, proxies=proxies1, timeout=15).content
        print('***代理1***')
    else:
        html = requests.get(url, proxies=proxies2, timeout=15).content
        print('***代理2***')
    # html = requests.get(url, timeout=15).content
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
        detail_header = pq_doc('.sellDetailHeader')
        title = detail_header('.main')
        summary = title.text()
        if summary.find('已下架')>0:
            return -1024
        else:
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

    # 获取历史成交信息
    chengjiao_records = pq_doc('.chengjiao_record').items('li')
    chengjiao_record_count = len(pq_doc('.chengjiao_record').find('li'))
    if chengjiao_record_count>0:
        trans_record_list = []
        for chengjiao_record in chengjiao_records:
            record_price = chengjiao_record('.record_price').text()
            record_detail = chengjiao_record('.record_detail').text()
            details = record_detail.split(',')
            if len(details) == 2:
                record_time = details[1].replace('成交', '')
                price_per_sm = details[0].replace('单价', '').replace('元/平', '')
                if price_per_sm == '--':
                    price_per_sm = ''
            else:
                record_time = record_detail.replace('成交', '')
                price_per_sm = ''
            trans_record_list.append((apartment_id, record_price, record_detail, record_time, price_per_sm))

        return mysql_fun_bj.update_apartment(tuple(apartment_info_list), trans_record_list)
    else:
        print('当前房屋没有成交历史，可能是下架的或者没卖掉。%s' % apartment_id)
        return -404


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


def batch_fetch_and_update_apartment():
    start = time.time()
    i = 1
    run_time = 0
    while run_time < 9:
        try:
            print('第%d轮执行' % i)
            fetch_apartment_info(False)
        except IndexError:
            traceback.print_exc()
            break
        except requests.exceptions.ConnectionError:
            print('遇到网络错误，再试一次。')
            continue
        except requests.exceptions.ReadTimeout:
            print('网络超时，暂停一分钟')
            time.sleep(60)
        print('一轮爬取结束，休息8秒。')
        time.sleep(8)
        current = time.time()
        print('本轮执行时间：%.01f' % (current - start))
        run_time = (current - start) / 3600
        i += 1
    end = time.time()
    print('程序结束时间：%s' % time.strftime('%H:%M:%S', time.localtime(end)))
    print("The function running time is : %.03f seconds" % (end - start))
    print ('程序开始时间：%s' % time.strftime('%H:%M:%S',time.localtime(start)))


batch_fetch_and_update_apartment()
