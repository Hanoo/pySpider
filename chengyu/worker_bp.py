#!/usr/bin/python
# encoding=utf-8
import random
import requests
import sys
import codecs

from pyquery import PyQuery as pq
from db_oper import DBOperateSet
from bs4 import BeautifulSoup


# 根据url获取当前页面的房屋详情页url
def fetch_html(url, filename, mock):
    if mock:
        html = read_file(filename)
    else:
        html = requests.get(url, headers=headers).content

    return pq(html)


def get_detail(detail_url, filename, mock):
    if mock:
        html_text = read_file(filename)
    else:
        html_text = requests.get(detail_url, headers=headers).content

    soup = BeautifulSoup(html_text, 'html.parser')
    # print(soup.prettify())
    p_tags = soup.find_all('p')
    # 打印每个<p>标签的文本内容
    for p in p_tags:
        print(p.get_text())
    # body = post_area('body')
    # print(body.html())
    # p_list = post_area.items('p')
    # i = 0
    # for item_p in p_list:
    #     print(item_p.text())
    #     i += 1
    # print(i)
    # return detail_url


def assemble(category_url):
    data_list = []
    for page_index in range(5):
        if page_index == 0:
            entrance_url = category_url
        else:
            entrance_url = category_url + '/page/' + (page_index+1)
        html_text = fetch_html(entrance_url, False)

        content_area = html_text('.col')

        list_content = content_area.items('.postlist')
        if list_content:
            for item in list_content:
                description = item('.postcontent')('p').html()
                a_list = item('.postmeat').items('a')

                for a in a_list:
                    if a.attr('title'):
                        chengyu = a.attr('title')
                        detail_url = a.attr('href')

                        detail_info = get_detail(detail_url, '', False)
                        data_list.append(
                            {
                                'chengyu': chengyu,
                                'description': description,
                                'detail_url': detail_url,
                                'detail_info': detail_info
                            }
                        )
    return data_list


def read_file(filename):
    try:
        fp = open(filename, 'r', encoding='UTF-8')
        content = fp.read()
        fp.close()
        return content
    except IOError:
        print('打开文件失败！')


if __name__ == "__main__":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

    user_agent = random.choice(read_file('agents').split('\n'))
    headers = {'User-Agent': user_agent}
    base_url = 'http://www.chengyuwan.com/category/'

    # db_oper = DBOperateSet()
    # for i in range(26):
    #     letter = chr(i + ord('a'))
    #     cat_url = base_url + letter
    #
    #     data = assemble(base_url, False)
    #     db_oper.insert_batch(data)

    file_name = 'detail_page.html'
    get_detail('', file_name, True)
    # print(html_content)
