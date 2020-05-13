import random, requests, os
from selenium import webdriver
from lxml import etree


def req(url):
    # 设置多个 user-agent
    User_Agent = random.choice([
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
        "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
        "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
        "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    ])
    # 从http://www.xicidaili.com/爬取代理，并存储到http_list.txt和https_list.txt的文件中
    l = os.listdir(os.getcwd())
    if "http_list.txt" not in l:
        proxy_url = 'http://www.xicidaili.com/'
        driver = webdriver.Chrome()
        driver.get(proxy_url)
        t = driver.page_source
        driver.quit()

        html = etree.HTML(t)
        http_list = []
        https_list = []
        for i in (list(range(3, 23)) + list(range(25, 45))):
            ip = html.xpath('//*[@id="ip_list"]/tbody/tr[{}]/td[2]/text()'.format(i))[0].strip()
            port = html.xpath('//*[@id="ip_list"]/tbody/tr[{}]/td[3]/text()'.format(i))[0].strip()
            protocol = html.xpath('//*[@id="ip_list"]/tbody/tr[{}]/td[6]/text()'.format(i))[0].strip()
            if protocol == "HTTP":
                http_list.append(protocol + r"://" + ip + ":" + port)
            if protocol == "HTTPS":
                https_list.append(protocol + r"://" + ip + ":" + port)
        with open("http_list.txt", "w") as p:
            p.write(str(http_list))
        with open("https_list.txt", "w") as p:
            p.write(str(https_list))
    else:
        with open("http_list.txt") as f:
            http_list = eval(f.read())
        with open("https_list.txt") as f:
            https_list = eval(f.read())

    try:
        proxies = {"http": random.choice(http_list), "https": random.choice(https_list)}
        headers = {"User-Agent": User_Agent, "cookie": revert_cookie(cookie)}
        r = requests.get(url, proxies=proxies, headers=headers)
        print(r.status_code)
        return r
    except:
        print("更换代理中...")
        while True:
            for n in range(10):
                proxies = {"http": random.choice(list(http_list)), "https": random.choice(list(https_list))}
                headers = {"User-Agent": User_Agent, }
                r = requests.get(url, proxies=proxies, headers=headers)
                if r.status_code == 200:
                    print(r.status_code)
                    return r
                else:
                    continue
            print('无法连接服务器...')


if __name__ == '__main__':
    url = "http://www.ifeng.com"
    req(url)