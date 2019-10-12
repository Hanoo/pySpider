#!/usr/bin/python

import requests
from pyquery import PyQuery as pq
import time
import os
import sys
import re

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '

           'AppleWebKit/537.36 (KHTML, like Gecko) '

           'Chrome/56.0.2924.87 Safari/537.36'}

base_url = 'https://qqh225.com/luyilu/2018/0813/5639.html'
base_folder = "D:\\spider_downloads\\"

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
        print("Got the lable" + label)
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
        return getPicUrl(next_url)

def download_pic():
    global finished_number
    if len(pic_list)>0:
        d_folder = base_folder + article_title
        mkdir(d_folder)
        for pic in pic_list:
            cache_array = pic.split('/')
            pic_name = cache_array[len(cache_array)-1]

            save_path = d_folder + "\\" + pic_name
            if os.path.exists(save_path):
                print("File: " + save_path + " exists.")
                finished_number += 1
            else:
                r = requests.get(pic)
                finished_number += 1
                with open(save_path, "wb") as code:
                    code.write(r.content)

                print("Saving image " + pic_name + " success")
                time.sleep(1)
    else:
        print("图片列表是空的，啥也干不了······")

def mkdir(path):
    folder = os.path.exists(path)

    if not folder:
        os.makedirs(path)
        print("---  Create new folder...  ---")
    else:
        print("---  There is this folder!  ---")

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
    return year[2:]+month
getPicUrl(base_url)
for ele in pic_list:
    print(ele)

print(article_title)

download_pic()
