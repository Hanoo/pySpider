import sys

import requests
import os


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
def generate_urls(start_num, loop_count, char1, char2):
    # 检查起始数字是否合法
    if start_num not in [0, 1]:
        raise ValueError("起始数字必须是0或1")

    # 如果char1不以/结尾，则在其后面添加/
    if not char1.endswith('/'):
        char1 += '/'

    result = []
    for i in range(loop_count):
        num = (start_num + i)
        # 如果数字是个位数，补0
        num_str = f"{num:02}"
        result.append(f"{char1}{num_str}{char2}")

    return result


proxy_host = "127.0.0.1"
proxy_port = "8001"

# 设置代理
proxies = {
    'http': f'http://{proxy_host}:{proxy_port}',
    'https': f'http://{proxy_host}:{proxy_port}'
}

# 示例调用
start_num = 0
loop_count = 16
char1 = "https://content9.100bucksbabes.com/linseyworld.com/0039/"
char2 = ".jpg"
result = generate_urls(start_num, loop_count, char1, char2)
print(result)

model_name = 'Linsey Dawn'
title = 'Nude-Oil-2'
seperator = os.sep

base_folder = f'E:{seperator}Download'
res = create_folder(True)

for img_url in result:
    download_image_via_proxy(img_url, res)
