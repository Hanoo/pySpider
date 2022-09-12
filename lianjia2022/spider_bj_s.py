# -*- coding: utf-8 -*-
import os
import time
import datetime
import math
from log_util import LogUtil

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from db_func_bj import DBOperateSet
from pyquery import PyQuery as pyQ


class SpiderBJ:
    # 改成你的chromedriver的完整路径地址,驱动版本和chrome版本要一致，精确到101.0.4951.64中的4951这一位
    chromedriver_path = r"D:\Programs\Google\Chrome\Application\chromedriver.exe"

    # 对象初始化
    def __init__(self):
        self.url = index_url

        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})  # 不加载图片,加快访问速度
        # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium
        options.add_experimental_option('excludeSwitches', ['enable-automation'])

        s = Service(self.chromedriver_path)

        self.browser = webdriver.Chrome(service=s, options=options)
        self.wait = WebDriverWait(self.browser, 300)  # 超时时长设置，单位为秒

    def terminal(self):
        self.browser.close()

    def login(self):
        # 打开网页
        self.browser.get(self.url)
        self.browser.maximize_window()

        # 点击切换登陆模式为密码登陆
        login_div = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'actLoginBtn')))
        login_div.click()

        # 点击切换登陆模式为密码登陆
        login_type = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'change_login_type')))
        login_type.click()

        # 等待 手机号 出现
        site_phone_num = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'phonenum_input')))
        site_phone_num.send_keys(user_name)
        LogUtil.debug('填入手机号···')

        # 等待 密码输入框 出现
        site_pwd = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'password_input')))
        site_pwd.send_keys(password)
        LogUtil.debug('填入密码···')

        # 等待 提交按钮 出现
        site_login = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'login_panel_op')))
        site_login.click()
        LogUtil.debug('点击登陆按钮等待跳转······')

    # 获取指定页面的源码，根据指定的目标类型，等待页面加载完成
    def get_page_html(self, url, target_type, key_words):
        try:
            self.browser.get(url)
            self.wait.until(EC.presence_of_element_located((target_type, key_words)))
            self.browser.execute_script('window.scrollBy(0,1000)')
        except TimeoutException:  # 一般情况下，两次访问应该就可以了
            LogUtil.warn('出现超时问题，重新再打开一遍页面。')
            self.browser.get(url)
            self.wait.until(EC.presence_of_element_located((target_type, key_words)))
            self.browser.execute_script('window.scrollBy(0,1000)')

        return self.browser.page_source


# 从数据库读取社区列表，从页面获取所有成交记录概要信息
def crawl_resolve_community():
    community_list = db_o.select_community_by_condition_2022(' where direct_name=\'%s\' and finished=0 limit 0, 400'
                                                             % direct_name)
    # 遍历小区列表
    for community in community_list:
        flag = 1
        community_id = community[0]
        partition_name = community[3]
        community_name = community[5]
        LogUtil.info('开始处理小区: %s' % community_name)
        page = 1
        apartment_count = 0
        page_count = 101
        try:
            while page < page_count:
                url = index_url + 'chengjiao/pg%drs%s' % (page, community_name)
                url_mapping, total_count = fetch_apartment_summary(url, partition_name, community_name)
                if total_count == 0:
                    LogUtil.info('%s一套交易都没有' % community_name)
                    flag = 2
                    break

                if total_count == -1:  # 跳出这个小区的爬取
                    LogUtil.info('剩下数据都早于时间线。')
                    page_count = 0
                apartment_count += len(url_mapping)
                # 链家列表上限为100，超过100就不再计算了
                if page_count == 101 and total_count < 30000:
                    page_count = math.floor(total_count / 30)
                if len(url_mapping) > 0:
                    LogUtil.info('将获得的成交记录概要写入数据库。')
                    ret = db_o.insert_batch_apartment(url_mapping, table_name_suffix)
                    if ret < 1:
                        LogUtil.info('写入程序出错！正在写入的小区id：%s' % community_id)
                        flag = 0
                    page += 1

            db_o.update_community_bj_2022_for_finish(community_id, flag, apartment_count)
            LogUtil.info('小区：%s，状态信息已更新，%d套成交。休息几秒钟吧' % (community_name, apartment_count))
            time.sleep(3)
        except TimeoutError:
            LogUtil.info('请求超时。')
            if page < 100:
                LogUtil.info('抽取中途出错，只能把已经写入的内容都删除了。')
                ret = db_o.delete_apartment_by_community_name(table_name_suffix, community_name)
                LogUtil.info('删除纪录：%d' % ret)
                time.sleep(60)  # 休息一下等网络恢复
    db_o.before_quit()

    return len(community_list)


# 单个页面元素内容抽取函数，获取成交记录的概要信息
def fetch_apartment_summary(url, partition_name, community_name):
    html = sbj.get_page_html(url, By.CLASS_NAME, 'leftContent')

    pq_doc = pyQ(html)
    url_mapping = []
    list_content = pq_doc('.listContent')
    if list_content:
        infoes = list_content.items('.info')
        for info in infoes:
            title = info('.title')
            deal_date_str = info('.dealDate').text()
            try:
                dd = datetime.datetime.strptime(deal_date_str, "%Y.%m.%d")
            except ValueError:
                LogUtil.debug('格式错误，再尝试另一种')
                dd = datetime.datetime.strptime(deal_date_str, "%Y.%m")
            if dd > time_line:
                tag_a = title('a')
                detail_url = tag_a.attr('href')
                summary = tag_a.text()
                url_mapping.append((detail_url, summary, direct_name, partition_name, community_name))
            else:  # 默认链家的数据是按照时间倒序排列的，一旦出现一条晚于time_line的，就停止对这个小区的爬取
                return url_mapping, -1
        total_fl = pq_doc('.total')
        inner_span = int(total_fl('span').text())
        return url_mapping, inner_span
    else:
        return None, 0


# 从数据库加载交易信息，通过url打开详情页面并抽取关键信息
def fetch_apartment_info_and_update(url, apartment_id, d_name_py):
    html = sbj.get_page_html(url, By.CLASS_NAME, 'container')
    apartment_info_list = []
    pq_doc = pyQ(html)

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
    if len(msg_list) < 1:
        detail_header = pq_doc('.sellDetailHeader')
        title = detail_header('.main')
        summary = title.text()
        if summary.find('已下架') > 0:
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
    if chengjiao_record_count > 0:
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

        return db_o.update_apartment(d_name_py, tuple(apartment_info_list), trans_record_list)
    else:
        LogUtil.info('当前房屋没有成交历史，可能是下架的或者没卖掉。%s' % apartment_id)
        return -404


def fetch_apartment_info(reverse, d_name_py):
    # 从数据库取出成交详情
    ret = db_o.select_apartments(reverse, direct_name, d_name_py, 100)
    pedometer = 1
    if len(ret) == 0:
        return 0
    for apartment in ret:
        apartment_id = apartment[0]
        apartment_url = apartment[1]

        ret = fetch_apartment_info_and_update(apartment_url, apartment_id, d_name_py)
        if ret > 0:
            sleep_sec = 1.8
            LogUtil.info('ID：%d执行成功，休息%0.2f秒' % (apartment_id, sleep_sec))
            time.sleep(sleep_sec)
        elif ret == -1024:
            LogUtil.info('页面内找不到交易历史，删除对应房屋信息：%d' % apartment_id)
            db_o.del_apartment_by_id(d_name_py, apartment_id)
        elif ret == -999:
            return -500
        else:
            LogUtil.info('有异常导致插入出错！出错URL:%s' % apartment_url)
        pedometer += 1
    db_o.before_quit()
    return 1


if __name__ == "__main__":
    time_line = datetime.datetime.strptime('2020.12.31', "%Y.%m.%d")
    LogUtil.init('crawl.log', console=True)
    time_sec = time.time()

    user_name = '15600280105'
    password = 'happy999'
    # user_name = '13810954447'
    # password = 'symbol28'
    # user_name = '18510515447'
    # password = 'symbol28'
    # 首页地址
    index_url = 'https://bj.lianjia.com/'
    apartment_list_url = index_url + 'chengjiao/pg1rs%E5%B0%8F%E5%8D%97%E5%BA%84%E7%A4%BE%E5%8C%BA/'
    direct_name = '朝阳'
    table_name_suffix = 'chy_2022'
    interval = [2.5, 6, 3, 6, 5, 4, 2, 6, 3, 5.5]
    page_size = 100  # 每次查询的集合长度

    db_o = DBOperateSet(1)

    time_open = time.time()
    sbj = SpiderBJ()
    sbj.login()
    time.sleep(5)
    crawl_resolve_community()
    sbj.terminal()
    time_arrived = time.time()
    LogUtil.info('本次执行耗时：%0.2f秒' % (time_arrived - time_open))
