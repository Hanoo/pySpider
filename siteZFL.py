import requests
import re

from pyquery import PyQuery as pq

pic_list = []
article_title = ''
label = ''


def getPicUrl(url):
    response = requests.get(url)

    html = response.content
    pq_doc = pq(html)

    global article_title
    if not article_title:
        article_title = pq_doc(".article-title").html()

    items = pq_doc("img").items()
    global label
    if not label:
        label = getLable(url)
        print("Got the lable: " + label)
    for it in items:
        src = it.attr('src')
        if src.endswith('.jpg'):
            res = re.search(label, src)
            if res:
                pic_list.append(src)

    next_page = pq_doc(".next-page a").attr("href")
    if next_page:
        cache_array = url.split('/')
        cache_array[len(cache_array) - 1] = next_page
        next_url = "/".join(cache_array)
        getPicUrl(next_url)

    return article_title, pic_list


def getLable(url):
    cache_array = url.split('/')
    year = ''
    month = ''
    for ele in cache_array:
        year_res = re.search('(?P<year>20\d{2})', ele)
        if year_res:
            year = year_res.groupdict("year").get('year')

        mon_res = re.search('(?P<mon>[0-1][0-9][0-3][0-9])', ele)
        if mon_res:
            month = mon_res.groupdict("mon").get('mon')
    return year[2:] + month
