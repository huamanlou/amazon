# -*- coding: utf-8 -*-
import MySQLdb
import scrapy
import time
import json
from amazon.items import AmazonItem



class MysqlDo:
    host = 'localhost'
    user = 'amazon'
    passwd = 'Amazon123!@#'
    db = 'amazon_us'
    charset = 'utf8'
    conn = ''
    def __init__(self):
        self.conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db, charset=self.charset)

    def close_conn(self):
        self.conn.close()

    def select_asin(self, asin):
        cursor = self.conn.cursor()
        cursor.execute("select * from t_asin where asin= '%s'" % (asin))
        row = cursor.fetchall()
        # self.conn.close()
        return len(row)

    def insert_asin(self, asin):
        cursor = self.conn.cursor()
        ctime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        sql = "insert into t_asin(asin,ctime, status) value ('%s', '%s', '%d')"
        try:
            cursor.execute(sql % (asin,ctime,1))
            self.conn.commit()
        except:

            self.conn.close()



class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    allowed_domians = ['amazon.com']
    base_url = 'http://www.amazon.com/dp/'
    start_urls = [
        'https://www.amazon.com/dp/B01G48RH20'
    ]

    def parse(self, response):
        selector = response.selector
        #页面抓取相关产品json数据包
        sim_feature = selector.css('div[id="purchase-sims-feature"]')
        products_data = sim_feature.css('div::attr(data-a-carousel-options)').extract_first()
        products_data = json.loads(products_data)
        # print(products_data)
        asin_list = products_data['ajax']['id_list']

        #循环读取asin，查询数据库，若不存在，则插入数据库
        mysql_do = MysqlDo()
        for asin in asin_list:
            row = mysql_do.select_asin(asin)
            if row<1:
                mysql_do.insert_asin(asin)
                #入库后，将新的asin，重新开启爬虫进程
                product_url = self.base_url + asin
                yield scrapy.Request(product_url, callback=self.parse)


        mysql_do.close_conn()

'''
class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    allowed_domians = ['amazon.com']
    start_urls = [
        'https://www.amazon.com/gp/product/B01BLQ24IW/'
        'https://www.amazon.com/dp/B01MEE4UYL/'
    ]

    def parse(self, response):
        item = AmazonItem()
        selector = response.selector

        #title = selector.xpath('// *[ @ id = "productTitle"]/text()').extract_first().strip()
        title = selector.css('span[id="productTitle"]::text').extract_first().strip()
        reviews = selector.css('span[id="acrCustomerReviewText"]::text').extract_first().strip()
        answers = selector.css('a[id="askATFLink"] .a-size-base::text').extract_first().strip()
        stars = selector.css('.a-declarative .a-icon-alt::text').extract_first().strip()
        price = selector.css('span[id="priceblock_saleprice"]::text').extract_first().strip()

        # print('+++++++++')
        # print(title)
        # print(reviews)
        # print(answers)
        # print(stars)
        # print(price)
        # print('===========')
        item['title'] = title
        item['reviews'] = reviews
        item['answers'] = answers
        item['stars'] = stars
        item['price'] = price

        yield item


class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    allowed_domians = ['amazon.com']
    base_url = 'http://www.amazon.com'
    load_page = 1
    start_urls = [
        'https://www.amazon.com/s/ref=nb_sb_noss_1?url=search-alias%3Daps&field-keywords=3d+pen'
    ]

    def parse(self, response):
        # with open('body', 'wb') as f:
        #     f.write(response.body)
        item = AmazonItem()
        selector = response.selector
        products = selector.css('.s-result-item')
        for pro in products:
            isPro = pro.css('.a-fixed-left-grid').extract()
            if (len(isPro)<1):
                continue

            title = pro.css('h2.s-access-title::attr(data-attribute)').extract_first()
            asin = pro.css('::attr(data-asin)').extract_first()
            att_id = pro.css('::attr(id)').extract_first()

            print('+'*10)
            print(att_id)
            print(title)
            print(asin)
            print('='*10)


        self.load_page = self.load_page + 1

        next_pages = selector.css('.pagnNext::attr(href)')

        if next_pages and self.load_page<3:
            page_url = self.base_url + next_pages[0].extract()
            print(page_url)
            yield scrapy.Request(page_url, callback=self.parse)

'''