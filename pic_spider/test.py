import requests
import os


# 下载url中的内容并保存
def download_image_via_proxy():
    # 提取文件名
    file_name = os.path.basename(url)

    try:
        # 通过代理请求URL
        response = requests.get(url, proxies=proxies, stream=True)
        response.raise_for_status()  # 检查请求是否成功

        # 将图片内容写入文件
        with open(file_name, 'wb') as file:
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
        num = (start_num + i) % 10  # 确保数字在0-9之间循环
        # 如果数字是个位数，补0
        num_str = f"{num:02}"
        result.append(f"{char1}{num_str}{char2}")

    return result


# 示例调用
url = "https://www.popo8.com/gift/gift_314.png"  # 你要下载的图片URL
proxy_host = "192.168.0.210"
proxy_port = "8001"

# 设置代理
proxies = {
    'http': f'http://{proxy_host}:{proxy_port}',
    'https': f'http://{proxy_host}:{proxy_port}'
}

# 示例调用
start_num = 0
loop_count = 12
char1 = "https://www.popo8.com/gift/"
char2 = ".jpg"
result = generate_urls(start_num, loop_count, char1, char2)
print(result)

# download_image_via_proxy()
