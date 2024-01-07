#!/usr/bin/python
# encoding=utf-8
import random
import requests
import sys
import codecs
from log_util import LogUtil

from pyquery import PyQuery as pq


# 公共函数，根据url获取当前页面的房屋详情页url
from qqc.db_oper import DBOperateSet


def fetch_html(url, filename, mock):
    if mock:
        html = read_file(filename)
    else:
        html = requests.get(url, headers=headers).content

    return pq(html)


# 打开索引页，如果有“查看全部”，则记录查看全部链接，如果没有则记录所有成语及链接
# chengyu_url_list是最终结果的集合，数据结构：韵母，成语，详细url
def process_index_page(page_url, filename, mock):
    chengyu_url_list = []
    pq_elements = fetch_html(page_url, filename, mock)
    clearfix_list = pq_elements('.boxHui1').items('.clearfix')
    for clearfix_div in clearfix_list:
        mtitle = clearfix_div('.mtitle')
        if mtitle:
            pronunciation = mtitle('.red').text()
            view_more = mtitle('.more')
            if view_more:
                more_url_suffix = view_more.attr('href')
                LogUtil.debug('找到详细页面，进入‘查看全部’页处理逻辑：%s' % more_url_suffix)
                more_url = base_url + more_url_suffix
                chengyu_url_list.extend(process_index_page(more_url, filename, mock))
            else:
                ele_ul = clearfix_div('ul')
                li_list = ele_ul.items('li')
                for li in li_list:
                    chengyu_url_list.append((pronunciation, li.text(), li('a').attr('href')))

    return chengyu_url_list


def process_detail_page(detail_url_suffix):
    page_url = base_url + detail_url_suffix
    pq_elements = fetch_html(page_url, '', False)
    listbody = pq_elements('.listbody')
    p_list = listbody.items('p')
    temp = []
    for p_ele in p_list:
        if not p_ele('.description'):
            temp.append(p_ele.text())

    # return page_content


def read_file(filename):
    try:
        fp = open(filename, 'r', encoding='UTF-8')
        content = fp.read()
        fp.close()
        return content
    except IOError:
        LogUtil.debug('打开文件失败！')


if __name__ == "__main__":
    LogUtil.init('run.log', console=True)
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

    user_agent = random.choice(read_file('../common/agents').split('\n'))
    headers = {'User-Agent': user_agent}
    base_url = 'http://www.qqc.net/'

    db_oper = DBOperateSet()
    for i in range(26):  # 还是从26的字母开始循环
        letter = chr(i + ord('A'))
        cat_url = base_url + letter

        info_list = process_index_page(cat_url, '', False)
        data_list = []
        for info in info_list:
            detail_url_suffix = info[2]
            content_html = process_detail_page(detail_url_suffix)
            data_list.append((info[1], detail_url_suffix, info[0], str(content_html)))
            LogUtil.debug(content_html)

        db_oper.insert_batch(data_list)
    db_oper.before_quit()

