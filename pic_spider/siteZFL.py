import requests
import re

from pyquery import PyQuery as pq

pic_list = []
article_title = ''
label = ''


def get_pic_url_list(url):
    response = requests.get(url)

    html = response.content
    pq_doc = pq(html)

    global article_title
    if not article_title:
        article_title = pq_doc(".article-title").html()

    items = pq_doc("img").items()
    global label
    if not label:
        label = get_label_easy(url)
        print("Got the label: " + label)
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
        get_pic_url_list(next_url)

    return article_title, pic_list


def get_label(url):
    cache_array = url.split('/')
    cache_array.pop(0)
    cache_array.pop()
    year = ''
    month = ''
    for ele in cache_array:
        year_res = re.search('(?P<year>20\d{2})', ele)
        if year_res:
            year = year_res.groupdict("year").get('year')

        mon_res = re.search('(?P<mon>[0-1][0-9][0-3][0-9])', ele)
        if mon_res:
            temp = mon_res.groupdict("mon").get('mon')
            if int(temp) <= 1231:
                month = temp
    return year[2:] + month


def get_label_easy(url):
    cache_array = url.split('/')
    cache_array.pop()
    month = cache_array.pop()
    year = cache_array.pop()
    return year[2:] + month
