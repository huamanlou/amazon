# -*- coding: utf-8 -*-
import scrapy

# from pyquery import PyQuery as pq
from amazon.items import AmazonItem
from mysql_do import MysqlDo
from html_deal import HtmlDeal

#爬虫规则
class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    allowed_domians = ['amazon.com']
    base_url = 'http://www.amazon.com/dp/'
    # start_urls = ['https://www.amazon.com/dp/B00008DFOM']
    start_urls = []

    def __init__(self):
        #从db取出一个asin进行爬取
        mysql_do = MysqlDo()
        asin_rows = mysql_do.select_scrapy(1)
        for asin in asin_rows:
            init_url = self.base_url + asin[0]
            self.start_urls.append(init_url)


    def parse(self, response):
        item = AmazonItem()
        mysql_do = MysqlDo()
        html_deal = HtmlDeal(response)
        # asin
        #asin = selector.css('input[id="ASIN"]::attr(value)').extract_first()
        url = response.url
        asin = url[url.rfind('/')+1:len(url)]
        print asin
        res = html_deal.isbook()
        print res
        isbook = res['isbook']
        bsr = res['bsr']

        #假如是图书，索引表作标志，并且退出，不做数据处理
        if isbook==1:
            #更新索引表标志
            mysql_do.update_asin_isbook(asin)
            # 修改状态
            mysql_do.update_scrapy(asin)
            # 继续塞进程爬
            next_asins = mysql_do.select_scrapy(2)
            if next_asins == 0:
                return
            for asin in next_asins:
                product_url = self.base_url + asin[0]
                yield scrapy.Request(product_url, callback=self.parse)

            return

        #爬取相关产品，并插入数据库
        res = html_deal.get_products()
        print res
        customer_product_list = res['customer_product_list']
        sponsored_product_list = res['sponsored_product_list']
        if len(customer_product_list)>0:
            # 循环读取asin，查询数据库，若不存在，则插入数据库
            for asin_key in customer_product_list:
                row = mysql_do.select_asin(asin_key)
                if row < 1:
                    mysql_do.insert_asin(asin_key)

        if len(sponsored_product_list)>0:
            # 循环读取asin，查询数据库，若不存在，则插入数据库
            for asin_key in sponsored_product_list:
                row = mysql_do.select_asin(asin_key)
                if row < 1:
                    mysql_do.insert_asin(asin_key)


        item = html_deal.get_items()
        item['asin'] = asin
        # 分类销量排名
        item['bsr'] = bsr

        print item
        yield item
        #修改状态
        mysql_do.update_scrapy(asin)

        #继续塞进程爬
        next_asins = mysql_do.select_scrapy(2)
        if next_asins == 0:
            return
        for asin in next_asins:
            product_url = self.base_url + asin[0]
            print(product_url)
            yield scrapy.Request(product_url, callback=self.parse)

        #mysql_do.close_conn()
