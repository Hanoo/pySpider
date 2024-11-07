#!/usr/bin/python
# encoding=utf-8

import argparse
import time

import sys

import requests
import os


# 创建保存图片的文件夹
def create_folder(force):
    folder_path = f'{base_folder}{seperator}{model_name}{seperator}{title}'
    if os.path.exists(folder_path) and not force:
        print('文件系统中存在同名目录，请重新设置')
        sys.exit(-1)
    elif os.path.exists(folder_path) and force:
        os.removedirs(folder_path)
        print('移除已存在的目录')
    os.makedirs(folder_path)
    print('创建目录成功')
    return folder_path


# 下载url中的内容并保存
def download_image_via_proxy(url, folder):
    # 提取文件名
    file_name = os.path.basename(url)
    full_path = f'{folder}{seperator}{file_name}'

    try:
        # 通过代理请求URL
        response = requests.get(url, proxies=proxies, stream=True)
        response.raise_for_status()  # 检查请求是否成功

        # 将图片内容写入文件
        with open(full_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"图片已保存为 {file_name}")
    except requests.exceptions.RequestException as e:
        print(f"请求出错: {e}")


# 根据指定的起始数字、循环次数、图片地址、文件后缀生成下载路径
def generate_urls(start_num, loop_count, url):
    # 检查起始数字是否合法
    if start_num not in [0, 1]:
        raise ValueError("起始数字必须是0或1")

    # 如果char1不以/结尾，则在其后面添加/
    if not url.endswith('/'):
        url += '/'

    result = []
    suffix = '.jpg'  # 一般情况下都是jpg文件
    for i in range(loop_count):
        num = (start_num + i)
        # 如果数字是个位数，补0
        num_str = f"{num:02}"
        result.append(f"{url}{num_str}{suffix}")

    return result


if __name__ == "__main__":
    proxy_host = "192.168.0.210"
    proxy_port = "8001"

    # 设置代理
    proxies = {
        'http': f'http://{proxy_host}:{proxy_port}',
        'https': f'http://{proxy_host}:{proxy_port}'
    }
    seperator = os.sep
    char1 = "https://content9.100bucksbabes.com/linseyworld.com/0039/"

    model_name = 'Linsey Dawn'
    title = 'Nude-Oil-2'
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('--bu', type=str, default=None)
    parser.add_argument('--f', type=str, default=None)
    parser.add_argument('--mn', type=str, default=None)
    parser.add_argument('--t', type=str, default=None)
    parser.add_argument('--sn', type=int, default=None)
    parser.add_argument('--c', type=int, default=None)
    args = parser.parse_args()

    # 图片根路径
    if args.bu:
        base_url = args.bu
        print("Use argument input as base url.")
    else:
        print("没路径参数你让我下个屁啊！")
        sys.exit(-1)

    # 存储根路径
    if args.f:
        base_folder = args.f
        print("Use argument input as base folder.")
    else:
        base_folder = f'E:{seperator}Download'
        print("使用默认根路径")

    # 模特的姓名，作为路径使用
    if args.mn:
        model_name = args.mn
        print("Use argument input as model name.")
    else:
        print("没名没姓我不知道存哪！")
        sys.exit(-1)

    # 专辑的名称，作为路径使用
    if args.t:
        title = args.t
        print("Use argument input as title.")
    else:
        print("没专辑名也不行的，我不知道存哪！")
        sys.exit(-1)

    # 第一张图片的编号
    if args.sn:
        start_num = args.sn
        print("Use argument input as base folder.")
    else:
        start_num = 0
        print("没有起始编号参数就从零开始！")

    # 图片数量
    if args.c:
        loop_count = args.c
        print("Use argument input as base url.")
    else:
        print("没有图片数量，下多了没用，下少了也没用，就不浪费流量了！")
        sys.exit(-1)

    url_list = generate_urls(start_num, loop_count, base_url)
    res = create_folder(True)

    for img_url in url_list:
        download_image_via_proxy(img_url, res)

    print("Jobs done!")
