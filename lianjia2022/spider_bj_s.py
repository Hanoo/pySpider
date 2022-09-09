# -*- coding: utf-8 -*-
import os
import datetime
import math

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

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
        print('填入手机号···')

        # 等待 密码输入框 出现
        site_pwd = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'password_input')))
        site_pwd.send_keys(password)
        print('填入密码···')

        # 等待 提交按钮 出现
        site_login = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'login_panel_op')))
        site_login.click()
        print('点击登陆按钮等待跳转······')

    # 获取指定页面的源码，根据指定的目标类型，等待页面加载完成
    def get_page_html(self, url, target_type, key_words):
        self.browser.get(url)
        self.wait.until(EC.presence_of_element_located((target_type, key_words)))
        return self.browser.page_source


# 从数据库读取社区列表，从页面获取所有成交记录概要信息
def crawl_resolve_community():
    community_list = db_oper.select_community_by_condition_2022(' where direct_name=\'%s\' and finished=0 limit 0, 1'
                                                                % direct_name)
    # 遍历小区列表
    for community in community_list:
        flag = 0
        community_id = community[0]
        partition_name = community[3]
        community_name = community[5]
        print('开始处理小区: %s' % community_name)
        page = 1
        apartment_count = 0
        page_count = 101
        try:
            while page < page_count:
                url = index_url + '/chengjiao/pg%drs%s' % (page, community_name)
                url_mapping, total_count = fetch_apartment_summary(url, partition_name, community_name)
                if total_count == 0:
                    print('%s一套交易都没有' % community_name)
                    flag = 2
                    break
                elif total_count == -1:  # 跳出这个小区的爬取
                    print('剩下数据都早于时间线。')
                    page_count = 0
                apartment_count += len(url_mapping)
                # 链家列表上限为100，超过100就不再计算了
                if page_count == 101 and total_count < 30000:
                    page_count = math.floor(total_count / 30)
                if len(url_mapping) > 0:
                    print('当前处理页面的url：%s' % url)
                    ret = db_oper.insert_batch_apartment(url_mapping, table_name_suffix)
                    if ret < 1:
                        print('写入程序出错！正在写入的小区id：%s' % community_id)
                        flag = 0
                    else:
                        flag = 1
                    page += 1

            db_oper.update_community_bj_2022_for_finish(community_id, flag, apartment_count)
            print('%s处理完成。' % community_name)
            time.sleep(3)
        except TimeoutError:
            print('请求超时。')
            if page < 100:
                print('抽取中途出错，只能把已经写入的内容都删除了。')
                ret = db_oper.delete_apartment_by_community_name(table_name_suffix, community_name)
                print('删除纪录：%d' % ret)
                time.sleep(60)  # 休息一下等网络恢复
    db_oper.before_quit()

    return len(community_list)


# 单个页面元素内容抽取函数，获取成交记录的概要信息
def fetch_apartment_summary(url, partition_name, community_name):
    print('直接访问。')
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
                print('格式错误，再尝试另一种')
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


if __name__ == "__main__":
    time_line = datetime.datetime.strptime('2020.12.31', "%Y.%m.%d")
    user_names = ['13810954447', '15600280105']
    passwords = ['symbol28', 'happy999']
    time_sec = time.time()
    condition = time_sec % 2
    user_name = user_names[int(condition)]
    password = passwords[int(condition)]
    # 首页地址
    index_url = 'https://bj.lianjia.com/'
    apartment_list_url = index_url + 'chengjiao/pg1rs%E5%B0%8F%E5%8D%97%E5%BA%84%E7%A4%BE%E5%8C%BA/'
    direct_name = '海淀'
    table_name_suffix = 'hd_2022'

    db_oper = DBOperateSet(1)

    time_open = time.time()
    sbj = SpiderBJ()
    sbj.login()
    crawl_resolve_community()
    sbj.terminal()
    time_arrived = time.time()
    print('登陆耗时：%f' % (time_arrived - time_open))
