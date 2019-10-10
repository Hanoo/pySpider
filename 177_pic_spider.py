#!/usr/bin/python

import requests
from pyquery import PyQuery as pq
import time
import os
import sys

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '

           'AppleWebKit/537.36 (KHTML, like Gecko) '

           'Chrome/56.0.2924.87 Safari/537.36'}

proxies = {'http': 'socks5://localhost:58080', 'https': 'socks5://localhost:58080'}

base_url = 'http://www.177pic.info/html/2019/09/311581.html'
base_folder = "G:\\spider_downloads\\"

if len(sys.argv) > 1:
    base_url = sys.argv[1]
    print("Set the fst command line parameter as base url.")

if len(sys.argv) > 2:
    base_folder = sys.argv[2]
    print("Set the sec command line parameter as save base path.")

if len(sys.argv) > 3:
    print("Warning: More than 2 parameters will be discard.")

folder_name = ''

def get_sub_url(base):
    global folder_name
    response = requests.get(base, proxies=proxies)
    html = response.content
    pq_doc = pq(html)
    folder_name = pq_doc('title').html()
    page_links = pq_doc(".page-links").find('a').items()

    url_list = []
    for link in page_links:
        href = link.attr('href')
        if href not in url_list:
            url_list.append(href)

    return url_list


def getPicUrl(url):

    response = requests.get(url, proxies=proxies)

    html = response.content

    pq_doc = pq(html)

    items = pq_doc("img").items()

    pic_list = []
    for it in items:
        src = it.attr('src')
        if src.endswith('.jpg'):
            pic_list.append(src)

    return pic_list


finished_number = 0
def download_pic(pic_urls, folder_name):
    d_folder = base_folder+folder_name
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
            r = requests.get(pic, proxies=proxies)
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


start = time.clock()
page_list = get_sub_url(base_url)
page_list.insert(0, base_url)

pic_url_list = []
title_array = folder_name.split("|")
title = title_array[0].strip()

for url in page_list:
    pc_list = getPicUrl(url)
    pic_url_list.extend(pc_list)

pic_number = len(pic_url_list)
print(pic_number, " pictures will be download.")


while(finished_number<pic_number):
    try:
        download_pic(pic_url_list, title)
    except requests.ConnectionError:
        time.sleep(30)


print("Jobs done!")
elapsed = (time.clock() - start)
print("Time used:", elapsed)



