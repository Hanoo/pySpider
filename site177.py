import requests
from pyquery import PyQuery as pq


def get_sub_url(base_url, proxies):
    response = requests.get(base_url, proxies=proxies)
    html = response.content
    pq_doc = pq(html)
    folder_name = pq_doc('title').html()
    page_links = pq_doc(".page-links").find('a').items()

    url_list = []
    for link in page_links:
        href = link.attr('href')
        if href not in url_list:
            url_list.append(href)

    return url_list, folder_name


def getPicUrl(page_url, proxies):
    response = requests.get(page_url, proxies=proxies)

    html = response.content

    pq_doc = pq(html)

    items = pq_doc("img").items()

    pic_list = []
    for it in items:
        src = it.attr('src')
        if src.endswith('.jpg'):
            pic_list.append(src)

    return pic_list


def getPicUrlList(base_url, proxies):
    page_list, folder_name = get_sub_url(base_url, proxies)
    page_list.insert(0, base_url)

    pic_url_list = []
    title_array = folder_name.split("|")
    title = title_array[0].strip()

    for url in page_list:
        pc_list = getPicUrl(url, proxies)
        pic_url_list.extend(pc_list)

    return title, pic_url_list
