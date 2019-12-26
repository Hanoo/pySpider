#!/usr/bin/python

import argparse
import os
import sys
import site177
import time
import requests

parser = argparse.ArgumentParser(description='manual to this script')
parser.add_argument('--bu', type=str, default=None)
parser.add_argument('--folder', type=str, default=None)
parser.add_argument('--proxy', type=bool, default=True)
args = parser.parse_args()


proxies = {'http': 'socks5://localhost:58080', 'https': 'socks5://localhost:58080'}

base_url = 'http://www.177pic.info/html/2019/10/3182183.html'
base_folder = "/home/cyanks/spider/"
finished_number = 0

if args.bu:
    base_url = args.bu
    print("Use argument input as base url.")
else:
    print("No argument use as base url.")

if args.folder:
    base_folder = args.folder
    print("Use argument input as base folder.")
else:
    print("No argument use as base folder.")

separator = "\\"
sysType = sys.platform[0:3]
if sysType == "lin":
    print("Current platform is " + sysType)
    separator = "/"


def mkdir(path):
    folder = os.path.exists(path)

    if not folder:
        os.makedirs(path)
        print("---  Create new folder on path  ---")
        print(path)
    else:
        print("---  Folder exist! Nothing to do ...  ---")


def download_pic(pic_urls, saved_folder):
    d_folder = base_folder + saved_folder
    mkdir(d_folder)
    global finished_number
    for pic in pic_urls:
        cache_array = pic.split('/')
        pic_name = cache_array[len(cache_array) - 1]

        save_path = d_folder + separator + pic_name
        if os.path.exists(save_path):
            print("File: " + save_path + " exists.")
            finished_number += 1
        else:
            if args.proxy:
                r = requests.get(pic, proxies=proxies)
            else:
                r = requests.get(pic)
            finished_number += 1
            with open(save_path, "wb") as code:
                code.write(r.content)

            print("Saving image " + pic_name + " success")
            time.sleep(1)


tittle, picUrlList = site177.getPicUrlList(base_url, proxies)
pic_number = len(picUrlList)
print(str(pic_number)+" pictures will be download.")

while finished_number < pic_number:
    try:
        download_pic(picUrlList, tittle)
    except requests.ConnectionError:
        time.sleep(10)

print("Jobs done!")
