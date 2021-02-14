#!/usr/bin/python
# encoding=utf-8

import argparse
import os
import sys
import site177
import time
import requests
from common import socks_proxy
import siteZFL


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

    for pic in pic_urls:
        cache_array = pic.split('/')
        pic_name = cache_array[len(cache_array) - 1]
        save_path = d_folder + separator + pic_name
        if os.path.exists(save_path):
            print("File: " + save_path + " exists.")
        else:
            if args.proxy:
                r = socks_proxy.get_res_in_socks(pic)
            else:
                r = requests.get(pic)

            with open(save_path, "wb") as code:
                code.write(r.content)
            print("Saving image " + pic_name + " success")
            # time.sleep(1)
        pic_urls.remove(pic)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('--bu', type=str, default=None)
    parser.add_argument('--folder', type=str, default=None)
    parser.add_argument('--proxy', type=bool, default=False)
    args = parser.parse_args()

    if args.bu:
        base_url = args.bu
        print("Use argument input as base url.")
    else:
        base_url = 'https://qqkj52.com/luyilu/2015/0630/1714.html'
        print("No argument use as base url.")

    if args.folder:
        base_folder = args.folder
        print("Use argument input as base folder.")
    else:
        base_folder = 'D:\\Download\\'
        print("No argument use as base folder.")

    separator = "\\"
    sysType = sys.platform[0:3]
    if sysType == "lin":
        print("Current platform is " + sysType)
        separator = "/"

    proxies = {'http': 'socks5://localhost:58080', 'https': 'socks5://localhost:58080'}

    tittle, pic_url_list = siteZFL.get_pic_url_list(base_url)

    while pic_url_list:
        print('%d pictures will be downloaded.' % len(pic_url_list))
        try:
            download_pic(pic_url_list, tittle)
        except requests.ConnectionError:
            print('meet network issue.')
            time.sleep(10)

    print("Jobs done!")