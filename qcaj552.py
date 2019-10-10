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
base_folder = "G:\\spider_downloads\\"

def getPicUrl(url):
    response = requests.get(url)

    html = response.content
    pq_doc = pq(html)

    items = pq_doc("img").items()

    pic_list = []
    lable = getLable(url)
    print(lable)
    for it in items:
        src = it.attr('src')
        if src.endswith('.jpg'):
            res = re.search(lable, src)
            if res:
                print(src)
    return pic_list

def download_pic(pic_urls, folder_name):
    d_folder = base_folder + folder_name
    mkdir(d_folder)
    global finished_number
    for pic in pic_urls:
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
        if year_res!=None:
            year = year_res.groupdict("year").get('year')

        mon_res = re.search('(?P<mon>[0-1][0-9][0-3][0-9])', ele)
        if mon_res!=None:
            month = mon_res.groupdict("mon").get('mon')
    return year[2:]+month
getPicUrl(base_url)


