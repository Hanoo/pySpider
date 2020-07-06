#!/usr/bin/python
# encoding=utf-8
import random
import time
import traceback
import requests
import db_func_bj
import argparse
import sys
import codecs

from pyquery import PyQuery as pq
from db_func_bj import DBOperateSet

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

user_agent = random.choice([
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
        "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
        "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
        "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    ])
headers = {'User-Agent': user_agent}
base_url = 'https://bj.lianjia.com'
districts = ['xicheng', 'chaoyang', 'haidian', 'fengtai', 'shijingshan', 'tongzhou', 'changping', 'daxing', 'yizhuangkaifaqu', 'shunyi', 'fangshan']
offline = False
http_proxy_1 = {'http': 'http://118.190.104.85:12306', 'https': 'https://118.190.104.85:12306'}
http_proxy_2 = {'http': 'http://114.215.43.57:12306', 'https': 'https://114.215.43.57:12306'}
interval = [2.5, 6, 3, 6, 5, 4, 2, 6, 3, 5.5]


# 获取小区，爬取交易基本信息和详情页地址。
# flag作为爬取状态标记，0代表失败，1代表成功，2代表小区没有成交记录，
def wrap_fetch_apartments_base_info(env, run_hour, direct_name, table_name_suffix, use_proxy):
    start = time.time()
    print('程序开始时间：%s' % time.strftime('%H:%M:%S', time.localtime(start)))
    i = 1
    run_time = 0
    while run_time < run_hour:
        try:
            print('第%d轮执行' % i)
            ret = fetch_apartments(env, direct_name, table_name_suffix, use_proxy)
            if ret==0:
                print('所有数据抽取完毕。')
                break
        except IndexError:
            traceback.print_exc()
            break
        except requests.exceptions.ConnectionError:
            print('遇到网络错误，再试一次。')
            continue
        except requests.exceptions.ReadTimeout:
            print('网络超时，暂停一分钟')
            time.sleep(60)
        print('一轮爬取结束，休息5秒。')
        time.sleep(5)
        current = time.time()
        run_time = (current - start) / 3600
        i += 1
    end = time.time()
    print('共爬取的轮数:%d' % i)
    print('程序结束时间：%s' % time.strftime('%H:%M:%S', time.localtime(end)))
    print("程序耗时 : %.03f seconds" % (end - start))

def fetch_apartments(env, direct_name, table_name_suffix, use_proxy):
    db_oper = DBOperateSet(env)
    community_list = db_oper.select_community_by_condition(' where direct_name=\'%s\' and finished is null limit 0,100' % direct_name)
    for community in community_list:
        flag = 0
        community_id = community[0]
        partition_name = community[3]
        community_name = community[5]
        print('开始处理小区: %s' % community_name)
        page = 1
        sleep_sec = 1.8
        total_count = 0
        try:
            while page<101:
                url = base_url + '/chengjiao/pg%drs%s' % (page, community_name)
                url_mapping, total_count = fetch_apartment_detail_url(page % 3, url, direct_name, partition_name, community_name, use_proxy)
                if len(url_mapping) > 0:
                    print('当前处理页面的url：%s' % url)
                    ret = db_oper.insert_batch_apartment(url_mapping, table_name_suffix)
                    if ret<1:
                        print('写入程序出错！正在写入的小区id：%s' % community_id)
                        flag = 0
                    else:
                        flag = 1
                    page += 1
                    time.sleep(sleep_sec)
                else:
                    if page==1:
                        print('%s一套交易都没有' % community_name)
                        flag = 2
                    break
            db_oper.update_community_bj_for_finish(community_id, flag, total_count)
            print('%s处理完成。' % community_name)
            time.sleep(3)
        except TimeoutError:
            print('请求超时。')
            if page<100:
                print('抽取中途出错，只能把已经写入的内容都删除了。')
                ret = db_oper.delete_apartment_by_community_name(table_name_suffix, community_name)
                print('删除纪录：%d' % ret)
                time.sleep(60)  # 休息一下等网络恢复
    db_oper.before_quit()

    return len(community_list)


# 根据url获取当前页面的房屋详情页url
def fetch_apartment_detail_url(switch, url, direct_name, partition_name, community_name, use_proxy):
    if use_proxy:
        if switch==1:
            print('直接访问。')
            html = requests.get(url, headers=headers).content
        elif switch==2:
            print('使用代理1进行访问。')
            html = requests.get(url, headers=headers, proxies=http_proxy_1).content
        else:
            print('使用代理2进行访问。')
            html = requests.get(url, headers=headers, proxies=http_proxy_2).content
    else:
        print('直接访问。')
        html = requests.get(url, headers=headers).content

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
def fetch_partition(env):
    db_oper = DBOperateSet(env)
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
        ret = db_oper.filter_dup_partition_by_url(list1)

        if len(ret)>0:
            db_oper.insert_batch_partition(ret)
        time.sleep(20)
    db_oper.before_quit()


# 从数据库读取所有分片，循环获取小区名称
def fetch_community(env):
    db_oper = DBOperateSet(env)
    partition_list = db_oper.select_partition()
    for partition in partition_list :
        partition_url = partition[2]
        partition_id = partition_url.split('/')[2]
        fetch_community_page(partition_id)
    db_oper.before_quit()


# 根据分片的url获取小区名称
def fetch_community_page(env, partition_id):
    db_oper = DBOperateSet(env)
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
        list_content = pq_doc(".listContent")
        if list_content:
            li_items = list_content.items('li')
            for li in li_items:
                community_name = li('img').attr('alt')
                print(community_name)
                communities.append((partition_id, community_name))
                print('----------------------------------------------------')
            time.sleep(20)
            index += 1
        else: # 页面没有内容
            print ('已经到了最后一页了')
            break
    db_oper.insert_community(communities)
    db_oper.before_quit()


def get_exactly_direct_name(env):
    db_oper = DBOperateSet(env)
    partition_list = db_oper.select_partition(' where direct_name is null')
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
        ret = db_oper.update_partition_bj(partition_id, direct_name)
        if ret > 0:
            print('%s片区的正确市区更新成功' % partition_name)
        time.sleep(4)
    db_oper.before_quit()


def update_community(env):
    db_oper = DBOperateSet(env)
    partition_list = db_oper.select_partition('')
    for partition in partition_list:
        partition_name = partition[1]
        partition_url = partition[2]
        print(partition_url)
        direct_name = partition[3]
        partition_name_py = partition_url.replace('/', '').replace('chengjiao', '')
        db_oper.update_community_bj(partition_name_py, direct_name, partition_url, partition_name)
    db_oper.before_quit()


def fetch_apartment_info_and_update(db_oper, switch, url, apartment_id, d_name_py):
    if not isinstance(db_oper, DBOperateSet):
        return -1

    if switch==1:
        html = requests.get(url, timeout=15).content
        print('***直接连接***')
    elif switch==0:
        html = requests.get(url, proxies=http_proxy_1, timeout=15).content
        print('***代理1***')
    else:
        html = requests.get(url, proxies=http_proxy_2, timeout=15).content
        print('***代理2***')
    # html = requests.get(url, timeout=15).content
    apartment_info_list = []
    pq_doc = pq(html)

    container = pq_doc('.container').text()
    if '人机认证' in container:
        return -999

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

        return db_oper.update_apartment(d_name_py, tuple(apartment_info_list), trans_record_list)
    else:
        print('当前房屋没有成交历史，可能是下架的或者没卖掉。%s' % apartment_id)
        return -404


def fetch_apartment_info(reverse, use_proxies, direct_name, d_name_py, env):
    db_oper = DBOperateSet(env)
    # 从数据库取出成交详情
    ret = db_oper.select_apartments(reverse, direct_name, d_name_py, 100)
    pedometer = 1
    if len(ret) == 0:
        return 0
    for apartment in ret:
        apartment_id = apartment[0]
        apartment_url = apartment[1]
        if use_proxies:
            ret = fetch_apartment_info_and_update(db_oper, pedometer%3, apartment_url, apartment_id, d_name_py)
            if ret > 0:
                sleep_sec = 1.8
                print('ID：%d执行成功，休息%0.2f秒' % (apartment_id, sleep_sec))
                time.sleep(sleep_sec)
            elif ret == -1024:
                print('页面内找不到交易历史，删除对应房屋信息：%d' % apartment_id)
                db_oper.del_apartment_by_id(d_name_py, apartment_id)
            elif ret == -999:
                return -500
            else:
                print('有异常导致插入出错！出错URL:%s' % apartment_url)
        else:
            ret = fetch_apartment_info_and_update(db_oper, 1, apartment_url, apartment_id, d_name_py)
            if ret > 0:
                sleep_sec = interval[pedometer%10]
                print('ID：%d执行成功，休息%0.2f秒' % (apartment_id, sleep_sec))
                time.sleep(sleep_sec)
            elif ret == -1024:
                print('页面内找不到交易历史，删除对应房屋信息：%d' % apartment_id)
                db_oper.del_apartment_by_id(d_name_py, apartment_id)
            elif ret == -999:
                return -500
            else:
                print('有异常导致插入出错！出错URL:%s' % apartment_url)
        pedometer += 1
    db_oper.before_quit()
    return 1


def batch_fetch_and_update_apartment(runtime, direct_name, d_name_py, reverse_execute, use_proxies, env):
    start = time.time()
    print ('程序开始时间：%s' % time.strftime('%H:%M:%S',time.localtime(start)))
    i = 1
    run_time = 0
    while run_time < runtime:
        try:
            print('第%d轮执行' % i)
            ret = fetch_apartment_info(reverse_execute, use_proxies, direct_name, d_name_py, env)
            if ret==-500:
                print('遇到人机认证，休眠10分钟后继续执行。')
                time.sleep(600)
            elif ret == 0:
                print('所有数据更新完毕，程序结束。')
                break
        except IndexError:
            traceback.print_exc()
            break
        except requests.exceptions.ConnectionError:
            print('遇到网络错误，再试一次。')
            continue
        except requests.exceptions.ReadTimeout:
            print('网络超时，暂停一分钟')
            time.sleep(60)
        print('一轮爬取结束，休息5秒。')
        time.sleep(5)
        current = time.time()
        run_time = (current - start) / 3600
        i += 1
    end = time.time()
    print('共爬取的轮数:%d' % i)
    print('程序结束时间：%s' % time.strftime('%H:%M:%S', time.localtime(end)))
    print("程序耗时 : %.03f seconds" % (end - start))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('--dn',  type=str, default='海淀')
    parser.add_argument('--sfx', type=str, default='hd')
    parser.add_argument('--eh',  type=int, default=1)
    parser.add_argument('--rve', type=bool, default=False)
    parser.add_argument('--upx', type=bool, default=False)
    parser.add_argument('--env', type=int, default=1)
    args = parser.parse_args()

    direct_name1 = args.dn
    print("--- Direct name choiced: %s ---" % direct_name1)

    suffix = args.sfx
    print("--- Table suffix: %s ---" % suffix)

    execute_hours = args.eh
    print("--- Script execution hours： %d ---" % execute_hours)

    reverse_order = args.rve
    print("--- Select data in reverse order? %s ---" % reverse_order)

    use_proxies1 = args.upx
    if use_proxies1:
        print("--- Use http proxy model. ---")
    else:
        print("--- Connect directly. ---")

    environment = args.env
    if environment==1:
        print('--- Local database. ---')
    else:
        print('--- Remote database ---')

    wrap_fetch_apartments_base_info(environment, execute_hours, direct_name1, suffix, use_proxies1)
    # batch_fetch_and_update_apartment(execute_hours, direct_name1, suffix, reverse_order, use_proxies1, environment)
    # db_func_bj.new_etl('dch')

