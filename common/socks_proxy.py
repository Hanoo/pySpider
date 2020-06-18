#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socket
import socks
import requests
import time

headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11"}


# 返回查询的html文本
def get_html_in_socks(url):
    return get_res_in_socks(url).content


# 返回查询的返回值
def get_res_in_socks(url):
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 58080)
    socket.socket = socks.socksocket
    try:
        response = requests.get(url=url, headers=headers, timeout=15)
        return response
    except requests.exceptions.ReadTimeout:
        print('Meet timeout issue.')
        time.sleep(15)
        return get_res_in_socks(url)
