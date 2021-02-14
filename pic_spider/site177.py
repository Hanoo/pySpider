from pyquery import PyQuery as pq
from common import socks_proxy


def get_sub_url(base_url):
    html = socks_proxy.get_html_in_socks(base_url)
    pq_doc = pq(html)
    folder_name = pq_doc('title').html()
    page_links = pq_doc(".page-links").find('a').items()

    url_list = []
    for link in page_links:
        href = link.attr('href')
        if href not in url_list:
            url_list.append(href)

    return url_list, folder_name


def get_pic_url(page_url):

    html = socks_proxy.get_html_in_socks(page_url)

    pq_doc = pq(html)

    items = pq_doc('img').items()

    pic_list = []
    for it in items:
        src = it.attr('src')
        if src.endswith('.jpg'):
            pic_list.append(src)

    return pic_list


def get_pic_url_list(base_url):
    page_list, folder_name = get_sub_url(base_url)
    page_list.insert(0, base_url)

    pic_url_list = []
    title_array = folder_name.split("|")
    title = title_array[0].strip()

    for url in page_list:
        pc_list = get_pic_url(url)
        pic_url_list.extend(pc_list)

    return title, pic_url_list
