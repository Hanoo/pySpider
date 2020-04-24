#!/usr/bin/python
# encoding=utf-8

import time

import requests
from pyquery import PyQuery as pq

from lianjia import mysql_fun

separator = "\\"
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '

                         'AppleWebKit/537.36 (KHTML, like Gecko) '

                         'Chrome/56.0.2924.87 Safari/537.36'}

base_url = 'https://bj.lianjia.com/'
districts = ['xicheng', 'chaoyang', 'haidian', 'fengtai', 'shijingshan', 'tongzhou', 'changping', 'daxing', 'yizhuangkaifaqu', 'shunyi', 'fangshan']
# districts = ['dongcheng']
offline = False


def fetch_html(url):

    if offline:
        html = read_file()
    else:
        html = requests.get(url).content
    pq_doc = pq(html)
    pq_doc.remove(".houseIcon")
    pq_doc.remove(".positionIcon")
    pq_doc.remove(".dealHouseIcon")
    pq_doc.remove(".dealCycleIcon")
    infoes = pq_doc(".info").items()

    for item in infoes:
        gaikuo = item(".title a").html().split(' ')  # 概括性描述
        fangwumingcheng = gaikuo[0]
        huxing = gaikuo[1]
        mianji = gaikuo[2]
        chaoxiangzhuangxiu = item(".houseInfo").html()  # 朝向 | 装修

        nianxianditie = ''  # 年限和地铁相关信息
        dealHouseTxt = item(".dealHouseTxt")
        if dealHouseTxt:
            dealHouseTxts = dealHouseTxt.find("span")
            nianxianditie = dealHouseTxts.html()
            iterator = dealHouseTxts.next()
            if iterator:
                nianxianditie = nianxianditie + " / " + iterator.html()
        else:
            print ('不存在')

        guapaijiage = ''
        chengjiaozhouqi = ''
        dealCycleTxt = item(".dealCycleTxt")
        if dealCycleTxt:
            dealCycleTxts = dealCycleTxt.find("span")
            guapaijiage = dealCycleTxts.html()
            chengjiaozhouqi = dealCycleTxts.next().html()

        chengjiaoshijian = item(".dealDate").html()
        chengjiaojiage = item(".totalPrice").text()
        pingjundanjia = item(".unitPrice").text()

        print ('房屋简介：%s' % fangwumingcheng)
        print ('户型：%s' % huxing)
        print ('面积：%s' % mianji)
        print ('房屋朝向|装修描述：%s' % chaoxiangzhuangxiu)
        print ('年限 / 地铁：%s' % nianxianditie)
        print ('挂牌价格：%s' % guapaijiage)
        print ('成交周期：%s' % chengjiaozhouqi)
        print ('成交时间：%s' % chengjiaoshijian)
        print ('成交价格：%s' % chengjiaojiage)
        print ('平均单价：%s' % pingjundanjia)
        print ('**********************************')


def read_file():
    # filename = '/home/cyanks/Desktop/xicheng.html'
    filename = 'D:\\lianjia.html'
    try:
        fp = open(filename, 'r', encoding='UTF-8')
        content = fp.read()
        fp.close()
        return content
    except IOError:
        print ('打开文件失败！')


def fetch_partition():
    for district in districts:
        list1 = []
        url = base_url + 'chengjiao/' + district
        if offline:
            html = read_file()
        else:
            html = requests.get(url).content
        pq_doc = pq(html)
        div_data_role = pq_doc('div[data-role]')
        partitions = div_data_role.items('a')
        for partition in partitions:
            if not partition.attr('title'):
                ele = (partition.html(), partition.attr('href'))
                list1.append(ele)
        print ('搞定%s区的片区了，有：%d条记录' % (district, len(list1)))
        ret = mysql_fun.filter_dup_partition_by_url(list1)

        if len(ret)>0:
            mysql_fun.insert_batch_partition(ret)
        time.sleep(20)

# 从数据库读取所有分片，循环获取小区名称
def fetch_community():
    partition_urls = mysql_fun.select_partition()
    for partition_url in partition_urls :
        partition_id = partition_url.split('/')[2]
        fetch_community_page(partition_id)


# 根据分片的url获取小区名称
def fetch_community_page(partition_id):
    communities = []
    index = 1
    while True:
        url = base_url + 'xiaoqu/' + partition_id + "/pg%d" % index
        print(url)
        if offline:
            html = read_file()
        else:
            html = requests.get(url).content

        pq_doc = pq(html)
        listContent = pq_doc(".listContent")
        if listContent:
            li_items = listContent.items('li')
            for li in li_items:
                communitiy_name = li('img').attr('alt')
                print(communitiy_name)
                communities.append((partition_id, communitiy_name))
                print('----------------------------------------------------')
            time.sleep(20)
            index += 1
        else: # 页面没有内容
            print ('已经到了最后一页了')
            break
    mysql_fun.insert_community(communities)


def test_py():
    html = '''
    <ul class="listContent" log-mod="list"><li class="clear xiaoquListItem" data-index="0" data-log_index="0" data-id="1111027378886" data-el="xiaoqu" data-housecode="1111027378886" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027378886/" target="_blank">
    <img class="lj-lazy" src="https://image1.ljcdn.com/hdic-resblock/05b210b4-6569-467c-881b-2919292c4acd.jpg.232x174.jpg" data-original="https://image1.ljcdn.com/hdic-resblock/05b210b4-6569-467c-881b-2919292c4acd.jpg.232x174.jpg" alt="青年湖北街" style="display: inline;">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027378886/" target="_blank">青年湖北街</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="青年湖北街网签" href="https://bj.lianjia.com/chengjiao/c1111027378886/">30天成交0套</a>
      <span class="cutLine">|</span><a title="青年湖北街租房">0套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /塔楼
                  /&nbsp;1997年建成
          </div>
        <div class="agentInfo">
      <span class="agentIcon"></span>
      <a href="https://dianpu.lianjia.com/1000000010088653" class="agentName">张平</a>
      <div class="agent_chat im-talk LOGCLICKDATA" data-lj_evtid="12951" data-lj_action_event="WebClick" data-lj_action_pid="lianjiaweb" data-lj_action_resblock_id="1111027378886" data-lj_action_resblock_name="青年湖北街" data-lj_action_agent_name="张平" data-lj_action_agent_id="1000000010088653" data-lj_action_source_type="pc_xiaoqu_liebiao" data_lj_action_e_plan="{&quot;u&quot;:1000000010088653,&quot;v&quot;:&quot;V1&quot;,&quot;s&quot;:&quot;NATURAL&quot;,&quot;adId&quot;:100000131,&quot;flow&quot;:&quot;natural&quot;,&quot;b&quot;:&quot;DisplayTopAgentBuilder&quot;,&quot;p&quot;:&quot;&quot;,&quot;g&quot;:&quot;&quot;,&quot;sid&quot;:&quot;1000000010088653_1111027378886&quot;,&quot;rid&quot;:&quot;5014305824297679328&quot;}" data-ucid="1000000010088653" data-msg-payload="HI，您好。我正在看青年湖北街小区" data-source-port="pc_lianjia_ershou_xiaoqu_liebiao">
        <i class="chatIcon"></i>
        <span>免费咨询</span>
      </div>
    </div>
        <div class="tagList">
                    <span>近地铁5号线和平里北街站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>105727</span>元/m<sup>2</sup></div>
            <div class="priceDesc">
        2月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="青年湖北街二手房" href="https://bj.lianjia.com/ershoufang/c1111027378886/" class="totalSellCount"><span>4</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="1" data-log_index="1" data-id="1111027377848" data-el="xiaoqu" data-housecode="1111027377848" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027377848/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="" alt="灵光西巷">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027377848/" target="_blank">灵光西巷</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="灵光西巷网签" href="https://bj.lianjia.com/chengjiao/c1111027377848/">30天成交0套</a>
      <span class="cutLine">|</span><a title="灵光西巷租房">0套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /未知类型
                  /&nbsp;未知年建成
          </div>
        <div class="agentInfo">
      <span class="agentIcon"></span>
      <a href="https://dianpu.lianjia.com/1000000020104055" class="agentName">李建伟</a>
      <div class="agent_chat im-talk LOGCLICKDATA" data-lj_evtid="12951" data-lj_action_event="WebClick" data-lj_action_pid="lianjiaweb" data-lj_action_resblock_id="1111027377848" data-lj_action_resblock_name="灵光西巷" data-lj_action_agent_name="李建伟" data-lj_action_agent_id="1000000020104055" data-lj_action_source_type="pc_xiaoqu_liebiao" data_lj_action_e_plan="{&quot;u&quot;:1000000020104055,&quot;v&quot;:&quot;V1&quot;,&quot;s&quot;:&quot;NATURAL&quot;,&quot;adId&quot;:100000131,&quot;flow&quot;:&quot;natural&quot;,&quot;b&quot;:&quot;DisplayTopAgentBuilder&quot;,&quot;p&quot;:&quot;&quot;,&quot;g&quot;:&quot;&quot;,&quot;sid&quot;:&quot;1000000020104055_1111027377848&quot;,&quot;rid&quot;:&quot;5014305824297679328&quot;}" data-ucid="1000000020104055" data-msg-payload="HI，您好。我正在看灵光西巷小区" data-source-port="pc_lianjia_ershou_xiaoqu_liebiao">
        <i class="chatIcon"></i>
        <span>免费咨询</span>
      </div>
    </div>
        <div class="tagList">
                    <span>近地铁2号线鼓楼大街站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>暂无</span></div>
            <div class="priceDesc">
        3月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="灵光西巷二手房" href="https://bj.lianjia.com/ershoufang/c1111027377848/" class="totalSellCount"><span>1</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="2" data-log_index="2" data-id="1111027380244" data-el="xiaoqu" data-housecode="1111027380244" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027380244/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="https://image1.ljcdn.com/hdic-resblock/8d054b74-e1b2-4db5-8f31-323016019c72.jpg.232x174.jpg" alt="外馆东街50号院">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027380244/" target="_blank">外馆东街50号院</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="外馆东街50号院网签" href="https://bj.lianjia.com/chengjiao/c1111027380244/">30天成交0套</a>
      <span class="cutLine">|</span><a title="外馆东街50号院租房" href="https://bj.lianjia.com/zufang/c1111027380244/">2套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/chaoyang/" class="district" title="朝阳小区">朝阳</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /塔楼/板楼
                  /&nbsp;1979年建成
          </div>
        <div class="agentInfo">
      <span class="agentIcon"></span>
      <a href="https://dianpu.lianjia.com/1000000020195267" class="agentName">刘玉辉</a>
      <div class="agent_chat im-talk LOGCLICKDATA" data-lj_evtid="12951" data-lj_action_event="WebClick" data-lj_action_pid="lianjiaweb" data-lj_action_resblock_id="1111027380244" data-lj_action_resblock_name="外馆东街50号院" data-lj_action_agent_name="刘玉辉" data-lj_action_agent_id="1000000020195267" data-lj_action_source_type="pc_xiaoqu_liebiao" data_lj_action_e_plan="{&quot;u&quot;:1000000020195267,&quot;v&quot;:&quot;V1&quot;,&quot;s&quot;:&quot;NATURAL&quot;,&quot;adId&quot;:100000131,&quot;flow&quot;:&quot;natural&quot;,&quot;b&quot;:&quot;DisplayTopAgentBuilder&quot;,&quot;p&quot;:&quot;&quot;,&quot;g&quot;:&quot;&quot;,&quot;sid&quot;:&quot;1000000020195267_1111027380244&quot;,&quot;rid&quot;:&quot;5014305824297679328&quot;}" data-ucid="1000000020195267" data-msg-payload="HI，您好。我正在看外馆东街50号院小区" data-source-port="pc_lianjia_ershou_xiaoqu_liebiao">
        <i class="chatIcon"></i>
        <span>免费咨询</span>
      </div>
    </div>
        <div class="tagList">
                    <span>近地铁8号线安华桥站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>75839</span>元/m<sup>2</sup></div>
            <div class="priceDesc">
        3月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="外馆东街50号院二手房" href="https://bj.lianjia.com/ershoufang/c1111027380244/" class="totalSellCount"><span>4</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="3" data-log_index="3" data-id="1111027377835" data-el="xiaoqu" data-housecode="1111027377835" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027377835/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="" alt="灵光胡同">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027377835/" target="_blank">灵光胡同</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="灵光胡同网签" href="https://bj.lianjia.com/chengjiao/c1111027377835/">30天成交0套</a>
      <span class="cutLine">|</span><a title="灵光胡同租房">0套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /板楼/平房
                  /&nbsp;1980年建成
          </div>
        <div class="agentInfo">
      <span class="agentIcon"></span>
      <a href="https://dianpu.lianjia.com/1000000020239963" class="agentName">陈嘉贵</a>
      <div class="agent_chat im-talk LOGCLICKDATA" data-lj_evtid="12951" data-lj_action_event="WebClick" data-lj_action_pid="lianjiaweb" data-lj_action_resblock_id="1111027377835" data-lj_action_resblock_name="灵光胡同" data-lj_action_agent_name="陈嘉贵" data-lj_action_agent_id="1000000020239963" data-lj_action_source_type="pc_xiaoqu_liebiao" data_lj_action_e_plan="{&quot;u&quot;:1000000020239963,&quot;v&quot;:&quot;V1&quot;,&quot;s&quot;:&quot;NATURAL&quot;,&quot;adId&quot;:100000131,&quot;flow&quot;:&quot;natural&quot;,&quot;b&quot;:&quot;DisplayTopAgentBuilder&quot;,&quot;p&quot;:&quot;&quot;,&quot;g&quot;:&quot;&quot;,&quot;sid&quot;:&quot;1000000020239963_1111027377835&quot;,&quot;rid&quot;:&quot;5014305824297679328&quot;}" data-ucid="1000000020239963" data-msg-payload="HI，您好。我正在看灵光胡同小区" data-source-port="pc_lianjia_ershou_xiaoqu_liebiao">
        <i class="chatIcon"></i>
        <span>免费咨询</span>
      </div>
    </div>
        <div class="tagList">
                    <span>近地铁2号线安定门站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>120776</span>元/m<sup>2</sup></div>
            <div class="priceDesc">
        3月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="灵光胡同二手房" href="https://bj.lianjia.com/ershoufang/c1111027377835/" class="totalSellCount"><span>2</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="4" data-log_index="4" data-id="1111027377923" data-el="xiaoqu" data-housecode="1111027377923" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027377923/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="https://image1.ljcdn.com/hdic-resblock/07cbd77b-a3be-4434-9da7-c9e230549b80.jpg.232x174.jpg" alt="朗家胡同24号院">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027377923/" target="_blank">朗家胡同24号院</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="朗家胡同24号院网签" href="https://bj.lianjia.com/chengjiao/c1111027377923/">30天成交1套</a>
      <span class="cutLine">|</span><a title="朗家胡同24号院租房" href="https://bj.lianjia.com/zufang/c1111027377923/">1套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /板楼
                  /&nbsp;1977年建成
          </div>
        <div class="agentInfo">
      <span class="agentIcon"></span>
      <a href="https://dianpu.lianjia.com/1000000020099093" class="agentName">于朝阳</a>
      <div class="agent_chat im-talk LOGCLICKDATA" data-lj_evtid="12951" data-lj_action_event="WebClick" data-lj_action_pid="lianjiaweb" data-lj_action_resblock_id="1111027377923" data-lj_action_resblock_name="朗家胡同24号院" data-lj_action_agent_name="于朝阳" data-lj_action_agent_id="1000000020099093" data-lj_action_source_type="pc_xiaoqu_liebiao" data_lj_action_e_plan="{&quot;u&quot;:1000000020099093,&quot;v&quot;:&quot;V1&quot;,&quot;s&quot;:&quot;NATURAL&quot;,&quot;adId&quot;:100000131,&quot;flow&quot;:&quot;natural&quot;,&quot;b&quot;:&quot;DisplayTopAgentBuilder&quot;,&quot;p&quot;:&quot;&quot;,&quot;g&quot;:&quot;&quot;,&quot;sid&quot;:&quot;1000000020099093_1111027377923&quot;,&quot;rid&quot;:&quot;5014305824297679328&quot;}" data-ucid="1000000020099093" data-msg-payload="HI，您好。我正在看朗家胡同24号院小区" data-source-port="pc_lianjia_ershou_xiaoqu_liebiao">
        <i class="chatIcon"></i>
        <span>免费咨询</span>
      </div>
    </div>
        <div class="tagList">
                    <span>近地铁2号线鼓楼大街站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>109491</span>元/m<sup>2</sup></div>
            <div class="priceDesc">
        3月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="朗家胡同24号院二手房" href="https://bj.lianjia.com/ershoufang/c1111027377923/" class="totalSellCount"><span>2</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="5" data-log_index="5" data-id="1111027376991" data-el="xiaoqu" data-housecode="1111027376991" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027376991/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="https://image1.ljcdn.com/hdic-resblock/95d5d268-a89f-4999-9118-50c0e39ea45a.jpg.232x174.jpg" alt="京宝花园">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027376991/" target="_blank">京宝花园</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="京宝花园网签" href="https://bj.lianjia.com/chengjiao/c1111027376991/">30天成交0套</a>
      <span class="cutLine">|</span><a title="京宝花园租房" href="https://bj.lianjia.com/zufang/c1111027376991/">7套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /板楼
                  /&nbsp;1994年建成
          </div>
        <div class="agentInfo">
      <span class="agentIcon"></span>
      <a href="https://dianpu.lianjia.com/1000000010140303" class="agentName">任立勇</a>
      <div class="agent_chat im-talk LOGCLICKDATA" data-lj_evtid="12951" data-lj_action_event="WebClick" data-lj_action_pid="lianjiaweb" data-lj_action_resblock_id="1111027376991" data-lj_action_resblock_name="京宝花园" data-lj_action_agent_name="任立勇" data-lj_action_agent_id="1000000010140303" data-lj_action_source_type="pc_xiaoqu_liebiao" data_lj_action_e_plan="{&quot;u&quot;:1000000010140303,&quot;v&quot;:&quot;V1&quot;,&quot;s&quot;:&quot;NATURAL&quot;,&quot;adId&quot;:100000131,&quot;flow&quot;:&quot;natural&quot;,&quot;b&quot;:&quot;DisplayTopAgentBuilder&quot;,&quot;p&quot;:&quot;&quot;,&quot;g&quot;:&quot;&quot;,&quot;sid&quot;:&quot;1000000010140303_1111027376991&quot;,&quot;rid&quot;:&quot;5014305824297679328&quot;}" data-ucid="1000000010140303" data-msg-payload="HI，您好。我正在看京宝花园小区" data-source-port="pc_lianjia_ershou_xiaoqu_liebiao">
        <i class="chatIcon"></i>
        <span>免费咨询</span>
      </div>
    </div>
        <div class="tagList">
                    <span>近地铁2号线安定门站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>67954</span>元/m<sup>2</sup></div>
            <div class="priceDesc">
        3月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="京宝花园二手房" href="https://bj.lianjia.com/ershoufang/c1111027376991/" class="totalSellCount"><span>6</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="6" data-log_index="6" data-id="1111027373935" data-el="xiaoqu" data-housecode="1111027373935" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027373935/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="" alt="东绦胡同">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027373935/" target="_blank">东绦胡同</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="东绦胡同网签" href="https://bj.lianjia.com/chengjiao/c1111027373935/">30天成交0套</a>
      <span class="cutLine">|</span><a title="东绦胡同租房" href="https://bj.lianjia.com/zufang/c1111027373935/">2套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /平房
                  /&nbsp;1975年建成
          </div>
        <div class="tagList">
                    <span>近地铁2号线鼓楼大街站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>暂无</span></div>
            <div class="priceDesc">
        2月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="东绦胡同二手房" href="https://bj.lianjia.com/ershoufang/c1111027373935/" class="totalSellCount"><span>0</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="7" data-log_index="7" data-id="1111027374339" data-el="xiaoqu" data-housecode="1111027374339" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027374339/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="https://image1.ljcdn.com/hdic-resblock/81aa1405-5ff6-45bb-8e84-7da9e3ecff2a.jpg.232x174.jpg" alt="府上嘉园">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027374339/" target="_blank">府上嘉园</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="府上嘉园网签" href="https://bj.lianjia.com/chengjiao/c1111027374339/">30天成交0套</a>
      <span class="cutLine">|</span><a title="府上嘉园租房">0套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /板楼/塔板结合
                  /&nbsp;2007年建成
          </div>
        <div class="agentInfo">
      <span class="agentIcon"></span>
      <a href="https://dianpu.lianjia.com/1000000010139674" class="agentName">杜利鹏</a>
      <div class="agent_chat im-talk LOGCLICKDATA" data-lj_evtid="12951" data-lj_action_event="WebClick" data-lj_action_pid="lianjiaweb" data-lj_action_resblock_id="1111027374339" data-lj_action_resblock_name="府上嘉园" data-lj_action_agent_name="杜利鹏" data-lj_action_agent_id="1000000010139674" data-lj_action_source_type="pc_xiaoqu_liebiao" data_lj_action_e_plan="{&quot;u&quot;:1000000010139674,&quot;v&quot;:&quot;V1&quot;,&quot;s&quot;:&quot;NATURAL&quot;,&quot;adId&quot;:100000131,&quot;flow&quot;:&quot;natural&quot;,&quot;b&quot;:&quot;DisplayTopAgentBuilder&quot;,&quot;p&quot;:&quot;&quot;,&quot;g&quot;:&quot;&quot;,&quot;sid&quot;:&quot;1000000010139674_1111027374339&quot;,&quot;rid&quot;:&quot;5014305824297679328&quot;}" data-ucid="1000000010139674" data-msg-payload="HI，您好。我正在看府上嘉园小区" data-source-port="pc_lianjia_ershou_xiaoqu_liebiao">
        <i class="chatIcon"></i>
        <span>免费咨询</span>
      </div>
    </div>
        <div class="tagList">
                    <span>近地铁8号线安德里北街站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>123005</span>元/m<sup>2</sup></div>
            <div class="priceDesc">
        3月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="府上嘉园二手房" href="https://bj.lianjia.com/ershoufang/c1111027374339/" class="totalSellCount"><span>3</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="8" data-log_index="8" data-id="1111027374695" data-el="xiaoqu" data-housecode="1111027374695" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027374695/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="" alt="工人日报社宿舍">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027374695/" target="_blank">工人日报社宿舍</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="工人日报社宿舍网签" href="https://bj.lianjia.com/chengjiao/c1111027374695/">30天成交0套</a>
      <span class="cutLine">|</span><a title="工人日报社宿舍租房">0套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /塔板结合
                  /&nbsp;1999年建成
          </div>
        <div class="tagList">
                    <span>近地铁2号线鼓楼大街站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>暂无</span></div>
            <div class="priceDesc">
        2月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="工人日报社宿舍二手房" href="https://bj.lianjia.com/ershoufang/c1111027374695/" class="totalSellCount"><span>0</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="9" data-log_index="9" data-id="1111027374703" data-el="xiaoqu" data-housecode="1111027374703" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027374703/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="" alt="国盛胡同">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027374703/" target="_blank">国盛胡同</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="国盛胡同网签" href="https://bj.lianjia.com/chengjiao/c1111027374703/">30天成交0套</a>
      <span class="cutLine">|</span><a title="国盛胡同租房">0套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /平房
                  /&nbsp;1980年建成
          </div>
        <div class="tagList">
                    <span>近地铁2号线鼓楼大街站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>暂无</span></div>
            <div class="priceDesc">
        2月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="国盛胡同二手房" href="https://bj.lianjia.com/ershoufang/c1111027374703/" class="totalSellCount"><span>0</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="10" data-log_index="10" data-id="1111027374711" data-el="xiaoqu" data-housecode="1111027374711" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027374711/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="" alt="官书院胡同">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027374711/" target="_blank">官书院胡同</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="官书院胡同网签" href="https://bj.lianjia.com/chengjiao/c1111027374711/">30天成交0套</a>
      <span class="cutLine">|</span><a title="官书院胡同租房">0套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /平房
                  /&nbsp;1960年建成
          </div>
        <div class="tagList">
                    <span>近地铁2号线雍和宫站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>暂无</span></div>
            <div class="priceDesc">
        2月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="官书院胡同二手房" href="https://bj.lianjia.com/ershoufang/c1111027374711/" class="totalSellCount"><span>0</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="11" data-log_index="11" data-id="1111027375446" data-el="xiaoqu" data-housecode="1111027375446" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027375446/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="" alt="花园东巷">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027375446/" target="_blank">花园东巷</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="花园东巷网签" href="https://bj.lianjia.com/chengjiao/c1111027375446/">30天成交0套</a>
      <span class="cutLine">|</span><a title="花园东巷租房" href="https://bj.lianjia.com/zufang/c1111027375446/">1套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /平房
                  /&nbsp;1980年建成
          </div>
        <div class="tagList">
                    <span>近地铁2号线安定门站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>暂无</span></div>
            <div class="priceDesc">
        2月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="花园东巷二手房" href="https://bj.lianjia.com/ershoufang/c1111027375446/" class="totalSellCount"><span>0</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="12" data-log_index="12" data-id="1111027375379" data-el="xiaoqu" data-housecode="1111027375379" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027375379/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="" alt="后肖家胡同">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027375379/" target="_blank">后肖家胡同</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="后肖家胡同网签" href="https://bj.lianjia.com/chengjiao/c1111027375379/">30天成交0套</a>
      <span class="cutLine">|</span><a title="后肖家胡同租房">0套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /平房
                  /&nbsp;1980年建成
          </div>
        <div class="tagList">
                    <span>近地铁2号线安定门站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>137882</span>元/m<sup>2</sup></div>
            <div class="priceDesc">
        3月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="后肖家胡同二手房" href="https://bj.lianjia.com/ershoufang/c1111027375379/" class="totalSellCount"><span>0</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="13" data-log_index="13" data-id="1111027375574" data-el="xiaoqu" data-housecode="1111027375574" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027375574/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="" alt="安德路59号">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027375574/" target="_blank">安德路59号</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="安德路59号网签" href="https://bj.lianjia.com/chengjiao/c1111027375574/">30天成交1套</a>
      <span class="cutLine">|</span><a title="安德路59号租房">0套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /板楼
                  /&nbsp;1988年建成
          </div>
        <div class="agentInfo">
      <span class="agentIcon"></span>
      <a href="https://dianpu.lianjia.com/1000000020267127" class="agentName">李京</a>
      <div class="agent_chat im-talk LOGCLICKDATA" data-lj_evtid="12951" data-lj_action_event="WebClick" data-lj_action_pid="lianjiaweb" data-lj_action_resblock_id="1111027375574" data-lj_action_resblock_name="安德路59号" data-lj_action_agent_name="李京" data-lj_action_agent_id="1000000020267127" data-lj_action_source_type="pc_xiaoqu_liebiao" data_lj_action_e_plan="{&quot;u&quot;:1000000020267127,&quot;v&quot;:&quot;V1&quot;,&quot;s&quot;:&quot;NATURAL&quot;,&quot;adId&quot;:100000131,&quot;flow&quot;:&quot;natural&quot;,&quot;b&quot;:&quot;DisplayTopAgentBuilder&quot;,&quot;p&quot;:&quot;&quot;,&quot;g&quot;:&quot;&quot;,&quot;sid&quot;:&quot;1000000020267127_1111027375574&quot;,&quot;rid&quot;:&quot;5014305824297679328&quot;}" data-ucid="1000000020267127" data-msg-payload="HI，您好。我正在看安德路59号小区" data-source-port="pc_lianjia_ershou_xiaoqu_liebiao">
        <i class="chatIcon"></i>
        <span>免费咨询</span>
      </div>
    </div>
        <div class="tagList">
                    <span>近地铁2号线鼓楼大街站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>102475</span>元/m<sup>2</sup></div>
            <div class="priceDesc">
        3月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="安德路59号二手房" href="https://bj.lianjia.com/ershoufang/c1111027375574/" class="totalSellCount"><span>2</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="14" data-log_index="14" data-id="1111027375582" data-el="xiaoqu" data-housecode="1111027375582" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027375582/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="" alt="安定门西大街">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027375582/" target="_blank">安定门西大街</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="安定门西大街网签" href="https://bj.lianjia.com/chengjiao/c1111027375582/">30天成交0套</a>
      <span class="cutLine">|</span><a title="安定门西大街租房">0套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /未知类型
                  /&nbsp;未知年建成
          </div>
        <div class="tagList">
                    <span>近地铁2号线鼓楼大街站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>暂无</span></div>
            <div class="priceDesc">
        2月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="安定门西大街二手房" href="https://bj.lianjia.com/ershoufang/c1111027375582/" class="totalSellCount"><span>0</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="15" data-log_index="15" data-id="1111027375505" data-el="xiaoqu" data-housecode="1111027375505" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027375505/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="" alt="花园前巷">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027375505/" target="_blank">花园前巷</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="花园前巷网签" href="https://bj.lianjia.com/chengjiao/c1111027375505/">30天成交0套</a>
      <span class="cutLine">|</span><a title="花园前巷租房">0套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /平房
                  /&nbsp;1980年建成
          </div>
        <div class="tagList">
                    <span>近地铁2号线安定门站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>暂无</span></div>
            <div class="priceDesc">
        2月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="花园前巷二手房" href="https://bj.lianjia.com/ershoufang/c1111027375505/" class="totalSellCount"><span>0</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="16" data-log_index="16" data-id="1111027375980" data-el="xiaoqu" data-housecode="1111027375980" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027375980/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="" alt="北锣鼓巷">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027375980/" target="_blank">北锣鼓巷</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="北锣鼓巷网签" href="https://bj.lianjia.com/chengjiao/c1111027375980/">30天成交0套</a>
      <span class="cutLine">|</span><a title="北锣鼓巷租房">0套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /平房
                  /&nbsp;1960年建成
          </div>
        <div class="tagList">
                    <span>近地铁2号线鼓楼大街站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>129615</span>元/m<sup>2</sup></div>
            <div class="priceDesc">
        3月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="北锣鼓巷二手房" href="https://bj.lianjia.com/ershoufang/c1111027375980/" class="totalSellCount"><span>0</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="17" data-log_index="17" data-id="1111027374895" data-el="xiaoqu" data-housecode="1111027374895" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027374895/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="https://image1.ljcdn.com/hdic-resblock/0b523ce2-1013-47ad-bb34-09cf73b87539.jpg.232x174.jpg" alt="皇城国际中心">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027374895/" target="_blank">皇城国际中心</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="皇城国际中心网签" href="https://bj.lianjia.com/chengjiao/c1111027374895/">30天成交0套</a>
      <span class="cutLine">|</span><a title="皇城国际中心租房">0套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /塔板结合
                  /&nbsp;2006年建成
          </div>
        <div class="tagList">
                    <span>近地铁2号线安定门站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>暂无</span></div>
            <div class="priceDesc">
        2月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="皇城国际中心二手房" href="https://bj.lianjia.com/ershoufang/c1111027374895/" class="totalSellCount"><span>0</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="18" data-log_index="18" data-id="1111027374743" data-el="xiaoqu" data-housecode="1111027374743" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027374743/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="" alt="国学胡同">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027374743/" target="_blank">国学胡同</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="国学胡同网签" href="https://bj.lianjia.com/chengjiao/c1111027374743/">30天成交0套</a>
      <span class="cutLine">|</span><a title="国学胡同租房">0套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /平房
                  /&nbsp;未知年建成
          </div>
        <div class="tagList">
                    <span>近地铁2号线雍和宫站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>暂无</span></div>
            <div class="priceDesc">
        2月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="国学胡同二手房" href="https://bj.lianjia.com/ershoufang/c1111027374743/" class="totalSellCount"><span>0</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="19" data-log_index="19" data-id="1111027374744" data-el="xiaoqu" data-housecode="1111027374744" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027374744/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="" alt="国祥胡同">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027374744/" target="_blank">国祥胡同</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="国祥胡同网签" href="https://bj.lianjia.com/chengjiao/c1111027374744/">30天成交0套</a>
      <span class="cutLine">|</span><a title="国祥胡同租房">0套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /板楼/平房
                  /&nbsp;1958年建成
          </div>
        <div class="tagList">
                    <span>近地铁2号线鼓楼大街站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>98167</span>元/m<sup>2</sup></div>
            <div class="priceDesc">
        3月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="国祥胡同二手房" href="https://bj.lianjia.com/ershoufang/c1111027374744/" class="totalSellCount"><span>0</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="20" data-log_index="20" data-id="1111027374852" data-el="xiaoqu" data-housecode="1111027374852" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027374852/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="" alt="国子监街">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027374852/" target="_blank">国子监街</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="国子监街网签" href="https://bj.lianjia.com/chengjiao/c1111027374852/">30天成交0套</a>
      <span class="cutLine">|</span><a title="国子监街租房">0套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /平房
                  /&nbsp;1980年建成
          </div>
        <div class="agentInfo">
      <span class="agentIcon"></span>
      <a href="https://dianpu.lianjia.com/1000000020000535" class="agentName">庞岩</a>
      <div class="agent_chat im-talk LOGCLICKDATA" data-lj_evtid="12951" data-lj_action_event="WebClick" data-lj_action_pid="lianjiaweb" data-lj_action_resblock_id="1111027374852" data-lj_action_resblock_name="国子监街" data-lj_action_agent_name="庞岩" data-lj_action_agent_id="1000000020000535" data-lj_action_source_type="pc_xiaoqu_liebiao" data_lj_action_e_plan="{&quot;u&quot;:1000000020000535,&quot;v&quot;:&quot;V1&quot;,&quot;s&quot;:&quot;NATURAL&quot;,&quot;adId&quot;:100000131,&quot;flow&quot;:&quot;natural&quot;,&quot;b&quot;:&quot;DisplayTopAgentBuilder&quot;,&quot;p&quot;:&quot;&quot;,&quot;g&quot;:&quot;&quot;,&quot;sid&quot;:&quot;1000000020000535_1111027374852&quot;,&quot;rid&quot;:&quot;5014305824297679328&quot;}" data-ucid="1000000020000535" data-msg-payload="HI，您好。我正在看国子监街小区" data-source-port="pc_lianjia_ershou_xiaoqu_liebiao">
        <i class="chatIcon"></i>
        <span>免费咨询</span>
      </div>
    </div>
        <div class="tagList">
                    <span>近地铁2号线安定门站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>144400</span>元/m<sup>2</sup></div>
            <div class="priceDesc">
        3月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="国子监街二手房" href="https://bj.lianjia.com/ershoufang/c1111027374852/" class="totalSellCount"><span>0</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="21" data-log_index="21" data-id="1111027375209" data-el="xiaoqu" data-housecode="1111027375209" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027375209/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="https://image1.ljcdn.com/hdic-resblock/542dac1c-c697-4b3e-bda0-58d1013e5eb3.jpg.232x174.jpg" alt="和平里中街">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027375209/" target="_blank">和平里中街</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="和平里中街网签" href="https://bj.lianjia.com/chengjiao/c1111027375209/">30天成交0套</a>
      <span class="cutLine">|</span><a title="和平里中街租房">0套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /板楼
                  /&nbsp;1976年建成
          </div>
        <div class="tagList">
                    <span>近地铁5号线和平里北街站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>102570</span>元/m<sup>2</sup></div>
            <div class="priceDesc">
        3月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="和平里中街二手房" href="https://bj.lianjia.com/ershoufang/c1111027375209/" class="totalSellCount"><span>0</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="22" data-log_index="22" data-id="1111027375725" data-el="xiaoqu" data-housecode="1111027375725" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027375725/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="https://image1.ljcdn.com/hdic-resblock/d43b84fb-b3b5-411b-bb7c-fcadf21c8823.jpg.232x174.jpg" alt="宝钞胡同">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027375725/" target="_blank">宝钞胡同</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="宝钞胡同网签" href="https://bj.lianjia.com/chengjiao/c1111027375725/">30天成交0套</a>
      <span class="cutLine">|</span><a title="宝钞胡同租房" href="https://bj.lianjia.com/zufang/c1111027375725/">1套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /板楼/平房
                  /&nbsp;1950年建成
          </div>
        <div class="agentInfo">
      <span class="agentIcon"></span>
      <a href="https://dianpu.lianjia.com/1000000023005478" class="agentName">温鑫喆</a>
      <div class="agent_chat im-talk LOGCLICKDATA" data-lj_evtid="12951" data-lj_action_event="WebClick" data-lj_action_pid="lianjiaweb" data-lj_action_resblock_id="1111027375725" data-lj_action_resblock_name="宝钞胡同" data-lj_action_agent_name="温鑫喆" data-lj_action_agent_id="1000000023005478" data-lj_action_source_type="pc_xiaoqu_liebiao" data_lj_action_e_plan="{&quot;u&quot;:1000000023005478,&quot;v&quot;:&quot;V1&quot;,&quot;s&quot;:&quot;NATURAL&quot;,&quot;adId&quot;:100000131,&quot;flow&quot;:&quot;natural&quot;,&quot;b&quot;:&quot;DisplayTopAgentBuilder&quot;,&quot;p&quot;:&quot;&quot;,&quot;g&quot;:&quot;&quot;,&quot;sid&quot;:&quot;1000000023005478_1111027375725&quot;,&quot;rid&quot;:&quot;5014305824297679328&quot;}" data-ucid="1000000023005478" data-msg-payload="HI，您好。我正在看宝钞胡同小区" data-source-port="pc_lianjia_ershou_xiaoqu_liebiao">
        <i class="chatIcon"></i>
        <span>免费咨询</span>
      </div>
    </div>
        <div class="tagList">
                    <span>近地铁2号线鼓楼大街站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>110015</span>元/m<sup>2</sup></div>
            <div class="priceDesc">
        3月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="宝钞胡同二手房" href="https://bj.lianjia.com/ershoufang/c1111027375725/" class="totalSellCount"><span>1</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="23" data-log_index="23" data-id="1111027375670" data-el="xiaoqu" data-housecode="1111027375670" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027375670/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="https://image1.ljcdn.com/hdic-resblock/8452c5a0-c4ab-4616-86d7-05623d5fb993.jpg.232x174.jpg" alt="安馨园">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027375670/" target="_blank">安馨园</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="安馨园网签" href="https://bj.lianjia.com/chengjiao/c1111027375670/">30天成交0套</a>
      <span class="cutLine">|</span><a title="安馨园租房">0套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /板楼
                  /&nbsp;2003年建成
          </div>
        <div class="tagList">
                    <span>近地铁2号线安定门站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>112968</span>元/m<sup>2</sup></div>
            <div class="priceDesc">
        3月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="安馨园二手房" href="https://bj.lianjia.com/ershoufang/c1111027375670/" class="totalSellCount"><span>0</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="24" data-log_index="24" data-id="1111027375661" data-el="xiaoqu" data-housecode="1111027375661" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027375661/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="" alt="安外大街82号院">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027375661/" target="_blank">安外大街82号院</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="安外大街82号院网签" href="https://bj.lianjia.com/chengjiao/c1111027375661/">30天成交0套</a>
      <span class="cutLine">|</span><a title="安外大街82号院租房">0套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /板楼
                  /&nbsp;1985年建成
          </div>
        <div class="tagList">
                    <span>近地铁8号线安德里北街站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>暂无</span></div>
            <div class="priceDesc">
        2月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="安外大街82号院二手房" href="https://bj.lianjia.com/ershoufang/c1111027375661/" class="totalSellCount"><span>0</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="25" data-log_index="25" data-id="1111027375879" data-el="xiaoqu" data-housecode="1111027375879" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027375879/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="" alt="宝景大厦">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027375879/" target="_blank">宝景大厦</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="宝景大厦网签" href="https://bj.lianjia.com/chengjiao/c1111027375879/">30天成交0套</a>
      <span class="cutLine">|</span><a title="宝景大厦租房">0套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /塔楼
                  /&nbsp;2000年建成
          </div>
        <div class="tagList">
                    <span>近地铁2号线安定门站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>暂无</span></div>
            <div class="priceDesc">
        2月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="宝景大厦二手房" href="https://bj.lianjia.com/ershoufang/c1111027375879/" class="totalSellCount"><span>0</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="26" data-log_index="26" data-id="1111027374953" data-el="xiaoqu" data-housecode="1111027374953" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027374953/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="https://image1.ljcdn.com/hdic-resblock/8e3d0d6a-57c2-4d89-8699-11c001f40361.jpg.232x174.jpg" alt="华府景园">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027374953/" target="_blank">华府景园</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="华府景园网签" href="https://bj.lianjia.com/chengjiao/c1111027374953/">30天成交1套</a>
      <span class="cutLine">|</span><a title="华府景园租房" href="https://bj.lianjia.com/zufang/c1111027374953/">2套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /塔楼/塔板结合
                  /&nbsp;2001年建成
          </div>
        <div class="agentInfo">
      <span class="agentIcon"></span>
      <a href="https://dianpu.lianjia.com/1000000020128908" class="agentName">侯魏华</a>
      <div class="agent_chat im-talk LOGCLICKDATA" data-lj_evtid="12951" data-lj_action_event="WebClick" data-lj_action_pid="lianjiaweb" data-lj_action_resblock_id="1111027374953" data-lj_action_resblock_name="华府景园" data-lj_action_agent_name="侯魏华" data-lj_action_agent_id="1000000020128908" data-lj_action_source_type="pc_xiaoqu_liebiao" data_lj_action_e_plan="{&quot;u&quot;:1000000020128908,&quot;v&quot;:&quot;V1&quot;,&quot;s&quot;:&quot;NATURAL&quot;,&quot;adId&quot;:100000131,&quot;flow&quot;:&quot;natural&quot;,&quot;b&quot;:&quot;DisplayTopAgentBuilder&quot;,&quot;p&quot;:&quot;&quot;,&quot;g&quot;:&quot;&quot;,&quot;sid&quot;:&quot;1000000020128908_1111027374953&quot;,&quot;rid&quot;:&quot;5014305824297679328&quot;}" data-ucid="1000000020128908" data-msg-payload="HI，您好。我正在看华府景园小区" data-source-port="pc_lianjia_ershou_xiaoqu_liebiao">
        <i class="chatIcon"></i>
        <span>免费咨询</span>
      </div>
    </div>
        <div class="tagList">
                </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>84373</span>元/m<sup>2</sup></div>
            <div class="priceDesc">
        3月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="华府景园二手房" href="https://bj.lianjia.com/ershoufang/c1111027374953/" class="totalSellCount"><span>2</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
<li class="clear xiaoquListItem" data-index="27" data-log_index="27" data-id="1111027382662" data-el="xiaoqu" data-housecode="1111027382662" data-is_focus="" data-sl="">
  <a class="img" href="https://bj.lianjia.com/xiaoqu/1111027382662/" target="_blank">
    <img class="lj-lazy" src="https://s1.ljcdn.com/feroot/pc/asset/img/blank.gif?_v=202004211506586" data-original="https://image1.ljcdn.com/hdic-resblock/0fbbb7a1-6756-4ded-be01-2b6fd3a226ad.jpg.232x174.jpg" alt="中绦胡同甲2号院">
  </a>
  <div class="info">
    <div class="title">
      <a href="https://bj.lianjia.com/xiaoqu/1111027382662/" target="_blank">中绦胡同甲2号院</a>
          </div>
    <div class="houseInfo">
      <span class="houseIcon"></span>
            <a title="中绦胡同甲2号院网签" href="https://bj.lianjia.com/chengjiao/c1111027382662/">30天成交1套</a>
      <span class="cutLine">|</span><a title="中绦胡同甲2号院租房" href="https://bj.lianjia.com/zufang/c1111027382662/">4套正在出租</a>
    </div>
    <div class="positionInfo">
      <span class="positionIcon"></span>
      <a href="https://bj.lianjia.com/xiaoqu/dongcheng/" class="district" title="东城小区">东城</a>
      &nbsp;<a href="https://bj.lianjia.com/xiaoqu/andingmen/" class="bizcircle" title="安定门小区">安定门</a>&nbsp;
              /板楼
                  /&nbsp;1985年建成
          </div>
        <div class="agentInfo">
      <span class="agentIcon"></span>
      <a href="https://dianpu.lianjia.com/1000000020239963" class="agentName">陈嘉贵</a>
      <div class="agent_chat im-talk LOGCLICKDATA" data-lj_evtid="12951" data-lj_action_event="WebClick" data-lj_action_pid="lianjiaweb" data-lj_action_resblock_id="1111027382662" data-lj_action_resblock_name="中绦胡同甲2号院" data-lj_action_agent_name="陈嘉贵" data-lj_action_agent_id="1000000020239963" data-lj_action_source_type="pc_xiaoqu_liebiao" data_lj_action_e_plan="{&quot;u&quot;:1000000020239963,&quot;v&quot;:&quot;V1&quot;,&quot;s&quot;:&quot;NATURAL&quot;,&quot;adId&quot;:100000131,&quot;flow&quot;:&quot;natural&quot;,&quot;b&quot;:&quot;DisplayTopAgentBuilder&quot;,&quot;p&quot;:&quot;&quot;,&quot;g&quot;:&quot;&quot;,&quot;sid&quot;:&quot;1000000020239963_1111027382662&quot;,&quot;rid&quot;:&quot;5014305824297679328&quot;}" data-ucid="1000000020239963" data-msg-payload="HI，您好。我正在看中绦胡同甲2号院小区" data-source-port="pc_lianjia_ershou_xiaoqu_liebiao">
        <i class="chatIcon"></i>
        <span>免费咨询</span>
      </div>
    </div>
        <div class="tagList">
                    <span>近地铁2号线鼓楼大街站</span>
          </div>
  </div>
  <div class="xiaoquListItemRight">
    <div class="xiaoquListItemPrice">
            <div class="totalPrice"><span>111687</span>元/m<sup>2</sup></div>
            <div class="priceDesc">
        3月二手房参考均价
      </div>
    </div>
        <div class="xiaoquListItemSellCount">
      <a title="中绦胡同甲2号院二手房" href="https://bj.lianjia.com/ershoufang/c1111027382662/" class="totalSellCount"><span>4</span>套</a>
      <div class="sellCountDesc">在售二手房</div>
    </div>
      </div>
</li>
</ul>
    '''
    doc = pq(html)
    li_items = doc('.listContent').items('li')
    for li in li_items:
        print(li('img').attr('alt'))
        print('----------------------------------------------------')


# fetch_community_page("andingmen")
fetch_community()
# test_py()